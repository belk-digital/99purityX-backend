from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.optimization.enums.program_enums import (
    PeptideProtocolStatus,
    PeptideRoute,
)


class PeptideProtocolCreate(BaseModel):
    program_id: UUID
    patient_id: UUID
    provider_id: UUID
    peptide_name: str = Field(..., max_length=255)
    purpose: str | None = None
    dosage: str = Field(..., max_length=255)
    frequency: str = Field(..., max_length=255)
    route: PeptideRoute
    status: PeptideProtocolStatus = PeptideProtocolStatus.PLANNED
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None


class PeptideProtocolUpdate(BaseModel):
    peptide_name: str | None = Field(default=None, max_length=255)
    purpose: str | None = None
    dosage: str | None = Field(default=None, max_length=255)
    frequency: str | None = Field(default=None, max_length=255)
    route: PeptideRoute | None = None
    status: PeptideProtocolStatus | None = None
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None


class PeptideProtocolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    program_id: UUID
    patient_id: UUID
    provider_id: UUID
    peptide_name: str
    purpose: str | None
    dosage: str
    frequency: str
    route: PeptideRoute
    status: PeptideProtocolStatus
    start_date: date | None
    end_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
