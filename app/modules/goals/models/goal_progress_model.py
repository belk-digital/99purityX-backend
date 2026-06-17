from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.modules.goals.models.health_goal_model import HealthGoal


class GoalProgress(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "goal_progress"

    goal_id: Mapped[str] = mapped_column(
        ForeignKey("health_goals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    value: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    goal: Mapped["HealthGoal"] = relationship(
        "HealthGoal",
        back_populates="progress_records",
        lazy="selectin",
    )
