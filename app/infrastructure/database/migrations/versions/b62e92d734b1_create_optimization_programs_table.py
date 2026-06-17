"""create optimization programs table

Revision ID: b62e92d734b1
Revises: a41d1c6d9f2b
Create Date: 2026-05-30 00:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b62e92d734b1"
down_revision: Union[str, None] = "a41d1c6d9f2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "optimization_programs",
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("provider_id", sa.UUID(), nullable=False),
        sa.Column("consultation_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("goal", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "ACTIVE",
                "PAUSED",
                "COMPLETED",
                "CANCELLED",
                name="optimizationprogramstatus",
            ),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["consultation_id"],
            ["consultations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
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
        op.f("ix_optimization_programs_consultation_id"),
        "optimization_programs",
        ["consultation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_optimization_programs_patient_id"),
        "optimization_programs",
        ["patient_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_optimization_programs_provider_id"),
        "optimization_programs",
        ["provider_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_optimization_programs_status"),
        "optimization_programs",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_optimization_programs_status"),
        table_name="optimization_programs",
    )
    op.drop_index(
        op.f("ix_optimization_programs_provider_id"),
        table_name="optimization_programs",
    )
    op.drop_index(
        op.f("ix_optimization_programs_patient_id"),
        table_name="optimization_programs",
    )
    op.drop_index(
        op.f("ix_optimization_programs_consultation_id"),
        table_name="optimization_programs",
    )
    op.drop_table("optimization_programs")
    op.execute("DROP TYPE IF EXISTS optimizationprogramstatus")
