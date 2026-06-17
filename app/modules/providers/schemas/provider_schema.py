from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProviderBase(BaseModel):
    provider_type: str = Field(..., max_length=50)
    speciality: str | None = Field(default=None, max_length=120)
    license_number: str | None = Field(default=None, max_length=120)
    years_experience: int | None = None
    bio: str | None = None
    consultation_fee: Decimal | None = None
    
class ProviderCreateSchema(BaseModel):

    user_id: UUID
    provider_type: str
    speciality: str
    license_number: str | None = None
    years_experience: int | None = None
    bio: str | None = None
    consultation_fee: float | None = None


class ProviderUpdateSchema(BaseModel):
    speciality: str | None = None
    years_experience: int | None = None
    bio: str | None = None
    consultation_fee: Decimal | None = None


class ProviderResponseSchema(ProviderBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class ProviderListResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider_type: str
    speciality: str | None
    years_experience: int | None
    consultation_fee: Decimal | None