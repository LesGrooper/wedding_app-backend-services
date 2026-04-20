from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def create(self, username: str, password_hash: str, role: str = "WO") -> User:
        user = User(username=username, password_hash=password_hash, role=role)
        self.db.add(user)
        self.db.flush()
        return user
