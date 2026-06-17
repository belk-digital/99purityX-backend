from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db
from app.modules.analytics.schemas.analytics_schema import (
    PatientAnalyticsResponse,
    PatientHealthScoreResponse,
    ProgramAnalyticsResponse,
    ProviderAnalyticsResponse,
)
from app.modules.analytics.services.analytics_service import AnalyticsService
from app.modules.auth.api.rbac import require_permissions
from app.modules.auth.constants.permissions import VIEW_ANALYTICS
from app.modules.auth.models.user import User

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/patient/{patient_id}",
    response_model=PatientAnalyticsResponse,
)
async def get_patient_analytics(
    patient_id: UUID,
    current_user: User = Depends(require_permissions(VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)

    return await service.get_patient_analytics(
        patient_id=patient_id,
        current_user=current_user,
    )


@router.get(
    "/provider/{provider_id}",
    response_model=ProviderAnalyticsResponse,
)
async def get_provider_analytics(
    provider_id: UUID,
    current_user: User = Depends(require_permissions(VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)

    return await service.calculate_provider_analytics(
        provider_id=provider_id,
        current_user=current_user,
    )


@router.get(
    "/program/{program_id}",
    response_model=ProgramAnalyticsResponse,
)
async def get_program_analytics(
    program_id: UUID,
    current_user: User = Depends(require_permissions(VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)

    return await service.calculate_program_analytics(
        program_id=program_id,
        current_user=current_user,
    )


@router.get(
    "/health-score/{patient_id}",
    response_model=PatientHealthScoreResponse,
)
async def get_patient_health_score(
    patient_id: UUID,
    current_user: User = Depends(require_permissions(VIEW_ANALYTICS)),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)

    return await service.calculate_patient_health_score(
        patient_id=patient_id,
        current_user=current_user,
    )
