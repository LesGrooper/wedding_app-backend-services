from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_wo
from app.db.session import get_db
from app.schemas.schemas import (
    CheckInResult, GuestCreate, GuestListOut, GuestOut, EntitlementOut
)
from app.services.guest_service import GuestService

router = APIRouter(prefix="/guests", tags=["Guests"])


@router.post("", response_model=GuestOut, status_code=status.HTTP_201_CREATED)
def create_guest(
    data: GuestCreate,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_wo),
):
    service = GuestService(db)
    guest = service.create_guest(data)
    entitlements = service.repo.get_entitlements(guest.id)
    guest_out = GuestOut.model_validate(guest)
    guest_out.entitlements = [EntitlementOut.model_validate(e) for e in entitlements]
    return guest_out


@router.get("", response_model=list[GuestListOut])
def list_guests(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _: object = Depends(get_current_wo),
):
    service = GuestService(db)
    return service.list_guests(skip, limit)


@router.get("/search", response_model=list[GuestListOut])
def search_guests(
    name: str = Query(min_length=1),
    db: Session = Depends(get_db),
    _: object = Depends(get_current_wo),
):
    service = GuestService(db)
    return service.search_guests(name)


@router.get("/{guest_id}", response_model=GuestOut)
def get_guest(
    guest_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_wo),
):
    service = GuestService(db)
    result = service.get_guest_with_entitlements(guest_id)
    if not result:
        raise HTTPException(status_code=404, detail="Guest not found.")
    guest = result["guest"]
    guest_out = GuestOut.model_validate(guest)
    guest_out.entitlements = [EntitlementOut.model_validate(e) for e in result["entitlements"]]
    return guest_out


@router.post("/{guest_id}/checkin", response_model=CheckInResult)
def manual_checkin(
    guest_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_wo),
):
    service = GuestService(db)
    return service.checkin_manual(guest_id)
