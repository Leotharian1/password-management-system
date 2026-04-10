import json
import os
import random
import string
import base64
from typing import Optional

import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from constants import DB_FILE, KEY_FILE, SYMBOLS

def load_db() -> dict:
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"users": {}, "vaults": {}}, f, indent=2)
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data: dict):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_kdf_salt() -> bytes:
    with open(KEY_FILE, "rb") as f:
        return f.read()

def derive_fernet_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_text(key: bytes, plaintext: str) -> str:
    f = Fernet(key)
    return f.encrypt(plaintext.encode()).decode()

def decrypt_text(key: bytes, token: str) -> str:
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()

def generate_password(length=12) -> str:
    length = max(8, min(16, length))
    categories = [string.ascii_lowercase, string.ascii_uppercase, string.digits, SYMBOLS]
    pw = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice(SYMBOLS),
    ]
    while len(pw) < length:
        pw.append(random.choice(random.choice(categories)))
    random.shuffle(pw)
    return "".join(pw)

def password_strength(pw: str) -> str:
    score = 0
    if any(c.islower() for c in pw):
        score += 1
    if any(c.isupper() for c in pw):
        score += 1
    if any(c.isdigit() for c in pw):
        score += 1
    if any(c in SYMBOLS for c in pw):
        score += 1
    if len(pw) >= 12:
        score += 1
    if score <= 2:
        return "Poor"
    if score == 3:
        return "Weak"
    if score == 4:
        return "Good"
    return "Strong"

def encrypt_safe(username: str, plaintext: str) -> str:
    data = load_db()
    user = data["users"][username]
    pw_hash = user["pw_hash"]
    salt = get_kdf_salt()
    key = derive_fernet_key(pw_hash, salt)
    return encrypt_text(key, plaintext)

def decrypt_safe(username: str, token: str) -> str:
    data = load_db()
    user = data["users"][username]
    pw_hash = user["pw_hash"]
    salt = get_kdf_salt()
    key = derive_fernet_key(pw_hash, salt)
    try:
        return decrypt_text(key, token)
    except Exception:
        return "<decryption failed>"

def create_user(username: str, email: str, password: str) -> None:
    data = load_db()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    data["users"][username] = {"email": email, "pw_hash": hashed.decode()}
    data["vaults"][username] = []
    save_db(data)

def verify_user(username: str, password: str) -> bool:
    data = load_db()
    user = data["users"].get(username)
    if not user:
        return False
    stored_hash = user["pw_hash"].encode()
    return bcrypt.checkpw(password.encode(), stored_hash)
