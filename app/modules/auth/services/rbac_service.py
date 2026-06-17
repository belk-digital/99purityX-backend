from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models.user import User
from app.modules.auth.models.role import Role
from app.modules.auth.models.role_permission import (
    RolePermission,
)


class RBACService:

    @staticmethod
    async def get_user_permissions(
        db: AsyncSession,
        user_id,
    ) -> set[str]:

        result = await db.execute(
            select(User)
            .options(
                selectinload(User.role)
                .selectinload(Role.role_permissions)
                .selectinload(
                    RolePermission.permission
                )
            )
            .where(User.id == user_id)
        )

        user = result.scalar_one_or_none()

        if not user or not user.role:
            return set()

        permissions = {
            rp.permission.name
            for rp in user.role.role_permissions
        }

        return permissions