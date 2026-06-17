from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.modules.consultations.enums.consultation_enums import (
    ConsultationStatus,
)


class ConsultationCreate(BaseModel):
    appointment_id: UUID
    started_at: datetime
    chief_complaint: str | None = None
    provider_notes: str | None = None


class ConsultationUpdate(BaseModel):
    ended_at: datetime | None = None
    status: ConsultationStatus | None = None
    provider_notes: str | None = None
    summary: str | None = None
    follow_up_required: bool | None = None


class ConsultationResponse(BaseModel):
    id: UUID
    appointment_id: UUID
    patient_id: UUID
    provider_id: UUID

    started_at: datetime
    ended_at: datetime | None

    status: ConsultationStatus

    chief_complaint: str | None
    provider_notes: str | None
    summary: str | None

    follow_up_required: bool

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoTokenResponse(BaseModel):
    token: str
    room_name: str
    identity: str