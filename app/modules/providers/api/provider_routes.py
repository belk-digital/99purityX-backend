from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db
from app.modules.auth.api.dependencies import (
    get_current_user,
)
from app.modules.auth.api.rbac import (
    require_permissions,
)
from app.modules.auth.models.user import User
from app.modules.providers.schemas.provider_schema import (
    ProviderCreateSchema,
    ProviderListResponseSchema,
    ProviderResponseSchema,
    ProviderUpdateSchema,
)
from app.modules.providers.services.provider_service import (
    ProviderService,
)

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get(
    "/me",
    response_model=ProviderResponseSchema,
)
async def get_my_provider_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProviderService(db)

    return await service.get_my_provider_profile(
        current_user.id,
    )


@router.post(
    "",
    response_model=ProviderResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_provider(
    payload: ProviderCreateSchema,
    current_user: User = Depends(
        require_permissions(
            "manage_providers"
        )
    ),
    db: AsyncSession = Depends(get_db),
):

    service = ProviderService(db)

    return await service.create_provider(
        payload=payload,
        actor_user_id=current_user.id,
    )

@router.put(
    "/me",
    response_model=ProviderResponseSchema,
)
async def update_my_provider_profile(
    payload: ProviderUpdateSchema,
    current_user: User = Depends(
        require_permissions("manage_provider_profile")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProviderService(db)

    return await service.update_my_provider_profile(
        current_user.id,
        payload,
    )


@router.get(
    "",
    response_model=list[ProviderListResponseSchema],
)
async def get_all_providers(
    db: AsyncSession = Depends(get_db),
):
    service = ProviderService(db)

    return await service.get_all_providers()


@router.get(
    "/{provider_id}",
    response_model=ProviderResponseSchema,
)
async def get_provider_by_id(
    provider_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ProviderService(db)

    return await service.get_provider_by_id(provider_id)