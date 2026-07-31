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

from app.modules.sales.models.sales_organization import (
    SalesOrganization,
)
from app.modules.sales.repositories.sales_organization_repository import (
    SalesOrganizationRepository,
)
from app.modules.sales.schemas.sales_organization_schema import (
    SalesOrganizationCreateSchema,
    SalesOrganizationUpdateSchema,
)


class SalesOrganizationService:

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
    async def create_sales_organization(
        db: AsyncSession,
        data: SalesOrganizationCreateSchema,
        actor_user_id: UUID,
    ) -> SalesOrganization:

        repository = SalesOrganizationRepository(db)

        existing_name = await repository.get_by_name(
            data.name,
        )

        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sales Organization with this name already exists.",
            )

        slug = SalesOrganizationService._generate_slug(
            data.name,
        )

        original_slug = slug
        counter = 1

        while await repository.get_by_slug(slug):
            slug = f"{original_slug}-{counter}"
            counter += 1

        sales_organization = SalesOrganization(
            name=data.name,
            slug=slug,
            email=data.email,
            phone=data.phone,
            website=data.website,
            country=data.country,
            timezone=data.timezone,
            logo_url=data.logo_url,
            primary_color=data.primary_color,
            secondary_color=data.secondary_color,
            description=data.description,
            is_active=data.is_active,
        )

        sales_organization = await repository.create(
            sales_organization,
        )

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.CREATE,
                resource=AuditResource.SALES_ORGANIZATION,
                resource_id=str(sales_organization.id),
                description="Sales Organization created",
                audit_metadata={
                    "sales_organization_name": sales_organization.name,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            sales_organization,
        )

        return sales_organization

    @staticmethod
    async def get_sales_organization(
        db: AsyncSession,
        sales_organization_id: UUID,
    ) -> SalesOrganization:

        repository = SalesOrganizationRepository(db)

        sales_organization = await repository.get_by_id(
            sales_organization_id,
        )

        if not sales_organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales Organization not found.",
            )

        return sales_organization

    @staticmethod
    async def get_all_sales_organizations(
        db: AsyncSession,
    ) -> list[SalesOrganization]:

        repository = SalesOrganizationRepository(db)

        return await repository.get_all()

    @staticmethod
    async def update_sales_organization(
        db: AsyncSession,
        sales_organization: SalesOrganization,
        data: SalesOrganizationUpdateSchema,
        actor_user_id: UUID,
    ) -> SalesOrganization:

        repository = SalesOrganizationRepository(db)

        update_data = data.model_dump(
            exclude_unset=True,
        )

        if (
            "name" in update_data
            and update_data["name"] != sales_organization.name
        ):

            existing = await repository.get_by_name(
                update_data["name"],
            )

            if (
                existing
                and existing.id != sales_organization.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sales Organization with this name already exists.",
                )

            slug = SalesOrganizationService._generate_slug(
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
                    or existing_slug.id == sales_organization.id
                ):
                    break

                slug = f"{original_slug}-{counter}"

                counter += 1

            sales_organization.slug = slug

        for field, value in update_data.items():

            setattr(
                sales_organization,
                field,
                value,
            )

        await db.flush()

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.UPDATE,
                resource=AuditResource.SALES_ORGANIZATION,
                resource_id=str(sales_organization.id),
                description="Sales Organization updated",
                audit_metadata={
                    "sales_organization_name": sales_organization.name,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            sales_organization,
        )

        return sales_organization

    @staticmethod
    async def delete_sales_organization(
        db: AsyncSession,
        sales_organization: SalesOrganization,
        actor_user_id: UUID,
    ) -> None:

        repository = SalesOrganizationRepository(db)

        await repository.delete(
            sales_organization,
        )

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.DELETE,
                resource=AuditResource.SALES_ORGANIZATION,
                resource_id=str(sales_organization.id),
                description="Sales Organization deleted",
                audit_metadata={
                    "sales_organization_name": sales_organization.name,
                },
            ),
        )

        await db.commit()