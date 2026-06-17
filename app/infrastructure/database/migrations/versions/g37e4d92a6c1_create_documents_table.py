"""create documents table

Revision ID: g37e4d92a6c1
Revises: f26c9a80d5b7
Create Date: 2026-05-30 02:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "g37e4d92a6c1"
down_revision: Union[str, None] = "f26c9a80d5b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("provider_id", sa.UUID(), nullable=True),
        sa.Column("uploaded_by_user_id", sa.UUID(), nullable=False),
        sa.Column("consultation_id", sa.UUID(), nullable=True),
        sa.Column("lab_order_id", sa.UUID(), nullable=True),
        sa.Column("optimization_program_id", sa.UUID(), nullable=True),
        sa.Column(
            "document_type",
            sa.Enum(
                "LAB_REPORT",
                "PRESCRIPTION",
                "CONSULTATION_ATTACHMENT",
                "MEDICAL_RECORD",
                "INSURANCE_DOCUMENT",
                "CONSENT_FORM",
                "OPTIMIZATION_PROGRAM_DOCUMENT",
                "PROGRESS_REPORT",
                "OTHER",
                name="documenttype",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("original_file_name", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=255), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "ARCHIVED",
                "DELETED",
                name="documentstatus",
            ),
            nullable=False,
        ),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["consultation_id"],
            ["consultations.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["lab_order_id"],
            ["lab_orders.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["optimization_program_id"],
            ["optimization_programs.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["provider_id"],
            ["providers.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by_user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index(
        op.f("ix_documents_consultation_id"),
        "documents",
        ["consultation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_document_type"),
        "documents",
        ["document_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_lab_order_id"),
        "documents",
        ["lab_order_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_optimization_program_id"),
        "documents",
        ["optimization_program_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_patient_id"),
        "documents",
        ["patient_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_provider_id"),
        "documents",
        ["provider_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_status"),
        "documents",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_uploaded_at"),
        "documents",
        ["uploaded_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_uploaded_by_user_id"),
        "documents",
        ["uploaded_by_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_documents_uploaded_by_user_id"),
        table_name="documents",
    )
    op.drop_index(
        op.f("ix_documents_uploaded_at"),
        table_name="documents",
    )
    op.drop_index(
        op.f("ix_documents_status"),
        table_name="documents",
    )
    op.drop_index(
        op.f("ix_documents_provider_id"),
        table_name="documents",
    )
    op.drop_index(
        op.f("ix_documents_patient_id"),
        table_name="documents",
    )
    op.drop_index(
        op.f("ix_documents_optimization_program_id"),
        table_name="documents",
    )
    op.drop_index(
        op.f("ix_documents_lab_order_id"),
        table_name="documents",
    )
    op.drop_index(
        op.f("ix_documents_document_type"),
        table_name="documents",
    )
    op.drop_index(
        op.f("ix_documents_consultation_id"),
        table_name="documents",
    )
    op.drop_table("documents")
    op.execute("DROP TYPE IF EXISTS documentstatus")
    op.execute("DROP TYPE IF EXISTS documenttype")
