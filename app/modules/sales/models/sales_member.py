from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import (
    TimestampMixin,
    UUIDMixin,
)

from app.modules.organization_sales_accounts.models.organization_sales_account import OrganizationSalesAccount
from app.modules.sales.constants.sales_member_enums import (
    SalesMemberRole,
    SalesMemberStatus,
)

if TYPE_CHECKING:
    from app.modules.auth.models.user import User
    from app.modules.sales.models.sales_organization import (
        SalesOrganization,
    )
    from app.modules.sales.models.sales_team import (
        SalesTeam,
    )
    from app.modules.sales.models.territory import (
        Territory,
    )


class SalesMember(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Represents a platform user working within a Sales Organization.

    A Sales Member belongs to:

    - One User
    - One Sales Organization
    - One Sales Team
    - One Territory

    This entity manages commercial assignments only.

    Clinical responsibilities remain within
    OrganizationMembership and Provider modules.
    """

    __tablename__ = "sales_members"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "sales_organization_id",
            name="uq_sales_member_per_organization",
        ),
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    sales_organization_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sales_organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    sales_team_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sales_teams.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    territory_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "territories.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # -------------------------------------------------------------------------
    # Sales Role
    # -------------------------------------------------------------------------

    role: Mapped[SalesMemberRole] = mapped_column(
        Enum(
            SalesMemberRole,
            name="sales_member_role",
        ),
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # Assignment Status
    # -------------------------------------------------------------------------

    status: Mapped[SalesMemberStatus] = mapped_column(
        Enum(
            SalesMemberStatus,
            name="sales_member_status",
        ),
        default=SalesMemberStatus.ACTIVE,
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # Assignment Information
    # -------------------------------------------------------------------------

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # ORM Relationships
    # -------------------------------------------------------------------------

    user: Mapped["User"] = relationship(
        "User",
        back_populates="sales_members",
    )

    sales_organization: Mapped["SalesOrganization"] = relationship(
        "SalesOrganization",
        back_populates="sales_members",
    )

    sales_team: Mapped["SalesTeam"] = relationship(
        "SalesTeam",
        back_populates="sales_members",
    )

    territory: Mapped["Territory"] = relationship(
        "Territory",
        back_populates="sales_members",
    )
    
    created_accounts: Mapped[list["OrganizationSalesAccount"]] = relationship(
        "OrganizationSalesAccount",
        foreign_keys="OrganizationSalesAccount.created_by_sales_member_id",
        back_populates="created_by_sales_member",
    )
    
    owned_accounts: Mapped[list["OrganizationSalesAccount"]] = relationship(
        "OrganizationSalesAccount",
        foreign_keys="OrganizationSalesAccount.account_owner_sales_member_id",
        back_populates="account_owner_sales_member",
    )