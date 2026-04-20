import hmac
import hashlib
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ──────────────────────────────────────────────
# Password utilities
# ──────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ──────────────────────────────────────────────
# JWT utilities
# ──────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None


# ──────────────────────────────────────────────
# QR Code signing
# ──────────────────────────────────────────────

def generate_qr_signature(guest_id: int) -> str:
    """HMAC-SHA256 signature for a guest_id."""
    msg = str(guest_id).encode()
    secret = settings.qr_hmac_secret.encode()
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()


def build_qr_code(guest_id: int) -> str:
    """Returns '{guest_id}:{signature}'."""
    sig = generate_qr_signature(guest_id)
    return f"{guest_id}:{sig}"


def verify_qr_code(code: str) -> int | None:
    """
    Validate a QR code string.
    Returns guest_id if valid, None otherwise.
    """
    try:
        raw_id, sig = code.split(":", 1)
        guest_id = int(raw_id)
    except (ValueError, AttributeError):
        return None

    expected = generate_qr_signature(guest_id)
    if hmac.compare_digest(expected, sig):
        return guest_id
    return None
