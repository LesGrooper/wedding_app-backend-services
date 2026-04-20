from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import RSVPCreate, RSVPWithGuestOut
from app.services.rsvp_service import RSVPService

router = APIRouter(prefix="/rsvp", tags=["RSVP"])


@router.post("", response_model=RSVPWithGuestOut, status_code=status.HTTP_201_CREATED)
def submit_rsvp(data: RSVPCreate, db: Session = Depends(get_db)):
    """
    Submit RSVP for a guest. No authentication required (public endpoint).
    Returns RSVP data along with related guest information.
    """
    service = RSVPService(db)
    return service.submit_rsvp(data)
