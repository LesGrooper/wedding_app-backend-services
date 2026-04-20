from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_wo
from app.db.session import get_db
from app.schemas.schemas import CheckInResult
from app.services.guest_service import GuestService

router = APIRouter(prefix="/checkin", tags=["Check-in"])


@router.get("", response_model=CheckInResult)
def qr_checkin(
    code: str = Query(min_length=1, description="QR code string from guest invitation"),
    db: Session = Depends(get_db),
    _: object = Depends(get_current_wo),
):
    """
    Scan a guest's QR code to validate and check them in.

    Returns:
    - **OK** – check-in successful, includes name, category, entitlements
    - **ALREADY_USED** – guest already checked in
    - **INVALID** – QR code is tampered or unknown
    """
    service = GuestService(db)
    return service.checkin_by_qr(code)
