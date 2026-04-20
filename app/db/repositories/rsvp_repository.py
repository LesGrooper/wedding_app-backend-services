from sqlalchemy.orm import Session

from app.db.models import RSVP


class RSVPRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, guest_id: int, attendance: str, guest_count: int) -> RSVP:
        rsvp = RSVP(guest_id=guest_id, attendance=attendance, guest_count=guest_count)
        self.db.add(rsvp)
        self.db.flush()
        return rsvp

    def get_by_guest_id(self, guest_id: int) -> RSVP | None:
        return self.db.query(RSVP).filter(RSVP.guest_id == guest_id).first()
