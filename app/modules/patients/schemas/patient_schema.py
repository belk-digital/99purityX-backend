from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PatientBaseSchema(BaseModel):
    date_of_birth: date | None = None
    gender: str | None = None
    phone_number: str | None = None
    blood_group: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    timezone: str | None = None
    preferred_language: str | None = None


class PatientUpdateSchema(
    PatientBaseSchema
):
    pass


class PatientResponseSchema(
    PatientBaseSchema
):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )