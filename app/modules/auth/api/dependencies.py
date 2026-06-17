from fastapi import (
    Depends,
    HTTPException,
)

from fastapi.security import (
    OAuth2PasswordBearer,
)

from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy.orm import (
    selectinload,
)

from app.infrastructure.database.session import (
    get_db,
)

from app.modules.auth.models.user import User

from app.modules.auth.services.jwt_service import (
    JWTService,
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


async def get_current_user(
    token: str = Depends(
        oauth2_scheme
    ),
    db: AsyncSession = Depends(get_db),
):

    payload = JWTService.decode_token(
        token
    )

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user_id = payload.get("sub")

    result = await db.execute(
        select(User)
        .options(
            selectinload(User.role),

            # IMPORTANT
            selectinload(User.patient),

            # IMPORTANT
            selectinload(
                User.provider_profile
            ),
        )
        .where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user