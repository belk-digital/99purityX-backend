from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.optimization.enums.program_enums import (
    HabitFrequency,
    HabitProtocolStatus,
)


class HabitProtocolCreate(BaseModel):
    program_id: UUID
    patient_id: UUID
    provider_id: UUID
    title: str = Field(..., max_length=255)
    description: str | None = None
    target_value: Decimal | None = None
    target_unit: str | None = Field(default=None, max_length=50)
    frequency: HabitFrequency = HabitFrequency.DAILY
    status: HabitProtocolStatus = HabitProtocolStatus.ACTIVE
    notes: str | None = None


class HabitProtocolUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    target_value: Decimal | None = None
    target_unit: str | None = Field(default=None, max_length=50)
    frequency: HabitFrequency | None = None
    status: HabitProtocolStatus | None = None
    notes: str | None = None


class HabitProtocolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    program_id: UUID
    patient_id: UUID
    provider_id: UUID
    title: str
    description: str | None
    target_value: Decimal | None
    target_unit: str | None
    frequency: HabitFrequency
    status: HabitProtocolStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime


class HabitLogCreate(BaseModel):
    habit_protocol_id: UUID
    date: date
    actual_value: Decimal | None = None
    completed: bool = False
    notes: str | None = None


class HabitLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    habit_protocol_id: UUID
    patient_id: UUID
    date: date
    actual_value: Decimal | None
    completed: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime
