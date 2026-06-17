from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db
from app.modules.auth.api.dependencies import (
    get_current_user,
)
from app.modules.auth.services.rbac_service import RBACService
from app.modules.auth.models.user import User


def require_roles(*allowed_roles: str):

    async def dependency(
        current_user: User = Depends(get_current_user)
    ):

        if current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions"
            )

        return current_user

    return dependency


def require_permissions(*required_permissions: str):

    async def dependency(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):

        user_permissions = await RBACService.get_user_permissions(
            db=db,
            user_id=current_user.id
        )

        missing_permissions = [
            permission
            for permission in required_permissions
            if permission not in user_permissions
        ]

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return current_user

    return dependency