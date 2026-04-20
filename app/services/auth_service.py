from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_access_token, verify_password
from app.db.models import User
from app.db.repositories import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def login(self, username: str, password: str) -> Optional[str]:
        """Returns JWT token on success, None on failure."""
        user = self.repo.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            return None
        token = create_access_token({"sub": user.username, "role": user.role})
        return token

    def get_current_user(self, token: str) -> Optional[User]:
        payload = decode_access_token(token)
        if not payload:
            return None
        username = payload.get("sub")
        if not username:
            return None
        return self.repo.get_by_username(username)
