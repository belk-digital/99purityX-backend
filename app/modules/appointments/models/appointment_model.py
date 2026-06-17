from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
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

from app.modules.appointments.enums.appointment_enums import (
    AppointmentStatus,
)
from app.modules.consultations.models.consultation_model import Consultation


class Appointment(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "appointments"

    __table_args__ = (
        Index(
            "ix_appointments_provider_schedule",
            "provider_id",
            "scheduled_start",
        ),
    )

    patient_id: Mapped[str] = mapped_column(
        ForeignKey(
            "patients.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    provider_id: Mapped[str] = mapped_column(
        ForeignKey(
            "providers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    scheduled_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    scheduled_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus),
        default=AppointmentStatus.SCHEDULED,
        nullable=False,
        index=True,
    )

    reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    patient = relationship(
        "Patient",
        back_populates="appointments",
    )

    provider = relationship(
        "Provider",
        back_populates="appointments",
    )
    
    consultation: Mapped["Consultation"] = relationship(
        "Consultation",
        back_populates="appointment",
        uselist=False,
        lazy="selectin",
    )