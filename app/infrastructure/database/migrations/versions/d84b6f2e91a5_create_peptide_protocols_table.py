"""create peptide protocols table

Revision ID: d84b6f2e91a5
Revises: c73f18a9d4e2
Create Date: 2026-05-30 01:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d84b6f2e91a5"
down_revision: Union[str, None] = "c73f18a9d4e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "peptide_protocols",
        sa.Column("program_id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("provider_id", sa.UUID(), nullable=False),
        sa.Column("peptide_name", sa.String(length=255), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column("dosage", sa.String(length=255), nullable=False),
        sa.Column("frequency", sa.String(length=255), nullable=False),
        sa.Column(
            "route",
            sa.Enum(
                "SUBCUTANEOUS",
                "INTRAMUSCULAR",
                "ORAL",
                "TOPICAL",
                "INTRAVENOUS",
                name="peptideroute",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "PLANNED",
                "ACTIVE",
                "PAUSED",
                "COMPLETED",
                "CANCELLED",
                name="peptideprotocolstatus",
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
        op.f("ix_peptide_protocols_patient_id"),
        "peptide_protocols",
        ["patient_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_peptide_protocols_peptide_name"),
        "peptide_protocols",
        ["peptide_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_peptide_protocols_program_id"),
        "peptide_protocols",
        ["program_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_peptide_protocols_provider_id"),
        "peptide_protocols",
        ["provider_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_peptide_protocols_route"),
        "peptide_protocols",
        ["route"],
        unique=False,
    )
    op.create_index(
        op.f("ix_peptide_protocols_status"),
        "peptide_protocols",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_peptide_protocols_status"),
        table_name="peptide_protocols",
    )
    op.drop_index(
        op.f("ix_peptide_protocols_route"),
        table_name="peptide_protocols",
    )
    op.drop_index(
        op.f("ix_peptide_protocols_provider_id"),
        table_name="peptide_protocols",
    )
    op.drop_index(
        op.f("ix_peptide_protocols_program_id"),
        table_name="peptide_protocols",
    )
    op.drop_index(
        op.f("ix_peptide_protocols_peptide_name"),
        table_name="peptide_protocols",
    )
    op.drop_index(
        op.f("ix_peptide_protocols_patient_id"),
        table_name="peptide_protocols",
    )
    op.drop_table("peptide_protocols")
    op.execute("DROP TYPE IF EXISTS peptideprotocolstatus")
    op.execute("DROP TYPE IF EXISTS peptideroute")
