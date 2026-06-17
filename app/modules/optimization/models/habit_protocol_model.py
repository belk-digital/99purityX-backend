from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import TimestampMixin, UUIDMixin
from app.modules.optimization.enums.program_enums import (
    HabitFrequency,
    HabitProtocolStatus,
)

if TYPE_CHECKING:
    from app.modules.optimization.models.habit_log_model import HabitLog
    from app.modules.optimization.models.optimization_program_model import (
        OptimizationProgram,
    )
    from app.modules.patients.models.patient_model import Patient
    from app.modules.providers.models.provider_model import Provider


class HabitProtocol(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "habit_protocols"

    program_id: Mapped[str] = mapped_column(
        ForeignKey("optimization_programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider_id: Mapped[str] = mapped_column(
        ForeignKey("providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    target_value: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4),
        nullable=True,
    )

    target_unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    frequency: Mapped[HabitFrequency] = mapped_column(
        Enum(HabitFrequency),
        default=HabitFrequency.DAILY,
        nullable=False,
        index=True,
    )

    status: Mapped[HabitProtocolStatus] = mapped_column(
        Enum(HabitProtocolStatus),
        default=HabitProtocolStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    program: Mapped["OptimizationProgram"] = relationship(
        "OptimizationProgram",
        back_populates="habit_protocols",
        lazy="selectin",
    )

    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="habit_protocols",
        lazy="selectin",
    )

    provider: Mapped["Provider"] = relationship(
        "Provider",
        back_populates="habit_protocols",
        lazy="selectin",
    )

    logs: Mapped[list["HabitLog"]] = relationship(
        "HabitLog",
        back_populates="habit_protocol",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
