from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models.session import (
    UserSession,
)
from app.modules.auth.models.user import User
from app.modules.auth.models.user_profile import (
    UserProfile,
)


class AuthRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_user_by_email(
        self,
        email: str,
    ):
        result = await self.db.execute(
            select(User).where(
                User.email == email
            )
        )

        return result.scalar_one_or_none()

    async def create_user(
        self,
        user: User,
    ):
        self.db.add(user)

        await self.db.commit()

        await self.db.refresh(user)

        return user

    async def create_profile(
        self,
        profile: UserProfile,
    ):
        self.db.add(profile)

        await self.db.commit()

        await self.db.refresh(profile)

        return profile

    async def create_session(
        self,
        session: UserSession,
    ):
        self.db.add(session)

        await self.db.commit()

        await self.db.refresh(session)

        return session

    async def get_session_by_token(
        self,
        refresh_token_hash: str,
    ):
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.refresh_token_hash
                == refresh_token_hash
            )
        )

        return result.scalar_one_or_none()

    async def delete_session(
        self,
        refresh_token_hash: str,
    ):
        await self.db.execute(
            delete(UserSession).where(
                UserSession.refresh_token_hash
                == refresh_token_hash
            )
        )

        await self.db.commit()
        
    async def get_user_by_google_id(
        self,
        google_id: str,
    ):
        result = await self.db.execute(
            select(User).where(
                User.google_id == google_id
            )
        )

        return result.scalar_one_or_none()