from fastapi import (
    HTTPException,
    status,
)

from app.modules.auth.models.user import User


def validate_admin_access(
    current_user: User,
) -> None:
    """
    Platform-level authorization.

    Only platform administrators can perform
    organization management operations.

    This dependency will evolve into tenant-aware
    authorization once Organization Membership
    RBAC is introduced.
    """

    if current_user.role.name.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action.",
        )