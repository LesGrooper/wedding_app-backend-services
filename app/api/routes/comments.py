from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import CommentCreate, CommentOut
from app.services.comment_service import CommentService

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def post_comment(data: CommentCreate, db: Session = Depends(get_db)):
    """Submit a comment/wish. No authentication required (public endpoint)."""
    service = CommentService(db)
    return service.add_comment(data)


@router.get("", response_model=list[CommentOut])
def get_comments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db),
):
    """Get latest comments/wishes. No authentication required (public endpoint)."""
    service = CommentService(db)
    return service.get_comments(skip, limit)
