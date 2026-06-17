from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import (
    get_db,
)

from app.modules.auth.api.dependencies import (
    get_current_user,
)

from app.modules.auth.api.rbac import (
    require_permissions,
)

from app.modules.auth.constants.permissions import (
    MANAGE_USERS,
)

from app.modules.patients.schemas.patient_schema import (
    PatientResponseSchema,
    PatientUpdateSchema,
)

from app.modules.patients.services.patient_service import (
    PatientService,
)

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.get(
    "/me",
    response_model=PatientResponseSchema,
)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    service = PatientService(db)

    patient = (
        await service.get_my_profile(
            current_user.id
        )
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found",
        )

    return patient


@router.put(
    "/me",
    response_model=PatientResponseSchema,
)
async def update_my_profile(
    payload: PatientUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    service = PatientService(db)

    try:
        return await service.update_my_profile(
            current_user.id,
            payload,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@router.get(
    "/{patient_id}",
    response_model=PatientResponseSchema,
)
async def get_patient_by_id(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        require_permissions(
            MANAGE_USERS
        )
    ),
):
    service = PatientService(db)

    patient = (
        await service.get_patient_by_id(
            patient_id
        )
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    return patient