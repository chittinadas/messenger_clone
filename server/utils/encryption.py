from Crypto.Cipher import AES
import base64

def encrypt_message(key, text):
    cipher = AES.new(key.encode(), AES.MODE_EAX)
    nonce = cipher.nonce
    ct, tag = cipher.encrypt_and_digest(text.encode())
    return base64.b64encode(nonce + ct).decode()

def decrypt_message(key, enc):
    data = base64.b64decode(enc)
    nonce, ct = data[:16], data[16:]
    cipher = AES.new(key.encode(), AES.MODE_EAX, nonce)
    return cipher.decrypt(ct).decode()
