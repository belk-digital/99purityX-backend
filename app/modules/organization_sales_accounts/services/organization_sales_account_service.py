from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.constants.business_identifier_prefixes import (
    BusinessIdentifierPrefix,
)
from app.infrastructure.services.business_identifier_service import (
    BusinessIdentifierService,
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

from app.modules.organizations.repositories.organization_repository import (
    OrganizationRepository,
)

from app.modules.sales.repositories.sales_member_repository import (
    SalesMemberRepository,
)
from app.modules.sales.repositories.sales_organization_repository import (
    SalesOrganizationRepository,
)

from app.modules.organization_sales_accounts.models.organization_sales_account import (
    OrganizationSalesAccount,
)
from app.modules.organization_sales_accounts.repositories.organization_sales_account_repository import (
    OrganizationSalesAccountRepository,
)
from app.modules.organization_sales_accounts.schemas.organization_sales_account_schema import (
    OrganizationSalesAccountCreateSchema,
    OrganizationSalesAccountUpdateSchema,
)


class OrganizationSalesAccountService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.repository = (
            OrganizationSalesAccountRepository(db)
        )

        self.organization_repository = (
            OrganizationRepository(db)
        )

        self.sales_organization_repository = (
            SalesOrganizationRepository(db)
        )

        self.sales_member_repository = (
            SalesMemberRepository(db)
        )

    # -------------------------------------------------------------------------
    # Validation Helpers
    # -------------------------------------------------------------------------

    async def _validate_organization(
        self,
        organization_id: UUID,
    ):

        organization = (
            await self.organization_repository.get_by_id(
                organization_id,
            )
        )

        if organization is None:
            raise ValueError(
                "Organization not found."
            )

        return organization

    async def _validate_sales_organization(
        self,
        sales_organization_id: UUID,
    ):

        sales_organization = (
            await self.sales_organization_repository.get_by_id(
                sales_organization_id,
            )
        )

        if sales_organization is None:
            raise ValueError(
                "Sales Organization not found."
            )

        return sales_organization

    async def _validate_sales_member(
        self,
        sales_member_id: UUID,
    ):

        sales_member = (
            await self.sales_member_repository.get_by_id(
                sales_member_id,
            )
        )

        if sales_member is None:
            raise ValueError(
                "Sales Member not found."
            )

        return sales_member

    async def _validate_unique_account(
        self,
        organization_id: UUID,
    ):

        existing_account = (
            await self.repository.get_by_organization(
                organization_id,
            )
        )

        if existing_account is not None:
            raise ValueError(
                "Organization already has a commercial account."
            )

    def _validate_sales_organization_membership(
        self,
        creator,
        owner,
        sales_organization_id: UUID,
    ):

        if (
            creator.sales_organization_id
            != sales_organization_id
        ):
            raise ValueError(
                "Creator does not belong to the selected Sales Organization."
            )

        if (
            owner.sales_organization_id
            != sales_organization_id
        ):
            raise ValueError(
                "Account owner does not belong to the selected Sales Organization."
            )
            
        # -------------------------------------------------------------------------
    # Create
    # -------------------------------------------------------------------------

    async def create_organization_sales_account(
        self,
        payload: OrganizationSalesAccountCreateSchema,
        performed_by: UUID,
    ) -> OrganizationSalesAccount:

        # ---------------------------------------------------------------------
        # Validate Organization
        # ---------------------------------------------------------------------

        await self._validate_organization(
            payload.organization_id,
        )

        # ---------------------------------------------------------------------
        # Validate Sales Organization
        # ---------------------------------------------------------------------

        await self._validate_sales_organization(
            payload.sales_organization_id,
        )

        # ---------------------------------------------------------------------
        # Validate Sales Members
        # ---------------------------------------------------------------------

        creator = await self._validate_sales_member(
            payload.created_by_sales_member_id,
        )

        owner = await self._validate_sales_member(
            payload.account_owner_sales_member_id,
        )

        # ---------------------------------------------------------------------
        # Validate Membership
        # ---------------------------------------------------------------------

        self._validate_sales_organization_membership(
            creator=creator,
            owner=owner,
            sales_organization_id=payload.sales_organization_id,
        )

        # ---------------------------------------------------------------------
        # Validate One Commercial Account Per Organization
        # ---------------------------------------------------------------------

        await self._validate_unique_account(
            payload.organization_id,
        )

        # ---------------------------------------------------------------------
        # Generate Business Account Number
        # ---------------------------------------------------------------------

        account_number = (
            await BusinessIdentifierService.generate_next(
                db=self.db,
                prefix=BusinessIdentifierPrefix.ACCOUNT,
            )
        )

        # ---------------------------------------------------------------------
        # Create Model
        # ---------------------------------------------------------------------

        account = OrganizationSalesAccount(
            account_number=account_number,
            organization_id=payload.organization_id,
            sales_organization_id=payload.sales_organization_id,
            created_by_sales_member_id=payload.created_by_sales_member_id,
            account_owner_sales_member_id=payload.account_owner_sales_member_id,
            account_type=payload.account_type,
            status=payload.status,
            customer_since=datetime.now(
                timezone.utc,
            ),
            contract_start=payload.contract_start,
            contract_end=payload.contract_end,
            renewal_date=payload.renewal_date,
            notes=payload.notes,
            is_active=payload.is_active,
        )

        account = await self.repository.create(
            account,
        )

        # ---------------------------------------------------------------------
        # Audit Log
        # ---------------------------------------------------------------------

        await AuditService.create_log(
            db=self.db,
            actor_user_id=performed_by,
            payload=AuditLogCreate(
                action=AuditAction.CREATE,
                resource=AuditResource.ORGANIZATION_SALES_ACCOUNT,
                resource_id=account.id,
                description=(
                    f"Created commercial account "
                    f"{account.account_number}"
                ),
            ),
        )

        # ---------------------------------------------------------------------
        # Commit Transaction
        # ---------------------------------------------------------------------

        await self.db.commit()

        await self.db.refresh(
            account,
        )

        return account

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    async def get_by_id(
        self,
        account_id: UUID,
    ) -> OrganizationSalesAccount:

        account = await self.repository.get_by_id(
            account_id,
        )

        if account is None:
            raise ValueError(
                "Commercial account not found."
            )

        return account

    async def get_all(
        self,
    ) -> list[OrganizationSalesAccount]:

        return await self.repository.get_all()
    
        # -------------------------------------------------------------------------
    # Update
    # -------------------------------------------------------------------------

    async def update_organization_sales_account(
        self,
        account_id: UUID,
        payload: OrganizationSalesAccountUpdateSchema,
        performed_by: UUID,
    ) -> OrganizationSalesAccount:

        account = await self.get_by_id(
            account_id,
        )

        # ---------------------------------------------------------------------
        # Validate Account Owner
        # ---------------------------------------------------------------------

        if payload.account_owner_sales_member_id is not None:

            owner = await self._validate_sales_member(
                payload.account_owner_sales_member_id,
            )

            self._validate_sales_organization_membership(
                creator=owner,
                owner=owner,
                sales_organization_id=account.sales_organization_id,
            )

            account.account_owner_sales_member_id = (
                payload.account_owner_sales_member_id
            )

        # ---------------------------------------------------------------------
        # Update Fields
        # ---------------------------------------------------------------------

        if payload.account_type is not None:
            account.account_type = payload.account_type

        if payload.status is not None:
            account.status = payload.status

        if payload.contract_start is not None:
            account.contract_start = payload.contract_start

        if payload.contract_end is not None:
            account.contract_end = payload.contract_end

        if payload.renewal_date is not None:
            account.renewal_date = payload.renewal_date

        if payload.notes is not None:
            account.notes = payload.notes

        if payload.is_active is not None:
            account.is_active = payload.is_active

        account = await self.repository.update(
            account,
        )

        # ---------------------------------------------------------------------
        # Audit Log
        # ---------------------------------------------------------------------

        await AuditService.create_log(
            db=self.db,
            actor_user_id=performed_by,
            payload=AuditLogCreate(
                action=AuditAction.UPDATE,
                resource=AuditResource.ORGANIZATION_SALES_ACCOUNT,
                resource_id=account.id,
                description=(
                    f"Updated commercial account "
                    f"{account.account_number}"
                ),
            ),
        )

        await self.db.commit()

        await self.db.refresh(
            account,
        )

        return account

    # -------------------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------------------

    async def delete_organization_sales_account(
        self,
        account_id: UUID,
        performed_by: UUID,
    ) -> None:

        account = await self.get_by_id(
            account_id,
        )

        await self.repository.delete(
            account,
        )

        # ---------------------------------------------------------------------
        # Audit Log
        # ---------------------------------------------------------------------

        await AuditService.create_log(
            db=self.db,
            actor_user_id=performed_by,
            payload=AuditLogCreate(
                action=AuditAction.DELETE,
                resource=AuditResource.ORGANIZATION_SALES_ACCOUNT,
                resource_id=account.id,
                description=(
                    f"Deleted commercial account "
                    f"{account.account_number}"
                ),
            ),
        )

        await self.db.commit()