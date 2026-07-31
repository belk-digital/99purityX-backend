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

from app.modules.sales.models.sales_team import (
    SalesTeam,
)
from app.modules.sales.repositories.sales_organization_repository import (
    SalesOrganizationRepository,
)
from app.modules.sales.repositories.sales_team_repository import (
    SalesTeamRepository,
)
from app.modules.sales.schemas.sales_team_schema import (
    SalesTeamCreateSchema,
    SalesTeamUpdateSchema,
)


class SalesTeamService:

    @staticmethod
    async def create_sales_team(
        db: AsyncSession,
        data: SalesTeamCreateSchema,
        actor_user_id: UUID,
    ) -> SalesTeam:

        team_repository = SalesTeamRepository(db)
        organization_repository = SalesOrganizationRepository(db)

        # --------------------------------------------------
        # Validate Sales Organization
        # --------------------------------------------------

        sales_organization = (
            await organization_repository.get_by_id(
                data.sales_organization_id,
            )
        )

        if not sales_organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales Organization not found.",
            )

        # --------------------------------------------------
        # Duplicate Team Name
        # --------------------------------------------------

        existing_name = await team_repository.get_by_name(
            sales_organization_id=data.sales_organization_id,
            name=data.name,
        )

        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sales Team with this name already exists.",
            )

        # --------------------------------------------------
        # Duplicate Team Code
        # --------------------------------------------------

        existing_code = await team_repository.get_by_team_code(
            sales_organization_id=data.sales_organization_id,
            team_code=data.team_code,
        )

        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sales Team code already exists.",
            )

        sales_team = SalesTeam(
            sales_organization_id=data.sales_organization_id,
            name=data.name,
            team_code=data.team_code,
            description=data.description,
            is_active=data.is_active,
        )

        sales_team = await team_repository.create(
            sales_team,
        )

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.CREATE,
                resource=AuditResource.SALES_TEAM,
                resource_id=str(sales_team.id),
                description="Sales Team created",
                audit_metadata={
                    "sales_team_name": sales_team.name,
                    "sales_organization_id": str(
                        sales_team.sales_organization_id
                    ),
                },
            ),
        )

        await db.commit()

        await db.refresh(
            sales_team,
        )

        return sales_team

    @staticmethod
    async def get_sales_team(
        db: AsyncSession,
        sales_team_id: UUID,
    ) -> SalesTeam:

        repository = SalesTeamRepository(db)

        sales_team = await repository.get_by_id(
            sales_team_id,
        )

        if not sales_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales Team not found.",
            )

        return sales_team

    @staticmethod
    async def get_all_sales_teams(
        db: AsyncSession,
    ) -> list[SalesTeam]:

        repository = SalesTeamRepository(db)

        return await repository.get_all()

    @staticmethod
    async def update_sales_team(
        db: AsyncSession,
        sales_team: SalesTeam,
        data: SalesTeamUpdateSchema,
        actor_user_id: UUID,
    ) -> SalesTeam:

        repository = SalesTeamRepository(db)

        update_data = data.model_dump(
            exclude_unset=True,
        )

        if (
            "name" in update_data
            and update_data["name"] != sales_team.name
        ):

            existing = await repository.get_by_name(
                sales_organization_id=sales_team.sales_organization_id,
                name=update_data["name"],
            )

            if (
                existing
                and existing.id != sales_team.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sales Team with this name already exists.",
                )

        if (
            "team_code" in update_data
            and update_data["team_code"] != sales_team.team_code
        ):

            existing = await repository.get_by_team_code(
                sales_organization_id=sales_team.sales_organization_id,
                team_code=update_data["team_code"],
            )

            if (
                existing
                and existing.id != sales_team.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sales Team code already exists.",
                )

        for field, value in update_data.items():

            setattr(
                sales_team,
                field,
                value,
            )

        await db.flush()

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.UPDATE,
                resource=AuditResource.SALES_TEAM,
                resource_id=str(sales_team.id),
                description="Sales Team updated",
                audit_metadata={
                    "sales_team_name": sales_team.name,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            sales_team,
        )

        return sales_team

    @staticmethod
    async def delete_sales_team(
        db: AsyncSession,
        sales_team: SalesTeam,
        actor_user_id: UUID,
    ) -> None:

        repository = SalesTeamRepository(db)

        await repository.delete(
            sales_team,
        )

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.DELETE,
                resource=AuditResource.SALES_TEAM,
                resource_id=str(sales_team.id),
                description="Sales Team deleted",
                audit_metadata={
                    "sales_team_name": sales_team.name,
                },
            ),
        )

        await db.commit()