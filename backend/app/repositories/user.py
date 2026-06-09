from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.user import User
from app.core.exceptions import NotFoundException
import uuid


class UserRepository(BaseRepository):
    model = User

    async def get_by_email(self, email: str) -> User:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise NotFoundException("User")
        return user

    async def get_by_id(self, user_id: uuid.UUID | str) -> User:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise NotFoundException("User")
        return user

    async def update(self, user_id: uuid.UUID | str, data: dict) -> User:
        user = await self.get_by_id(user_id)
        for key, value in data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        return await self.save(user)