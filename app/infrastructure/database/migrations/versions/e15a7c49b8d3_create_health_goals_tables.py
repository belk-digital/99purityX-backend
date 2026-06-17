"""create health goals tables

Revision ID: e15a7c49b8d3
Revises: d84b6f2e91a5
Create Date: 2026-05-30 01:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e15a7c49b8d3"
down_revision: Union[str, None] = "d84b6f2e91a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "health_goals",
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("provider_id", sa.UUID(), nullable=False),
        sa.Column("consultation_id", sa.UUID(), nullable=False),
        sa.Column("program_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "category",
            sa.Enum(
                "WEIGHT_LOSS",
                "MUSCLE_GAIN",
                "METABOLIC_HEALTH",
                "HORMONE_HEALTH",
                "SLEEP",
                "RECOVERY",
                "CARDIOVASCULAR",
                "LONGEVITY",
                "BIOMARKER",
                "CUSTOM",
                name="goalcategory",
            ),
            nullable=False,
        ),
        sa.Column("target_value", sa.Numeric(12, 4), nullable=False),
        sa.Column("current_value", sa.Numeric(12, 4), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("start_value", sa.Numeric(12, 4), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "ACHIEVED",
                "PAUSED",
                "CANCELLED",
                name="healthgoalstatus",
            ),
            nullable=False,
        ),
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
        op.f("ix_health_goals_category"),
        "health_goals",
        ["category"],
        unique=False,
    )
    op.create_index(
        op.f("ix_health_goals_consultation_id"),
        "health_goals",
        ["consultation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_health_goals_patient_id"),
        "health_goals",
        ["patient_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_health_goals_program_id"),
        "health_goals",
        ["program_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_health_goals_provider_id"),
        "health_goals",
        ["provider_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_health_goals_status"),
        "health_goals",
        ["status"],
        unique=False,
    )

    op.create_table(
        "goal_progress",
        sa.Column("goal_id", sa.UUID(), nullable=False),
        sa.Column("value", sa.Numeric(12, 4), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["goal_id"],
            ["health_goals.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_goal_progress_goal_id"),
        "goal_progress",
        ["goal_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_goal_progress_recorded_at"),
        "goal_progress",
        ["recorded_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_goal_progress_recorded_at"),
        table_name="goal_progress",
    )
    op.drop_index(
        op.f("ix_goal_progress_goal_id"),
        table_name="goal_progress",
    )
    op.drop_table("goal_progress")

    op.drop_index(
        op.f("ix_health_goals_status"),
        table_name="health_goals",
    )
    op.drop_index(
        op.f("ix_health_goals_provider_id"),
        table_name="health_goals",
    )
    op.drop_index(
        op.f("ix_health_goals_program_id"),
        table_name="health_goals",
    )
    op.drop_index(
        op.f("ix_health_goals_patient_id"),
        table_name="health_goals",
    )
    op.drop_index(
        op.f("ix_health_goals_consultation_id"),
        table_name="health_goals",
    )
    op.drop_index(
        op.f("ix_health_goals_category"),
        table_name="health_goals",
    )
    op.drop_table("health_goals")
    op.execute("DROP TYPE IF EXISTS healthgoalstatus")
    op.execute("DROP TYPE IF EXISTS goalcategory")
