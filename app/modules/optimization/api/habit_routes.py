from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db
from app.modules.auth.api.rbac import require_permissions
from app.modules.auth.constants.permissions import (
    CREATE_HABIT_LOGS,
    CREATE_OPTIMIZATION_HABITS,
    UPDATE_OPTIMIZATION_HABITS,
    VIEW_HABIT_LOGS,
    VIEW_OPTIMIZATION_HABITS,
)
from app.modules.auth.models.user import User
from app.modules.optimization.enums.program_enums import HabitProtocolStatus
from app.modules.optimization.schemas.habit_schema import (
    HabitLogCreate,
    HabitLogResponse,
    HabitProtocolCreate,
    HabitProtocolResponse,
    HabitProtocolUpdate,
)
from app.modules.optimization.services.habit_service import HabitService

router = APIRouter(
    prefix="/optimization",
    tags=["Optimization Habits"],
)


@router.post(
    "/habits",
    response_model=HabitProtocolResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_habit(
    payload: HabitProtocolCreate,
    current_user: User = Depends(
        require_permissions(CREATE_OPTIMIZATION_HABITS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = HabitService(db)

    return await service.create_habit(
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/habits",
    response_model=list[HabitProtocolResponse],
)
async def get_habits(
    status: HabitProtocolStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(
        require_permissions(VIEW_OPTIMIZATION_HABITS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = HabitService(db)

    return await service.get_habits(
        current_user=current_user,
        limit=limit,
        offset=offset,
        status=status,
    )


@router.get(
    "/habits/{habit_id}",
    response_model=HabitProtocolResponse,
)
async def get_habit_by_id(
    habit_id: UUID,
    current_user: User = Depends(
        require_permissions(VIEW_OPTIMIZATION_HABITS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = HabitService(db)

    return await service.get_habit_by_id(
        habit_id=habit_id,
        current_user=current_user,
    )


@router.put(
    "/habits/{habit_id}",
    response_model=HabitProtocolResponse,
)
async def update_habit(
    habit_id: UUID,
    payload: HabitProtocolUpdate,
    current_user: User = Depends(
        require_permissions(UPDATE_OPTIMIZATION_HABITS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = HabitService(db)

    return await service.update_habit(
        habit_id=habit_id,
        payload=payload,
        current_user=current_user,
    )


@router.post(
    "/habit-logs",
    response_model=HabitLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_habit_log(
    payload: HabitLogCreate,
    current_user: User = Depends(require_permissions(CREATE_HABIT_LOGS)),
    db: AsyncSession = Depends(get_db),
):
    service = HabitService(db)

    return await service.create_habit_log(
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/habit-logs",
    response_model=list[HabitLogResponse],
)
async def get_habit_logs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_permissions(VIEW_HABIT_LOGS)),
    db: AsyncSession = Depends(get_db),
):
    service = HabitService(db)

    return await service.get_habit_logs(
        current_user=current_user,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/habit-logs/{log_id}",
    response_model=HabitLogResponse,
)
async def get_habit_log_by_id(
    log_id: UUID,
    current_user: User = Depends(require_permissions(VIEW_HABIT_LOGS)),
    db: AsyncSession = Depends(get_db),
):
    service = HabitService(db)

    return await service.get_habit_log_by_id(
        log_id=log_id,
        current_user=current_user,
    )


@router.get(
    "/patient/{patient_id}/habits",
    response_model=list[HabitProtocolResponse],
)
async def get_patient_habits(
    patient_id: UUID,
    status: HabitProtocolStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(
        require_permissions(VIEW_OPTIMIZATION_HABITS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = HabitService(db)

    return await service.get_patient_habits(
        patient_id=patient_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
        status=status,
    )
