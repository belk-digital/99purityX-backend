from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.optimization.enums.program_enums import (
    OptimizationProgramStatus,
)


class OptimizationProgramCreate(BaseModel):
    patient_id: UUID
    provider_id: UUID
    consultation_id: UUID
    name: str = Field(..., max_length=255)
    goal: str | None = None
    status: OptimizationProgramStatus = OptimizationProgramStatus.DRAFT
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None


class OptimizationProgramUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    goal: str | None = None
    status: OptimizationProgramStatus | None = None
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None


class OptimizationProgramResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    provider_id: UUID
    consultation_id: UUID
    name: str
    goal: str | None
    status: OptimizationProgramStatus
    start_date: date | None
    end_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
