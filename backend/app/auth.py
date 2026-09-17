import base64, hashlib, hmac, os, time
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from .db import db_session, User

SECRET = os.getenv("SESSION_SECRET", "")
if os.getenv("APP_ENV", "development") == "production" and len(SECRET) < 32:
    raise RuntimeError("SESSION_SECRET must be at least 32 characters in production")
if not SECRET: SECRET = "development-only-change-me"

def hash_password(password: str) -> str:
    salt = os.urandom(16); digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return base64.urlsafe_b64encode(salt + digest).decode()

def verify_password(password: str, stored: str) -> bool:
    try:
        raw = base64.urlsafe_b64decode(stored.encode()); salt, expected = raw[:16], raw[16:]
        actual = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual, expected)
    except Exception: return False

def make_token(user_id: int) -> str:
    payload = f"{user_id}:{int(time.time())}"; sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}:{sig}".encode()).decode()

def current_user(authorization: str = Header(default=""), db: Session = Depends(db_session)) -> User:
    if not authorization.startswith("Bearer "): raise HTTPException(401, "Authentication required")
    try:
        raw = base64.urlsafe_b64decode(authorization[7:].encode()).decode().split(":"); user_id, issued, sig = int(raw[0]), raw[1], raw[2]
        payload = f"{user_id}:{issued}"; expected = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected) or time.time() - int(issued) > 86400 * 7: raise ValueError
    except Exception: raise HTTPException(401, "Invalid or expired session")
    user = db.get(User, user_id)
    if not user: raise HTTPException(401, "Invalid session")
    return user
