from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.documents.enums.document_enums import (
    DocumentStatus,
    DocumentType,
)


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    document_type: DocumentType | None = None
    status: DocumentStatus | None = None


class DocumentDownloadResponse(BaseModel):
    document_id: UUID
    download_url: str
    expires_in_seconds: int


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    provider_id: UUID | None
    uploaded_by_user_id: UUID
    consultation_id: UUID | None
    lab_order_id: UUID | None
    optimization_program_id: UUID | None
    document_type: DocumentType
    title: str
    description: str | None
    file_name: str
    original_file_name: str
    mime_type: str
    file_size: int
    status: DocumentStatus
    uploaded_at: datetime
    created_at: datetime
    updated_at: datetime
    download_url: str
