from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import Comment


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, message: str, guest_id: Optional[int] = None) -> Comment:
        comment = Comment(guest_id=guest_id, name=name, message=message)
        self.db.add(comment)
        self.db.flush()
        return comment

    def list_latest(self, skip: int = 0, limit: int = 50) -> list[Comment]:
        return (
            self.db.query(Comment)
            .order_by(Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
