"""create optimization habits tables

Revision ID: c73f18a9d4e2
Revises: b62e92d734b1
Create Date: 2026-05-30 01:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c73f18a9d4e2"
down_revision: Union[str, None] = "b62e92d734b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "habit_protocols",
        sa.Column("program_id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("provider_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_value", sa.Numeric(12, 4), nullable=True),
        sa.Column("target_unit", sa.String(length=50), nullable=True),
        sa.Column(
            "frequency",
            sa.Enum(
                "DAILY",
                "WEEKLY",
                "MONTHLY",
                name="habitfrequency",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "PAUSED",
                "COMPLETED",
                "CANCELLED",
                name="habitprotocolstatus",
            ),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["program_id"],
            ["optimization_programs.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["provider_id"],
            ["providers.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_habit_protocols_frequency"),
        "habit_protocols",
        ["frequency"],
        unique=False,
    )
    op.create_index(
        op.f("ix_habit_protocols_patient_id"),
        "habit_protocols",
        ["patient_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_habit_protocols_program_id"),
        "habit_protocols",
        ["program_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_habit_protocols_provider_id"),
        "habit_protocols",
        ["provider_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_habit_protocols_status"),
        "habit_protocols",
        ["status"],
        unique=False,
    )

    op.create_table(
        "habit_logs",
        sa.Column("habit_protocol_id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("actual_value", sa.Numeric(12, 4), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["habit_protocol_id"],
            ["habit_protocols.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "habit_protocol_id",
            "date",
            name="uq_habit_log_protocol_date",
        ),
    )
    op.create_index(
        op.f("ix_habit_logs_completed"),
        "habit_logs",
        ["completed"],
        unique=False,
    )
    op.create_index(
        op.f("ix_habit_logs_date"),
        "habit_logs",
        ["date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_habit_logs_habit_protocol_id"),
        "habit_logs",
        ["habit_protocol_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_habit_logs_patient_id"),
        "habit_logs",
        ["patient_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_habit_logs_patient_id"),
        table_name="habit_logs",
    )
    op.drop_index(
        op.f("ix_habit_logs_habit_protocol_id"),
        table_name="habit_logs",
    )
    op.drop_index(
        op.f("ix_habit_logs_date"),
        table_name="habit_logs",
    )
    op.drop_index(
        op.f("ix_habit_logs_completed"),
        table_name="habit_logs",
    )
    op.drop_table("habit_logs")

    op.drop_index(
        op.f("ix_habit_protocols_status"),
        table_name="habit_protocols",
    )
    op.drop_index(
        op.f("ix_habit_protocols_provider_id"),
        table_name="habit_protocols",
    )
    op.drop_index(
        op.f("ix_habit_protocols_program_id"),
        table_name="habit_protocols",
    )
    op.drop_index(
        op.f("ix_habit_protocols_patient_id"),
        table_name="habit_protocols",
    )
    op.drop_index(
        op.f("ix_habit_protocols_frequency"),
        table_name="habit_protocols",
    )
    op.drop_table("habit_protocols")
    op.execute("DROP TYPE IF EXISTS habitprotocolstatus")
    op.execute("DROP TYPE IF EXISTS habitfrequency")
