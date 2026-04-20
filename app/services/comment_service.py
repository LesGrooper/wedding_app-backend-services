from sqlalchemy.orm import Session

from app.db.models import Comment
from app.db.repositories import CommentRepository
from app.schemas.schemas import CommentCreate


class CommentService:
    def __init__(self, db: Session):
        self.repo = CommentRepository(db)
        self.db = db

    def add_comment(self, data: CommentCreate) -> Comment:
        comment = self.repo.create(
            name=data.name,
            message=data.message,
            guest_id=data.guest_id,
        )
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_comments(self, skip: int = 0, limit: int = 50) -> list[Comment]:
        return self.repo.list_latest(skip, limit)
