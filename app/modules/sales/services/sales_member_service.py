from datetime import datetime, timezone
from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.repositories.user_repository import (
    UserRepository,
)
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
from app.modules.sales.models import sales_member
from app.modules.sales.models.sales_member import (
    SalesMember,
)
from app.modules.sales.repositories.sales_member_repository import (
    SalesMemberRepository,
)
from app.modules.sales.repositories.sales_organization_repository import (
    SalesOrganizationRepository,
)
from app.modules.sales.repositories.sales_team_repository import (
    SalesTeamRepository,
)
from app.modules.sales.repositories.territory_repository import (
    TerritoryRepository,
)
from app.modules.sales.schemas.sales_member_schema import (
    SalesMemberCreateSchema,
    SalesMemberUpdateSchema,
)


class SalesMemberService:

    # -------------------------------------------------------------------------
    # Validation Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    async def _validate_user(
        db: AsyncSession,
        user_id: UUID,
    ):

        repository = UserRepository(db)

        user = await repository.get_by_id(
            user_id,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        return user

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
    async def _validate_sales_team(
        db: AsyncSession,
        sales_team_id: UUID,
        sales_organization_id: UUID,
    ):

        repository = SalesTeamRepository(db)

        sales_team = await repository.get_by_id(
            sales_team_id,
        )

        if not sales_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales Team not found.",
            )

        if (
            sales_team.sales_organization_id
            != sales_organization_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Sales Team does not belong to the selected "
                    "Sales Organization."
                ),
            )

        return sales_team

    @staticmethod
    async def _validate_territory(
        db: AsyncSession,
        territory_id: UUID,
        sales_organization_id: UUID,
    ):

        repository = TerritoryRepository(db)

        territory = await repository.get_by_id(
            territory_id,
        )

        if not territory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Territory not found.",
            )

        if (
            territory.sales_organization_id
            != sales_organization_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Territory does not belong to the selected "
                    "Sales Organization."
                ),
            )

        return territory

    @staticmethod
    async def _validate_duplicate_membership(
        repository: SalesMemberRepository,
        user_id: UUID,
        sales_organization_id: UUID,
        sales_member_id: UUID | None = None,
    ):

        existing = await repository.get_by_user_and_sales_organization(
            user_id=user_id,
            sales_organization_id=sales_organization_id,
        )

        if (
            existing
            and existing.id != sales_member_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "User is already a member of this "
                    "Sales Organization."
                ),
            )

    # -------------------------------------------------------------------------
    # Create Sales Member
    # -------------------------------------------------------------------------

    @staticmethod
    async def create_sales_member(
        db: AsyncSession,
        data: SalesMemberCreateSchema,
        actor_user_id: UUID,
    ) -> SalesMember:

        repository = SalesMemberRepository(db)

        await SalesMemberService._validate_user(
            db=db,
            user_id=data.user_id,
        )

        await SalesMemberService._validate_sales_organization(
            db=db,
            sales_organization_id=data.sales_organization_id,
        )

        await SalesMemberService._validate_sales_team(
            db=db,
            sales_team_id=data.sales_team_id,
            sales_organization_id=data.sales_organization_id,
        )

        await SalesMemberService._validate_territory(
            db=db,
            territory_id=data.territory_id,
            sales_organization_id=data.sales_organization_id,
        )

        await SalesMemberService._validate_duplicate_membership(
            repository=repository,
            user_id=data.user_id,
            sales_organization_id=data.sales_organization_id,
        )
        
        if data.is_primary:

            await SalesMemberService._clear_existing_primary_membership(
                repository=repository,
                user_id=data.user_id,
            )

        sales_member = SalesMember(
            user_id=data.user_id,
            sales_organization_id=data.sales_organization_id,
            sales_team_id=data.sales_team_id,
            territory_id=data.territory_id,
            role=data.role,
            joined_at=data.joined_at
            or datetime.now(timezone.utc),
            is_primary=data.is_primary,
            is_active=data.is_active,
        )

        sales_member = await repository.create(
            sales_member,
        )

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.CREATE,
                resource=AuditResource.SALES_MEMBER,
                resource_id=str(sales_member.id),
                description="Sales Member created",
                audit_metadata={
                    "user_id": str(
                        sales_member.user_id,
                    ),
                    "sales_organization_id": str(
                        sales_member.sales_organization_id,
                    ),
                    "role": sales_member.role.value,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            sales_member,
        )

        return sales_member
    
        # -------------------------------------------------------------------------
    # Get Sales Member
    # -------------------------------------------------------------------------

    @staticmethod
    async def get_sales_member(
        db: AsyncSession,
        sales_member_id: UUID,
    ) -> SalesMember:

        repository = SalesMemberRepository(db)

        sales_member = await repository.get_by_id(
            sales_member_id,
        )

        if not sales_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales Member not found.",
            )

        return sales_member

    # -------------------------------------------------------------------------
    # Get All Sales Members
    # -------------------------------------------------------------------------

    @staticmethod
    async def get_all_sales_members(
        db: AsyncSession,
    ) -> list[SalesMember]:

        repository = SalesMemberRepository(db)

        return await repository.get_all()

    # -------------------------------------------------------------------------
    # Update Sales Member
    # -------------------------------------------------------------------------

    @staticmethod
    async def update_sales_member(
        db: AsyncSession,
        sales_member: SalesMember,
        data: SalesMemberUpdateSchema,
        actor_user_id: UUID,
    ) -> SalesMember:

        repository = SalesMemberRepository(db)

        update_data = data.model_dump(
            exclude_unset=True,
        )

        # --------------------------------------------------------------
        # Validate Sales Team
        # --------------------------------------------------------------

        if "sales_team_id" in update_data:

            await SalesMemberService._validate_sales_team(
                db=db,
                sales_team_id=update_data["sales_team_id"],
                sales_organization_id=sales_member.sales_organization_id,
            )

        # --------------------------------------------------------------
        # Validate Territory
        # --------------------------------------------------------------

        if "territory_id" in update_data:

            await SalesMemberService._validate_territory(
                db=db,
                territory_id=update_data["territory_id"],
                sales_organization_id=sales_member.sales_organization_id,
            )

        # --------------------------------------------------------------
        # Apply Updates
        # --------------------------------------------------------------
        if (
            update_data.get("is_primary")
            is True
        ):

            await SalesMemberService._clear_existing_primary_membership(
                repository=repository,
                user_id=sales_member.user_id,
            )
            
        for field, value in update_data.items():

            setattr(
                sales_member,
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
                resource=AuditResource.SALES_MEMBER,
                resource_id=str(sales_member.id),
                description="Sales Member updated",
                audit_metadata={
                    "user_id": str(
                        sales_member.user_id,
                    ),
                    "sales_organization_id": str(
                        sales_member.sales_organization_id,
                    ),
                    "role": sales_member.role.value,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            sales_member,
        )

        return sales_member
    
    
        # -------------------------------------------------------------------------
    # Primary Assignment Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    async def _clear_existing_primary_membership(
        repository: SalesMemberRepository,
        user_id: UUID,
    ) -> None:
        """
        Ensures that a user has only one primary Sales Member assignment.
        """

        sales_members = await repository.get_by_user(
            user_id,
        )

        for member in sales_members:

            if member.is_primary:

                member.is_primary = False

    # -------------------------------------------------------------------------
    # Delete Sales Member
    # -------------------------------------------------------------------------

    @staticmethod
    async def delete_sales_member(
        db: AsyncSession,
        sales_member: SalesMember,
        actor_user_id: UUID,
    ) -> None:

        repository = SalesMemberRepository(db)

        await repository.delete(
            sales_member,
        )

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.DELETE,
                resource=AuditResource.SALES_MEMBER,
                resource_id=str(sales_member.id),
                description="Sales Member deleted",
                audit_metadata={
                    "user_id": str(
                        sales_member.user_id,
                    ),
                    "sales_organization_id": str(
                        sales_member.sales_organization_id,
                    ),
                    "role": sales_member.role.value,
                },
            ),
        )

        await db.commit()