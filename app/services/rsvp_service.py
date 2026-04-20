from sqlalchemy.orm import Session

from app.db.models import RSVP, Guest
from app.db.repositories import RSVPRepository, GuestRepository
from app.schemas.schemas import RSVPCreate, RSVPWithGuestOut


class RSVPService:
    def __init__(self, db: Session):
        self.repo = RSVPRepository(db)
        self.guest_repo = GuestRepository(db)
        self.db = db

    def submit_rsvp(self, data: RSVPCreate) -> RSVPWithGuestOut:
        rsvp = self.repo.create(
            guest_id=data.guest_id,
            attendance=data.attendance,
            guest_count=data.guest_count,
        )
        self.db.commit()
        self.db.refresh(rsvp)
        
        # Fetch guest data
        guest = self.guest_repo.get_by_id(data.guest_id)
        
        return RSVPWithGuestOut(
            rsvp=rsvp,
            guest=guest
        )
