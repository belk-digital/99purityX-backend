from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Text,
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

from app.modules.consultations.enums.consultation_enums import (
    ConsultationStatus,
)

if TYPE_CHECKING:
    from app.modules.appointments.models.appointment_model import Appointment
    from app.modules.documents.models.document_model import Document
    from app.modules.goals.models.health_goal_model import HealthGoal
    from app.modules.labs.models.lab_order_model import LabOrder
    from app.modules.optimization.models.optimization_program_model import (
        OptimizationProgram,
    )
    from app.modules.patients.models.patient_model import Patient
    from app.modules.providers.models.provider_model import Provider


class Consultation(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "consultations"

    appointment_id: Mapped[str] = mapped_column(
        ForeignKey("appointments.id"),
        unique=True,
        nullable=False,
        index=True,
    )

    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )

    provider_id: Mapped[str] = mapped_column(
        ForeignKey("providers.id"),
        nullable=False,
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[ConsultationStatus] = mapped_column(
        Enum(ConsultationStatus),
        default=ConsultationStatus.IN_PROGRESS,
        nullable=False,
        index=True,
    )

    chief_complaint: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    provider_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    follow_up_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    appointment: Mapped["Appointment"] = relationship(
        "Appointment",
        back_populates="consultation",
        lazy="selectin",
    )

    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="consultations",
        lazy="selectin",
    )

    provider: Mapped["Provider"] = relationship(
        "Provider",
        back_populates="consultations",
        lazy="selectin",
    )

    lab_orders: Mapped[list["LabOrder"]] = relationship(
        "LabOrder",
        back_populates="consultation",
        lazy="selectin",
    )

    optimization_programs: Mapped[list["OptimizationProgram"]] = relationship(
        "OptimizationProgram",
        back_populates="consultation",
        lazy="selectin",
    )

    health_goals: Mapped[list["HealthGoal"]] = relationship(
        "HealthGoal",
        back_populates="consultation",
        lazy="selectin",
    )

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="consultation",
        lazy="selectin",
    )
