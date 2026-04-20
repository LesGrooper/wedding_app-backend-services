from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.models import Guest, GuestEntitlement


class GuestRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, phone: Optional[str], category: str,
                invitation_type: str, qr_code: str) -> Guest:
        guest = Guest(
            name=name,
            phone=phone,
            category=category,
            invitation_type=invitation_type,
            qr_code=qr_code,
        )
        self.db.add(guest)
        self.db.flush()  # get id without committing
        return guest

    def get_by_id(self, guest_id: int) -> Optional[Guest]:
        return self.db.get(Guest, guest_id)

    def get_by_qr_code(self, qr_code: str) -> Optional[Guest]:
        return self.db.query(Guest).filter(Guest.qr_code == qr_code).first()

    def search_by_name(self, name: str) -> list[Guest]:
        pattern = f"%{name}%"
        return self.db.query(Guest).filter(Guest.name.ilike(pattern)).limit(20).all()

    def mark_checked_in(self, guest: Guest) -> Guest:
        guest.is_checked_in = True
        guest.checked_in_at = datetime.now(timezone.utc)
        self.db.flush()
        return guest

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Guest]:
        return self.db.query(Guest).offset(skip).limit(limit).all()

    def get_entitlements(self, guest_id: int) -> list[GuestEntitlement]:
        return (
            self.db.query(GuestEntitlement)
            .filter(GuestEntitlement.guest_id == guest_id)
            .all()
        )

    def add_entitlement(self, guest_id: int, type_: str, qty: int = 1) -> GuestEntitlement:
        ent = GuestEntitlement(guest_id=guest_id, type=type_, qty=qty)
        self.db.add(ent)
        return ent
