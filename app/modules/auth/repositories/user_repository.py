from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models.user import User


class UserRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:

        query = (
            select(User)
            .where(
                User.id == user_id
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:

        query = (
            select(User)
            .where(
                User.email == email
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_all(
        self,
    ) -> list[User]:

        query = (
            select(User)
            .order_by(
                User.email.asc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def update(
        self,
        user: User,
    ) -> User:

        await self.db.flush()

        await self.db.refresh(user)

        return user

    async def delete(
        self,
        user: User,
    ) -> None:

        await self.db.delete(user)

        await self.db.flush()