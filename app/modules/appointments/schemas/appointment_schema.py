from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.appointments.enums.appointment_enums import (
    AppointmentStatus,
)


class AppointmentCreate(BaseModel):
    provider_id: UUID
    scheduled_start: datetime
    scheduled_end: datetime
    reason: str | None = Field(default=None, max_length=500)
    notes: str | None = None


class AppointmentUpdate(BaseModel):
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    status: AppointmentStatus | None = None
    reason: str | None = Field(default=None, max_length=500)
    notes: str | None = None


class AppointmentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    provider_id: UUID
    scheduled_start: datetime
    scheduled_end: datetime
    status: AppointmentStatus
    reason: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True