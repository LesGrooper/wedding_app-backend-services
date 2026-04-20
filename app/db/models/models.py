from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Enum, Index, Integer,
    String, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Guest(Base):
    __tablename__ = "guests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    category: Mapped[str] = mapped_column(Enum("VIP", "REGULAR"), nullable=False)
    invitation_type: Mapped[str] = mapped_column(Enum("QR", "PHYSICAL"), nullable=False, default="QR")
    qr_code: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    is_checked_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    checked_in_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_guests_qr_code", "qr_code"),
        Index("idx_guests_name", "name"),
        Index("idx_guests_category", "category"),
    )


class GuestEntitlement(Base):
    __tablename__ = "guest_entitlements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guest_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    type: Mapped[str] = mapped_column(Enum("FOOD", "SOUVENIR"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    __table_args__ = (Index("idx_entitlements_guest_id", "guest_id"),)


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guest_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (Index("idx_comments_created_at", "created_at"),)


class RSVP(Base):
    __tablename__ = "rsvp"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guest_id: Mapped[int] = mapped_column(Integer, nullable=False)
    attendance: Mapped[str] = mapped_column(Enum("YES", "NO"), nullable=False)
    guest_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (Index("idx_rsvp_guest_id", "guest_id"),)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="WO", nullable=False)

    __table_args__ = (Index("idx_users_username", "username"),)
