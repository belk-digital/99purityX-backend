from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models.permission import Permission


class PermissionRepository:

    @staticmethod
    async def get_by_name(
        db: AsyncSession,
        name: str
    ) -> Permission | None:

        result = await db.execute(
            select(Permission).where(
                Permission.name == name
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession
    ) -> list[Permission]:

        result = await db.execute(
            select(Permission)
        )

        return result.scalars().all()