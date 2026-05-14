import base64
import os
import secrets
from hashlib import sha256

from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import settings

security = HTTPBasic()


def _normalize_key(raw_key: str) -> bytes:
    if not raw_key:
        digest = sha256("smartbox-default-fernet".encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)
    try:
        base64.urlsafe_b64decode(raw_key)
        return raw_key.encode("utf-8")
    except Exception:
        digest = sha256(raw_key.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)


FERNET = Fernet(_normalize_key(settings.fernet_key or os.getenv("SMARTBOX_FERNET_KEY", "")))


def encrypt_secret(value: str | None) -> str | None:
    if not value:
        return None
    return FERNET.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return FERNET.decrypt(value.encode("utf-8")).decode("utf-8")
    except Exception:
        return None


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    user_ok = secrets.compare_digest(credentials.username, settings.admin_username)
    pass_ok = secrets.compare_digest(credentials.password, settings.admin_password)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
