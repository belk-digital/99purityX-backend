from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.modules.optimization.models.habit_protocol_model import (
        HabitProtocol,
    )
    from app.modules.patients.models.patient_model import Patient


class HabitLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "habit_logs"

    __table_args__ = (
        UniqueConstraint(
            "habit_protocol_id",
            "date",
            name="uq_habit_log_protocol_date",
        ),
    )

    habit_protocol_id: Mapped[str] = mapped_column(
        ForeignKey("habit_protocols.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    actual_value: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4),
        nullable=True,
    )

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    habit_protocol: Mapped["HabitProtocol"] = relationship(
        "HabitProtocol",
        back_populates="logs",
        lazy="selectin",
    )

    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="habit_logs",
        lazy="selectin",
    )
