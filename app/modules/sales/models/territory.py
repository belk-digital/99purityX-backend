from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    String,
    Text,
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

from app.modules.sales.constants.territory_enums import (
    TerritoryLevel,
    TerritoryStatus,
)

if TYPE_CHECKING:
    from app.modules.sales.models.sales_organization import SalesOrganization
    # from app.modules.sales.models.sales_member import SalesMember


class Territory(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Represents a geographical sales territory.

    Territories support hierarchical structures through
    self-referencing parent-child relationships.

    Example:

        India
            ├── North India
            │      ├── Delhi NCR
            │      │      ├── Delhi
            │      │      └── Noida
            │      └── Punjab
            └── South India
    """

    __tablename__ = "territories"

    __table_args__ = (
        UniqueConstraint(
            "sales_organization_id",
            "code",
            name="uq_territory_code_per_sales_org",
        ),
        UniqueConstraint(
            "sales_organization_id",
            "parent_territory_id",
            "name",
            name="uq_territory_name_per_parent",
        ),
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    sales_organization_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sales_organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    parent_territory_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "territories.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    # -------------------------------------------------------------------------
    # Territory Information
    # -------------------------------------------------------------------------

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    level: Mapped[TerritoryLevel] = mapped_column(
        Enum(
            TerritoryLevel,
            name="territory_level",
        ),
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # Geographic Metadata
    # -------------------------------------------------------------------------

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    status: Mapped[TerritoryStatus] = mapped_column(
        Enum(
            TerritoryStatus,
            name="territory_status",
        ),
        default=TerritoryStatus.ACTIVE,
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

    sales_organization: Mapped["SalesOrganization"] = relationship(
        "SalesOrganization",
        back_populates="territories",
    )

    parent: Mapped["Territory | None"] = relationship(
        "Territory",
        remote_side="Territory.id",
        back_populates="children",
    )

    children: Mapped[list["Territory"]] = relationship(
        "Territory",
        back_populates="parent",
        cascade="save-update, merge",
    )

    # -------------------------------------------------------------------------
    # Future Relationships
    # -------------------------------------------------------------------------

    # sales_members: Mapped[list["SalesMember"]] = relationship(
    #     "SalesMember",
    #     back_populates="territory",
    # )