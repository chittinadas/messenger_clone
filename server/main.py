from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json, os
from utils.encryption import encrypt_message, decrypt_message

app = FastAPI()

# CORS setup for client access
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# WebSocket connections store
active_connections = {}

# Ensure data files exist
for file in ["users.json", "friends.json", "messages.json"]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)

# 🔹 User Registration
@app.post("/register")
async def register(user: dict):
    with open("users.json", "r+") as f:
        users = json.load(f)
        users.append(user)
        f.seek(0)
        json.dump(users, f)
    return {"status": "registered"}

# 🔹 User Login
@app.post("/login")
async def login(credentials: dict):
    with open("users.json", "r") as f:
        users = json.load(f)
    for u in users:
        if u["username"] == credentials["username"] and u["password"] == credentials["password"]:
            return {"status": "success"}
    return {"status": "failed"}

# 🔹 Add Friend
@app.post("/add_friend")
async def add_friend(data: dict):
    with open("friends.json", "r+") as f:
        friends = json.load(f)
        friends.append({"user": data["user"], "friend": data["friend"]})
        f.seek(0)
        json.dump(friends, f)
    return {"status": "added"}

# 🔹 Remove Friend
@app.post("/remove_friend")
async def remove_friend(data: dict):
    with open("friends.json", "r+") as f:
        friends = json.load(f)
        friends = [f for f in friends if not (f["user"] == data["user"] and f["friend"] == data["friend"])]
        f.seek(0)
        f.truncate()
        json.dump(friends, f)
    return {"status": "removed"}

# 🔹 WebSocket Chat
@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    active_connections[username] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            with open("messages.json", "r+") as f:
                messages = json.load(f)
                messages.append({"from": username, "message": data})
                f.seek(0)
                json.dump(messages, f)

            # Forward to all friends
            with open("friends.json", "r") as fr:
                friends = json.load(fr)
                user_friends = [f["friend"] for f in friends if f["user"] == username]
                for friend in user_friends:
                    if friend in active_connections:
                        await active_connections[friend].send_text(f"{username}: {data}")
    except WebSocketDisconnect:
        del active_connections[username]

# 🔹 Media Upload
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    path = f"media/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())
    return {"status": "uploaded", "filename": file.filename}
