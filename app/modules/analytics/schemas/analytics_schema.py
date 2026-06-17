from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PatientHealthScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    overall_score: Decimal
    adherence_score: Decimal
    biomarker_score: Decimal
    goal_score: Decimal
    calculated_at: datetime


class ProviderAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider_id: UUID
    active_patients: int
    active_programs: int
    completed_goals: int
    average_adherence: Decimal
    average_health_score: Decimal
    calculated_at: datetime


class ProgramAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    program_id: UUID
    enrolled_patients: int
    average_adherence: Decimal
    goal_completion_rate: Decimal
    average_health_score: Decimal
    calculated_at: datetime


class PatientAnalyticsResponse(BaseModel):
    health_score: PatientHealthScoreResponse
    active_programs: int
    active_goals: int
    completed_goals: int
    habit_logs: int
    completed_habit_logs: int
