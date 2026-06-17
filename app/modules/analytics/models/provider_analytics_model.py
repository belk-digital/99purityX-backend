from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.modules.providers.models.provider_model import Provider


class ProviderAnalytics(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "provider_analytics"

    provider_id: Mapped[str] = mapped_column(
        ForeignKey("providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    active_patients: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    active_programs: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    completed_goals: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    average_adherence: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    average_health_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    provider: Mapped["Provider"] = relationship(
        "Provider",
        back_populates="analytics_snapshots",
        lazy="selectin",
    )
