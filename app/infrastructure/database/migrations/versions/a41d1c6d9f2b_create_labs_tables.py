"""create labs tables

Revision ID: a41d1c6d9f2b
Revises: f45f94415e4f
Create Date: 2026-05-29 23:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a41d1c6d9f2b"
down_revision: Union[str, None] = "f45f94415e4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lab_orders",
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("provider_id", sa.UUID(), nullable=False),
        sa.Column("consultation_id", sa.UUID(), nullable=False),
        sa.Column("lab_name", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "ORDERED",
                "SAMPLE_COLLECTED",
                "COMPLETED",
                "CANCELLED",
                name="laborderstatus",
            ),
            nullable=False,
        ),
        sa.Column("ordered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
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
        op.f("ix_lab_orders_consultation_id"),
        "lab_orders",
        ["consultation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_lab_orders_patient_id"),
        "lab_orders",
        ["patient_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_lab_orders_provider_id"),
        "lab_orders",
        ["provider_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_lab_orders_status"),
        "lab_orders",
        ["status"],
        unique=False,
    )

    op.create_table(
        "lab_results",
        sa.Column("lab_order_id", sa.UUID(), nullable=False),
        sa.Column("biomarker_name", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Numeric(12, 4), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("reference_min", sa.Numeric(12, 4), nullable=True),
        sa.Column("reference_max", sa.Numeric(12, 4), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["lab_order_id"],
            ["lab_orders.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_lab_results_biomarker_name"),
        "lab_results",
        ["biomarker_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_lab_results_lab_order_id"),
        "lab_results",
        ["lab_order_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_lab_results_lab_order_id"),
        table_name="lab_results",
    )
    op.drop_index(
        op.f("ix_lab_results_biomarker_name"),
        table_name="lab_results",
    )
    op.drop_table("lab_results")

    op.drop_index(
        op.f("ix_lab_orders_status"),
        table_name="lab_orders",
    )
    op.drop_index(
        op.f("ix_lab_orders_provider_id"),
        table_name="lab_orders",
    )
    op.drop_index(
        op.f("ix_lab_orders_patient_id"),
        table_name="lab_orders",
    )
    op.drop_index(
        op.f("ix_lab_orders_consultation_id"),
        table_name="lab_orders",
    )
    op.drop_table("lab_orders")
    op.execute("DROP TYPE IF EXISTS laborderstatus")
