from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db
from app.modules.auth.api.rbac import require_permissions
from app.modules.auth.constants.permissions import (
    CREATE_OPTIMIZATION_PROGRAMS,
    UPDATE_OPTIMIZATION_PROGRAMS,
    VIEW_OPTIMIZATION_PROGRAMS,
)
from app.modules.auth.models.user import User
from app.modules.optimization.enums.program_enums import (
    OptimizationProgramStatus,
)
from app.modules.optimization.schemas.program_schema import (
    OptimizationProgramCreate,
    OptimizationProgramResponse,
    OptimizationProgramUpdate,
)
from app.modules.optimization.services.program_service import (
    OptimizationProgramService,
)

router = APIRouter(
    prefix="/optimization",
    tags=["Optimization Programs"],
)


@router.post(
    "/programs",
    response_model=OptimizationProgramResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_optimization_program(
    payload: OptimizationProgramCreate,
    current_user: User = Depends(
        require_permissions(CREATE_OPTIMIZATION_PROGRAMS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = OptimizationProgramService(db)

    return await service.create_program(
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/programs",
    response_model=list[OptimizationProgramResponse],
)
async def get_optimization_programs(
    status: OptimizationProgramStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(
        require_permissions(VIEW_OPTIMIZATION_PROGRAMS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = OptimizationProgramService(db)

    return await service.get_programs(
        current_user=current_user,
        limit=limit,
        offset=offset,
        status=status,
    )


@router.get(
    "/programs/{program_id}",
    response_model=OptimizationProgramResponse,
)
async def get_optimization_program_by_id(
    program_id: UUID,
    current_user: User = Depends(
        require_permissions(VIEW_OPTIMIZATION_PROGRAMS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = OptimizationProgramService(db)

    return await service.get_program_by_id(
        program_id=program_id,
        current_user=current_user,
    )


@router.put(
    "/programs/{program_id}",
    response_model=OptimizationProgramResponse,
)
async def update_optimization_program(
    program_id: UUID,
    payload: OptimizationProgramUpdate,
    current_user: User = Depends(
        require_permissions(UPDATE_OPTIMIZATION_PROGRAMS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = OptimizationProgramService(db)

    return await service.update_program(
        program_id=program_id,
        payload=payload,
        current_user=current_user,
    )
