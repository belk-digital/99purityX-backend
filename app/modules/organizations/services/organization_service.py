from re import sub
from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.enums.audit_enums import (
    AuditAction,
    AuditResource,
)
from app.modules.audit.schemas.audit_schema import (
    AuditLogCreate,
)
from app.modules.audit.services.audit_service import (
    AuditService,
)
from app.modules.organizations.models.organization import (
    Organization,
)
from app.modules.organizations.repositories.organization_repository import (
    OrganizationRepository,
)
from app.modules.organizations.schemas.organization_schema import (
    OrganizationCreateSchema,
    OrganizationUpdateSchema,
)


class OrganizationService:

    @staticmethod
    def _generate_slug(
        name: str,
    ) -> str:
        """
        Generate a URL-friendly slug.
        """

        slug = name.lower().strip()

        slug = sub(
            r"[^a-z0-9]+",
            "-",
            slug,
        )

        return slug.strip("-")

    @staticmethod
    async def create_organization(
        db: AsyncSession,
        data: OrganizationCreateSchema,
        actor_user_id: UUID,
    ) -> Organization:

        repository = OrganizationRepository(db)

        # CHECK DUPLICATE NAME
        existing_name = await repository.get_by_name(
            data.name,
        )

        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization with this name already exists.",
            )

        slug = OrganizationService._generate_slug(
            data.name,
        )

        original_slug = slug
        counter = 1

        while await repository.get_by_slug(slug):
            slug = f"{original_slug}-{counter}"
            counter += 1

        organization = Organization(
            name=data.name,
            slug=slug,
            organization_type=data.organization_type,
            email=data.email,
            phone=data.phone,
            website=data.website,
            timezone=data.timezone,
            logo_url=data.logo_url,
            primary_color=data.primary_color,
            secondary_color=data.secondary_color,
            description=data.description,
            tax_id=data.tax_id,
            is_active=data.is_active,
        )

        organization = await repository.create(
            organization,
        )

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.CREATE,
                resource=AuditResource.ORGANIZATION,
                resource_id=str(organization.id),
                description="Organization created",
                audit_metadata={
                    "organization_name": organization.name,
                    "organization_type": organization.organization_type.value,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            organization,
        )

        return organization

    @staticmethod
    async def get_organization(
        db: AsyncSession,
        organization_id: UUID,
    ) -> Organization:

        repository = OrganizationRepository(db)

        organization = await repository.get_by_id(
            organization_id,
        )

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        return organization

    @staticmethod
    async def update_organization(
        db: AsyncSession,
        organization: Organization,
        data: OrganizationUpdateSchema,
        actor_user_id: UUID,
    ) -> Organization:

        repository = OrganizationRepository(db)

        update_data = data.model_dump(
            exclude_unset=True,
        )

        # HANDLE NAME CHANGE
        if (
            "name" in update_data
            and update_data["name"] != organization.name
        ):

            existing = await repository.get_by_name(
                update_data["name"],
            )

            if (
                existing
                and existing.id != organization.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization with this name already exists.",
                )

            slug = OrganizationService._generate_slug(
                update_data["name"],
            )

            original_slug = slug
            counter = 1

            while True:

                existing_slug = await repository.get_by_slug(
                    slug,
                )

                if (
                    existing_slug is None
                    or existing_slug.id == organization.id
                ):
                    break

                slug = f"{original_slug}-{counter}"

                counter += 1

            organization.slug = slug

        for field, value in update_data.items():

            setattr(
                organization,
                field,
                value,
            )

        await db.flush()

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.UPDATE,
                resource=AuditResource.ORGANIZATION,
                resource_id=str(organization.id),
                description="Organization updated",
                audit_metadata={
                    "organization_name": organization.name,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            organization,
        )

        return organization

    @staticmethod
    async def delete_organization(
        db: AsyncSession,
        organization: Organization,
        actor_user_id: UUID,
    ) -> None:

        repository = OrganizationRepository(db)

        await repository.delete(
            organization,
        )

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.DELETE,
                resource=AuditResource.ORGANIZATION,
                resource_id=str(organization.id),
                description="Organization deleted",
                audit_metadata={
                    "organization_name": organization.name,
                },
            ),
        )

        await db.commit()