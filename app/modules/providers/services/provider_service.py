from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.auth.models.user import User
from sqlalchemy.orm import selectinload

from app.modules.audit.services.audit_service import (
    AuditService,
)
from app.modules.providers.models.provider_model import (
    Provider,
)
from app.modules.providers.repositories.provider_repository import (
    ProviderRepository,
)
from app.modules.providers.schemas.provider_schema import (
    ProviderCreateSchema,
    ProviderUpdateSchema,
)
from app.modules.audit.schemas.audit_schema import (
    AuditLogCreate,
)


class ProviderService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.provider_repository = (
            ProviderRepository(db)
        )

    async def get_my_provider_profile(
        self,
        user_id: UUID,
    ) -> Provider:

        provider = await (
            self.provider_repository.get_by_user_id(
                user_id
            )
        )

        if not provider:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider profile not found",
            )

        return provider

    async def get_provider_by_id(
        self,
        provider_id: UUID,
    ) -> Provider:

        provider = await (
            self.provider_repository.get_by_id(
                provider_id
            )
        )

        if not provider:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found",
            )

        return provider

    async def get_all_providers(
        self,
    ) -> list[Provider]:

        return await (
            self.provider_repository.get_all()
        )

    async def update_my_provider_profile(
        self,
        user_id: UUID,
        payload: ProviderUpdateSchema,
    ) -> Provider:

        provider = await (
            self.provider_repository.get_by_user_id(
                user_id
            )
        )

        if not provider:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider profile not found",
            )

        update_data = payload.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():

            setattr(
                provider,
                field,
                value,
            )

        provider = await (
            self.provider_repository.update(
                provider
            )
        )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=user_id,
            payload=AuditLogCreate(
                action="provider.profile.updated",
                resource="provider",
                resource_id=str(provider.id),
                description="Provider profile updated",
            ),
        )

        await self.db.commit()

        return provider
    
    async def create_provider(
        self,
        payload: ProviderCreateSchema,
        actor_user_id,
    ) -> Provider:

        user_result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(
                User.id == payload.user_id
            )
        )

        user = user_result.scalar_one_or_none()

        if not user:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        allowed_roles = [
            "DOCTOR",
            "NUTRITIONIST",
            "CARE_COORDINATOR",
        ]

        if user.role.name not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User role cannot become provider",
            )

        existing_provider = await (
            self.provider_repository.get_by_user_id(
                payload.user_id
            )
        )

        if existing_provider:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider profile already exists",
            )

        provider = Provider(
            user_id=payload.user_id,
            provider_type=payload.provider_type,
            speciality=payload.speciality,
            license_number=payload.license_number,
            years_experience=payload.years_experience,
            bio=payload.bio,
            consultation_fee=payload.consultation_fee,
        )

        provider = await (
            self.provider_repository.create(
                provider
            )
        )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action="provider.created",
                resource="provider",
                resource_id=str(provider.id),
                description="Provider profile created",
            ),
        )

        await self.db.commit()

        return provider