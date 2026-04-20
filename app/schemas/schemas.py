from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator
import bleach


# ──────────────────────────────────────────────
# Auth schemas
# ──────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ──────────────────────────────────────────────
# Guest schemas
# ──────────────────────────────────────────────

class GuestCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    category: str  # VIP | REGULAR
    invitation_type: str = "QR"  # QR | PHYSICAL

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        v = v.upper()
        if v not in ("VIP", "REGULAR"):
            raise ValueError("category must be VIP or REGULAR")
        return v

    @field_validator("invitation_type")
    @classmethod
    def validate_invitation_type(cls, v: str) -> str:
        v = v.upper()
        if v not in ("QR", "PHYSICAL"):
            raise ValueError("invitation_type must be QR or PHYSICAL")
        return v

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        return bleach.clean(v.strip())


class EntitlementOut(BaseModel):
    type: str
    qty: int

    class Config:
        from_attributes = True


class GuestOut(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    category: str
    invitation_type: str
    qr_code: str
    is_checked_in: bool
    checked_in_at: Optional[datetime]
    created_at: datetime
    entitlements: list[EntitlementOut] = []

    class Config:
        from_attributes = True


class GuestListOut(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    category: str
    invitation_type: str
    is_checked_in: bool
    created_at: datetime
    qr_code:str

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Check-in schemas
# ──────────────────────────────────────────────

class CheckInResult(BaseModel):
    status: str  # OK | ALREADY_USED | INVALID
    message: str
    guest_name: Optional[str] = None
    category: Optional[str] = None
    entitlements: list[EntitlementOut] = []


# ──────────────────────────────────────────────
# RSVP schemas
# ──────────────────────────────────────────────

class RSVPCreate(BaseModel):
    guest_id: int
    attendance: str  # YES | NO
    guest_count: int = 1

    @field_validator("attendance")
    @classmethod
    def validate_attendance(cls, v: str) -> str:
        v = v.upper()
        if v not in ("YES", "NO"):
            raise ValueError("attendance must be YES or NO")
        return v

    @field_validator("guest_count")
    @classmethod
    def validate_count(cls, v: int) -> int:
        if v < 1 or v > 20:
            raise ValueError("guest_count must be between 1 and 20")
        return v


class RSVPOut(BaseModel):
    id: int
    guest_id: int
    attendance: str
    guest_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class RSVPWithGuestOut(BaseModel):
    rsvp: RSVPOut
    guest: GuestListOut

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Comment schemas
# ──────────────────────────────────────────────

class CommentCreate(BaseModel):
    name: str
    message: str
    guest_id: Optional[int] = None

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        return bleach.clean(v.strip())[:150]

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        return bleach.clean(v.strip())[:1000]


class CommentOut(BaseModel):
    id: int
    guest_id: Optional[int]
    name: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Generic response
# ──────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
