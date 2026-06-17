from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db
from app.modules.auth.api.rbac import require_permissions
from app.modules.auth.constants.permissions import (
    CREATE_GOALS,
    RECORD_GOAL_PROGRESS,
    UPDATE_GOALS,
    VIEW_GOALS,
    VIEW_GOAL_PROGRESS,
)
from app.modules.auth.models.user import User
from app.modules.goals.enums.goal_enums import HealthGoalStatus
from app.modules.goals.schemas.goal_schema import (
    GoalProgressCreate,
    GoalProgressResponse,
    HealthGoalCreate,
    HealthGoalDetailResponse,
    HealthGoalResponse,
    HealthGoalUpdate,
)
from app.modules.goals.services.goal_service import HealthGoalService

router = APIRouter(
    prefix="/goals",
    tags=["Health Goals"],
)


@router.post(
    "",
    response_model=HealthGoalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_goal(
    payload: HealthGoalCreate,
    current_user: User = Depends(require_permissions(CREATE_GOALS)),
    db: AsyncSession = Depends(get_db),
):
    service = HealthGoalService(db)

    return await service.create_goal(
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[HealthGoalResponse],
)
async def get_goals(
    status: HealthGoalStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_permissions(VIEW_GOALS)),
    db: AsyncSession = Depends(get_db),
):
    service = HealthGoalService(db)

    return await service.get_goals(
        current_user=current_user,
        limit=limit,
        offset=offset,
        status=status,
    )


@router.post(
    "/progress",
    response_model=GoalProgressResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_goal_progress(
    payload: GoalProgressCreate,
    current_user: User = Depends(
        require_permissions(RECORD_GOAL_PROGRESS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = HealthGoalService(db)

    return await service.record_progress(
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/progress/{progress_id}",
    response_model=GoalProgressResponse,
)
async def get_goal_progress_by_id(
    progress_id: UUID,
    current_user: User = Depends(
        require_permissions(VIEW_GOAL_PROGRESS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = HealthGoalService(db)

    return await service.get_progress_by_id(
        progress_id=progress_id,
        current_user=current_user,
    )


@router.get(
    "/patient/{patient_id}",
    response_model=list[HealthGoalResponse],
)
async def get_patient_goals(
    patient_id: UUID,
    status: HealthGoalStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_permissions(VIEW_GOALS)),
    db: AsyncSession = Depends(get_db),
):
    service = HealthGoalService(db)

    return await service.get_patient_goals(
        patient_id=patient_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
        status=status,
    )


@router.get(
    "/{goal_id}",
    response_model=HealthGoalDetailResponse,
)
async def get_goal_by_id(
    goal_id: UUID,
    current_user: User = Depends(require_permissions(VIEW_GOALS)),
    db: AsyncSession = Depends(get_db),
):
    service = HealthGoalService(db)

    return await service.get_goal_by_id(
        goal_id=goal_id,
        current_user=current_user,
    )


@router.put(
    "/{goal_id}",
    response_model=HealthGoalResponse,
)
async def update_goal(
    goal_id: UUID,
    payload: HealthGoalUpdate,
    current_user: User = Depends(require_permissions(UPDATE_GOALS)),
    db: AsyncSession = Depends(get_db),
):
    service = HealthGoalService(db)

    return await service.update_goal(
        goal_id=goal_id,
        payload=payload,
        current_user=current_user,
    )
