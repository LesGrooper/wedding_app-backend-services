from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import build_qr_code, verify_qr_code
from app.db.models import Guest
from app.db.repositories import GuestRepository
from app.schemas.schemas import CheckInResult, EntitlementOut, GuestCreate


ENTITLEMENTS_BY_CATEGORY = {
    "VIP": ["FOOD", "SOUVENIR"],
    "REGULAR": ["SOUVENIR"],
}


class GuestService:
    def __init__(self, db: Session):
        self.repo = GuestRepository(db)
        self.db = db

    def create_guest(self, data: GuestCreate) -> Guest:
        # Temporary QR placeholder — we need the ID first
        guest = self.repo.create(
            name=data.name,
            phone=data.phone,
            category=data.category,
            invitation_type=data.invitation_type,
            qr_code="__pending__",
        )

        # Generate QR with real guest_id
        qr_code = build_qr_code(guest.id)
        guest.qr_code = qr_code

        # Assign entitlements
        for ent_type in ENTITLEMENTS_BY_CATEGORY.get(data.category, []):
            self.repo.add_entitlement(guest.id, ent_type)

        self.db.commit()
        self.db.refresh(guest)
        return guest

    def get_guest_with_entitlements(self, guest_id: int) -> Optional[dict]:
        guest = self.repo.get_by_id(guest_id)
        if not guest:
            return None
        entitlements = self.repo.get_entitlements(guest_id)
        return {"guest": guest, "entitlements": entitlements}

    def search_guests(self, name: str) -> list[Guest]:
        return self.repo.search_by_name(name)

    def list_guests(self, skip: int = 0, limit: int = 100) -> list[Guest]:
        return self.repo.list_all(skip, limit)

    def checkin_by_qr(self, code: str) -> CheckInResult:
        guest_id = verify_qr_code(code)
        if guest_id is None:
            return CheckInResult(status="INVALID", message="QR code is not valid.")

        guest = self.repo.get_by_id(guest_id)
        if not guest:
            return CheckInResult(status="INVALID", message="Guest not found.")

        if guest.is_checked_in:
            return CheckInResult(
                status="ALREADY_USED",
                message=f"This QR was already used at {guest.checked_in_at}.",
                guest_name=guest.name,
                category=guest.category,
            )

        self.repo.mark_checked_in(guest)
        self.db.commit()

        entitlements = self.repo.get_entitlements(guest.id)
        ent_out = [EntitlementOut(type=e.type, qty=e.qty) for e in entitlements]

        return CheckInResult(
            status="OK",
            message="Check-in successful.",
            guest_name=guest.name,
            category=guest.category,
            entitlements=ent_out,
        )

    def checkin_manual(self, guest_id: int) -> CheckInResult:
        guest = self.repo.get_by_id(guest_id)
        if not guest:
            return CheckInResult(status="INVALID", message="Guest not found.")

        if guest.is_checked_in:
            return CheckInResult(
                status="ALREADY_USED",
                message=f"Guest already checked in at {guest.checked_in_at}.",
                guest_name=guest.name,
                category=guest.category,
            )

        self.repo.mark_checked_in(guest)
        self.db.commit()

        entitlements = self.repo.get_entitlements(guest.id)
        ent_out = [EntitlementOut(type=e.type, qty=e.qty) for e in entitlements]

        return CheckInResult(
            status="OK",
            message="Manual check-in successful.",
            guest_name=guest.name,
            category=guest.category,
            entitlements=ent_out,
        )
