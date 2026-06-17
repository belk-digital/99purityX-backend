"""create analytics tables

Revision ID: f26c9a80d5b7
Revises: e15a7c49b8d3
Create Date: 2026-05-30 02:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f26c9a80d5b7"
down_revision: Union[str, None] = "e15a7c49b8d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "patient_health_scores",
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("overall_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("adherence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("biomarker_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("goal_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_patient_health_scores_calculated_at"),
        "patient_health_scores",
        ["calculated_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_patient_health_scores_patient_id"),
        "patient_health_scores",
        ["patient_id"],
        unique=False,
    )

    op.create_table(
        "provider_analytics",
        sa.Column("provider_id", sa.UUID(), nullable=False),
        sa.Column("active_patients", sa.Integer(), nullable=False),
        sa.Column("active_programs", sa.Integer(), nullable=False),
        sa.Column("completed_goals", sa.Integer(), nullable=False),
        sa.Column("average_adherence", sa.Numeric(5, 2), nullable=False),
        sa.Column("average_health_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["provider_id"],
            ["providers.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_provider_analytics_calculated_at"),
        "provider_analytics",
        ["calculated_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_provider_analytics_provider_id"),
        "provider_analytics",
        ["provider_id"],
        unique=False,
    )

    op.create_table(
        "program_analytics",
        sa.Column("program_id", sa.UUID(), nullable=False),
        sa.Column("enrolled_patients", sa.Integer(), nullable=False),
        sa.Column("average_adherence", sa.Numeric(5, 2), nullable=False),
        sa.Column("goal_completion_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("average_health_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["program_id"],
            ["optimization_programs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_program_analytics_calculated_at"),
        "program_analytics",
        ["calculated_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_program_analytics_program_id"),
        "program_analytics",
        ["program_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_program_analytics_program_id"),
        table_name="program_analytics",
    )
    op.drop_index(
        op.f("ix_program_analytics_calculated_at"),
        table_name="program_analytics",
    )
    op.drop_table("program_analytics")

    op.drop_index(
        op.f("ix_provider_analytics_provider_id"),
        table_name="provider_analytics",
    )
    op.drop_index(
        op.f("ix_provider_analytics_calculated_at"),
        table_name="provider_analytics",
    )
    op.drop_table("provider_analytics")

    op.drop_index(
        op.f("ix_patient_health_scores_patient_id"),
        table_name="patient_health_scores",
    )
    op.drop_index(
        op.f("ix_patient_health_scores_calculated_at"),
        table_name="patient_health_scores",
    )
    op.drop_table("patient_health_scores")
