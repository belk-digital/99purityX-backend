from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.labs.enums.lab_enums import LabOrderStatus


class LabOrderCreate(BaseModel):
    patient_id: UUID
    provider_id: UUID
    consultation_id: UUID
    lab_name: str = Field(..., max_length=255)
    notes: str | None = None
    ordered_at: datetime | None = None


class LabOrderUpdate(BaseModel):
    lab_name: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    status: LabOrderStatus | None = None
    completed_at: datetime | None = None


class LabResultCreate(BaseModel):
    lab_order_id: UUID
    biomarker_name: str = Field(..., max_length=255)
    value: Decimal
    unit: str | None = Field(default=None, max_length=50)
    reference_min: Decimal | None = None
    reference_max: Decimal | None = None
    notes: str | None = None
    recorded_at: datetime | None = None


class LabResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lab_order_id: UUID
    biomarker_name: str
    value: Decimal
    unit: str | None
    reference_min: Decimal | None
    reference_max: Decimal | None
    notes: str | None
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime


class LabOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    provider_id: UUID
    consultation_id: UUID
    lab_name: str
    notes: str | None
    status: LabOrderStatus
    ordered_at: datetime
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class LabOrderDetailResponse(LabOrderResponse):
    results: list[LabResultResponse] = Field(default_factory=list)
