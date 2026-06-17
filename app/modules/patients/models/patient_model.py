from datetime import date

from sqlalchemy import (
    Date,
    ForeignKey,
    String,
    Float,
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
from app.modules.consultations.models.consultation_model import Consultation
from app.modules.labs.models.lab_order_model import LabOrder
from app.modules.optimization.models.optimization_program_model import (
    OptimizationProgram,
)
from app.modules.optimization.models.habit_log_model import HabitLog
from app.modules.optimization.models.habit_protocol_model import HabitProtocol
from app.modules.optimization.models.peptide_protocol_model import (
    PeptideProtocol,
)
from app.modules.goals.models.health_goal_model import HealthGoal
from app.modules.analytics.models.patient_health_score_model import (
    PatientHealthScore,
)
from app.modules.documents.models.document_model import Document


class Patient(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "patients"

    user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    gender: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    blood_group: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    height_cm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    weight_kg: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    emergency_contact_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    emergency_contact_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    timezone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    preferred_language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="patient",
    )
    
    appointments = relationship(
        "Appointment",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    
    consultations: Mapped[list["Consultation"]] = relationship(
        "Consultation",
        back_populates="patient",
        lazy="selectin",
    )

    lab_orders: Mapped[list["LabOrder"]] = relationship(
        "LabOrder",
        back_populates="patient",
        lazy="selectin",
    )

    optimization_programs: Mapped[list["OptimizationProgram"]] = relationship(
        "OptimizationProgram",
        back_populates="patient",
        lazy="selectin",
    )

    habit_protocols: Mapped[list["HabitProtocol"]] = relationship(
        "HabitProtocol",
        back_populates="patient",
        lazy="selectin",
    )

    habit_logs: Mapped[list["HabitLog"]] = relationship(
        "HabitLog",
        back_populates="patient",
        lazy="selectin",
    )

    peptide_protocols: Mapped[list["PeptideProtocol"]] = relationship(
        "PeptideProtocol",
        back_populates="patient",
        lazy="selectin",
    )

    health_goals: Mapped[list["HealthGoal"]] = relationship(
        "HealthGoal",
        back_populates="patient",
        lazy="selectin",
    )

    health_scores: Mapped[list["PatientHealthScore"]] = relationship(
        "PatientHealthScore",
        back_populates="patient",
        lazy="selectin",
    )

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="patient",
        lazy="selectin",
    )
