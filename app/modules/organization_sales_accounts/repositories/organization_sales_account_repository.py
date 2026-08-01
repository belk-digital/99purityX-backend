from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.modules.organization_sales_accounts.models.organization_sales_account


class OrganizationSalesAccountRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # -------------------------------------------------------------------------
    # Create
    # -------------------------------------------------------------------------

    async def create(
        self,
        account: app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount,
    ) -> app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount:

        self.db.add(account)

        await self.db.flush()

        await self.db.refresh(account)

        return account

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    async def get_by_id(
        self,
        account_id: UUID,
    ) -> app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount | None:

        query = (
            select(app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount)
            .where(
                app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount.id == account_id
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_all(
        self,
    ) -> list[app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount]:

        query = (
            select(app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount)
            .order_by(
                app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount.created_at.desc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_by_organization(
        self,
        organization_id: UUID,
    ) -> app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount | None:

        query = (
            select(app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount)
            .where(
                app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount.organization_id == organization_id
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_account_number(
        self,
        account_number: str,
    ) -> app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount | None:

        query = (
            select(app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount)
            .where(
                app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount.account_number == account_number
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_sales_member(
        self,
        sales_member_id: UUID,
    ) -> list[app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount]:

        query = (
            select(app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount)
            .where(
                app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount.account_owner_sales_member_id
                == sales_member_id
            )
            .order_by(
                app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount.created_at.desc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_by_sales_organization(
        self,
        sales_organization_id: UUID,
    ) -> list[app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount]:

        query = (
            select(app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount)
            .where(
                app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount.sales_organization_id
                == sales_organization_id
            )
            .order_by(
                app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount.created_at.desc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def account_number_exists(
        self,
        account_number: str,
    ) -> bool:

        query = (
            select(app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount.id)
            .where(
                app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount.account_number == account_number
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none() is not None

    # -------------------------------------------------------------------------
    # Update
    # -------------------------------------------------------------------------

    async def update(
        self,
        account: app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount,
    ) -> app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount:

        await self.db.flush()

        await self.db.refresh(account)

        return account

    # -------------------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------------------

    async def delete(
        self,
        account: app.modules.organization_sales_accounts.models.organization_sales_account.OrganizationSalesAccount,
    ) -> None:

        await self.db.delete(account)

        await self.db.flush()