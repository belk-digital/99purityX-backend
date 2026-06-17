from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
)
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.session import (
    get_db,
)
from app.modules.auth.api.dependencies import (
    get_current_user,
)
from app.modules.auth.api.schemas import (
    GoogleLoginSchema,
    LoginSchema,
    VerifyEmailSchema,
    ResendOTPSchema,
    LogoutSchema,
    MeResponseSchema,
    RefreshTokenSchema,
    RegisterSchema,
    TokenResponseSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
)
from app.modules.auth.models.user import User
from app.modules.auth.models.role import Role
from app.modules.auth.services.auth_service import (
    AuthService,
)

from app.modules.auth.api.rbac import (
    require_permissions,
)

from app.modules.auth.constants.permissions import (
    MANAGE_USERS,
)
from app.modules.auth.services.rbac_service import (
    RBACService,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register")
async def register(
    payload: RegisterSchema,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        user = await service.register_user(
            payload
        )

        return {
            "message": "User registered successfully. Verification OTP sent to email.",
            "user_id": str(user.id),
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponseSchema,
)
async def login(
    request: Request,
    payload: LoginSchema,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        return await service.login_user(
            payload,
            request,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )
        
@router.post(
    "/google-login",
    response_model=TokenResponseSchema,
)
async def google_login(
    request: Request,
    payload: GoogleLoginSchema,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(
        db
    )

    try:
        return await service.google_login(
            payload.id_token,
            request,
        )

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )


@router.get(
    "/me",
    response_model=MeResponseSchema,
)
async def get_me(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    permissions = (
        await RBACService.get_user_permissions(
            db,
            current_user.id,
        )
    )

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role.name,
        "permissions": list(permissions),
    }

@router.post("/refresh")
async def refresh_token(
    request: Request,
    payload: RefreshTokenSchema,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        return await service.refresh_access_token(
            payload.refresh_token,
            request,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )

@router.post("/logout")
async def logout(
    request: Request,
    payload: LogoutSchema,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    return await service.logout(
        payload.refresh_token,
        request,
    )
    
@router.get("/admin-test")
async def admin_test(
    current_user=Depends(
        require_permissions(
            MANAGE_USERS
        )
    ),
):
    return {
        "message": "RBAC working"
    }


@router.get("/users")
async def list_users(
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permissions(MANAGE_USERS)),
):
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    users = result.scalars().all()

    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar()

    return {
        "users": [
            {
                "id": str(u.id),
                "email": u.email,
                "role": u.role.name if u.role else None,
                "is_active": u.is_active,
                "is_verified": u.is_verified,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "total": total,
    }


@router.put("/users/{user_id}/role")
async def change_user_role(
    user_id: UUID,
    role_name: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permissions(MANAGE_USERS)),
):
    user = (await db.execute(
        select(User).where(User.id == user_id)
    )).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = (await db.execute(
        select(Role).where(Role.name == role_name)
    )).scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=400, detail=f"Role '{role_name}' not found")

    user.role_id = role.id
    await db.commit()

    return {"message": f"User role changed to {role_name}"}
    
@router.post("/verify-email")
async def verify_email(
    payload: VerifyEmailSchema,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        return await service.verify_email(
            payload.email,
            payload.otp,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
        
@router.post("/resend-otp")
async def resend_otp(
    payload: ResendOTPSchema,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        return await service.resend_verification_otp(
            payload.email,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
        
@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordSchema,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        return await service.forgot_password(
            payload.email,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
        
@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordSchema,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        return await service.reset_password(
            payload.email,
            payload.otp,
            payload.new_password,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )