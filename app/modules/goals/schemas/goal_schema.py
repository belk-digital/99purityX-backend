from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.goals.enums.goal_enums import (
    GoalCategory,
    HealthGoalStatus,
)


class HealthGoalCreate(BaseModel):
    patient_id: UUID
    provider_id: UUID
    consultation_id: UUID
    program_id: UUID
    title: str = Field(..., max_length=255)
    description: str | None = None
    category: GoalCategory
    target_value: Decimal
    current_value: Decimal | None = None
    unit: str | None = Field(default=None, max_length=50)
    start_value: Decimal | None = None
    target_date: date | None = None
    status: HealthGoalStatus = HealthGoalStatus.ACTIVE
    notes: str | None = None


class HealthGoalUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    category: GoalCategory | None = None
    target_value: Decimal | None = None
    current_value: Decimal | None = None
    unit: str | None = Field(default=None, max_length=50)
    start_value: Decimal | None = None
    target_date: date | None = None
    status: HealthGoalStatus | None = None
    notes: str | None = None


class GoalProgressCreate(BaseModel):
    goal_id: UUID
    value: Decimal
    notes: str | None = None
    recorded_at: datetime | None = None


class GoalProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    goal_id: UUID
    value: Decimal
    notes: str | None
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime


class HealthGoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    provider_id: UUID
    consultation_id: UUID
    program_id: UUID
    title: str
    description: str | None
    category: GoalCategory
    target_value: Decimal
    current_value: Decimal | None
    unit: str | None
    start_value: Decimal | None
    target_date: date | None
    status: HealthGoalStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime


class HealthGoalDetailResponse(HealthGoalResponse):
    progress_records: list[GoalProgressResponse] = Field(default_factory=list)
