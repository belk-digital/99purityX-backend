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

from app.modules.sales.models.territory import (
    Territory,
)

from app.modules.sales.repositories.sales_organization_repository import (
    SalesOrganizationRepository,
)
from app.modules.sales.repositories.territory_repository import (
    TerritoryRepository,
)

from app.modules.sales.schemas.territory_schema import (
    TerritoryCreateSchema,
    TerritoryUpdateSchema,
)


class TerritoryService:

    # -------------------------------------------------------------------------
    # Internal Validation Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    async def _validate_sales_organization(
        db: AsyncSession,
        sales_organization_id: UUID,
    ):

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
    async def _validate_parent_territory(
        repository: TerritoryRepository,
        sales_organization_id: UUID,
        parent_territory_id: UUID | None,
    ) -> Territory | None:

        if parent_territory_id is None:
            return None

        parent = await repository.get_by_id(
            parent_territory_id,
        )

        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent Territory not found.",
            )

        if (
            parent.sales_organization_id
            != sales_organization_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Parent Territory belongs to another "
                    "Sales Organization."
                ),
            )

        return parent

    @staticmethod
    async def _validate_duplicate_name(
        repository: TerritoryRepository,
        sales_organization_id: UUID,
        parent_territory_id: UUID | None,
        name: str,
        territory_id: UUID | None = None,
    ):

        existing = await repository.get_by_name(
            sales_organization_id=sales_organization_id,
            parent_territory_id=parent_territory_id,
            name=name,
        )

        if (
            existing
            and existing.id != territory_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Territory with this name already "
                    "exists under the same parent."
                ),
            )

    @staticmethod
    async def _validate_duplicate_code(
        repository: TerritoryRepository,
        sales_organization_id: UUID,
        code: str,
        territory_id: UUID | None = None,
    ):

        existing = await repository.get_by_code(
            sales_organization_id=sales_organization_id,
            code=code,
        )

        if (
            existing
            and existing.id != territory_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Territory code already exists.",
            )

    @staticmethod
    async def _validate_no_circular_reference(
        repository: TerritoryRepository,
        territory_id: UUID,
        parent_territory_id: UUID | None,
    ):

        if parent_territory_id is None:
            return

        if territory_id == parent_territory_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "A Territory cannot be its own parent."
                ),
            )

        current_parent_id = parent_territory_id

        while current_parent_id is not None:

            parent = await repository.get_by_id(
                current_parent_id,
            )

            if parent is None:
                break

            if parent.id == territory_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Circular Territory hierarchy "
                        "detected."
                    ),
                )

            current_parent_id = parent.parent_territory_id

    # -------------------------------------------------------------------------
    # Create Territory
    # -------------------------------------------------------------------------

    @staticmethod
    async def create_territory(
        db: AsyncSession,
        data: TerritoryCreateSchema,
        actor_user_id: UUID,
    ) -> Territory:

        repository = TerritoryRepository(db)

        await TerritoryService._validate_sales_organization(
            db=db,
            sales_organization_id=data.sales_organization_id,
        )

        await TerritoryService._validate_parent_territory(
            repository=repository,
            sales_organization_id=data.sales_organization_id,
            parent_territory_id=data.parent_territory_id,
        )

        await TerritoryService._validate_duplicate_name(
            repository=repository,
            sales_organization_id=data.sales_organization_id,
            parent_territory_id=data.parent_territory_id,
            name=data.name,
        )

        await TerritoryService._validate_duplicate_code(
            repository=repository,
            sales_organization_id=data.sales_organization_id,
            code=data.code,
        )

        territory = Territory(
            sales_organization_id=data.sales_organization_id,
            parent_territory_id=data.parent_territory_id,
            name=data.name,
            code=data.code,
            level=data.level,
            country=data.country,
            state=data.state,
            city=data.city,
            description=data.description,
            is_active=data.is_active,
        )

        territory = await repository.create(
            territory,
        )

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.CREATE,
                resource=AuditResource.TERRITORY,
                resource_id=str(territory.id),
                description="Territory created",
                audit_metadata={
                    "territory_name": territory.name,
                    "territory_code": territory.code,
                    "sales_organization_id": str(
                        territory.sales_organization_id
                    ),
                },
            ),
        )

        await db.commit()

        await db.refresh(
            territory,
        )

        return territory
    
        # -------------------------------------------------------------------------
    # Get Territory
    # -------------------------------------------------------------------------

    @staticmethod
    async def get_territory(
        db: AsyncSession,
        territory_id: UUID,
    ) -> Territory:

        repository = TerritoryRepository(db)

        territory = await repository.get_by_id(
            territory_id,
        )

        if not territory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Territory not found.",
            )

        return territory

    # -------------------------------------------------------------------------
    # Get All Territories
    # -------------------------------------------------------------------------

    @staticmethod
    async def get_all_territories(
        db: AsyncSession,
    ) -> list[Territory]:

        repository = TerritoryRepository(db)

        return await repository.get_all()

    # -------------------------------------------------------------------------
    # Update Territory
    # -------------------------------------------------------------------------

    @staticmethod
    async def update_territory(
        db: AsyncSession,
        territory: Territory,
        data: TerritoryUpdateSchema,
        actor_user_id: UUID,
    ) -> Territory:

        repository = TerritoryRepository(db)

        update_data = data.model_dump(
            exclude_unset=True,
        )

        # --------------------------------------------------------------
        # Parent Territory Validation
        # --------------------------------------------------------------

        if "parent_territory_id" in update_data:

            await TerritoryService._validate_parent_territory(
                repository=repository,
                sales_organization_id=territory.sales_organization_id,
                parent_territory_id=update_data["parent_territory_id"],
            )

            await TerritoryService._validate_no_circular_reference(
                repository=repository,
                territory_id=territory.id,
                parent_territory_id=update_data["parent_territory_id"],
            )

        # --------------------------------------------------------------
        # Duplicate Name Validation
        # --------------------------------------------------------------

        if (
            "name" in update_data
            or "parent_territory_id" in update_data
        ):

            await TerritoryService._validate_duplicate_name(
                repository=repository,
                sales_organization_id=territory.sales_organization_id,
                parent_territory_id=update_data.get(
                    "parent_territory_id",
                    territory.parent_territory_id,
                ),
                name=update_data.get(
                    "name",
                    territory.name,
                ),
                territory_id=territory.id,
            )

        # --------------------------------------------------------------
        # Duplicate Code Validation
        # --------------------------------------------------------------

        if "code" in update_data:

            await TerritoryService._validate_duplicate_code(
                repository=repository,
                sales_organization_id=territory.sales_organization_id,
                code=update_data["code"],
                territory_id=territory.id,
            )

        # --------------------------------------------------------------
        # Apply Updates
        # --------------------------------------------------------------

        for field, value in update_data.items():

            setattr(
                territory,
                field,
                value,
            )

        await db.flush()

        # --------------------------------------------------------------
        # Audit Log
        # --------------------------------------------------------------

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.UPDATE,
                resource=AuditResource.TERRITORY,
                resource_id=str(territory.id),
                description="Territory updated",
                audit_metadata={
                    "territory_name": territory.name,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            territory,
        )

        return territory
    
        # -------------------------------------------------------------------------
    # Delete Territory
    # -------------------------------------------------------------------------

    @staticmethod
    async def delete_territory(
        db: AsyncSession,
        territory: Territory,
        actor_user_id: UUID,
    ) -> None:

        repository = TerritoryRepository(db)

        # --------------------------------------------------------------
        # Prevent deletion if child territories exist
        # --------------------------------------------------------------

        if await repository.has_children(
            territory.id,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Cannot delete Territory because it has child "
                    "Territories."
                ),
            )

        await repository.delete(
            territory,
        )

        # --------------------------------------------------------------
        # Audit Log
        # --------------------------------------------------------------

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.DELETE,
                resource=AuditResource.TERRITORY,
                resource_id=str(territory.id),
                description="Territory deleted",
                audit_metadata={
                    "territory_name": territory.name,
                    "territory_code": territory.code,
                    "sales_organization_id": str(
                        territory.sales_organization_id
                    ),
                },
            ),
        )

        await db.commit()