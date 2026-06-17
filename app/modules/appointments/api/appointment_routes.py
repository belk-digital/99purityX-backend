from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import (
    get_db,
)

from app.modules.auth.api.dependencies import (
    get_current_user,
)

from app.modules.auth.models.user import User

from app.modules.appointments.repositories.appointment_repository import (
    AppointmentRepository,
)

from app.modules.appointments.schemas.appointment_schema import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)

from app.modules.appointments.services.appointment_service import (
    AppointmentService,
)

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment(
    payload: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    # ONLY PATIENTS CAN CREATE APPOINTMENTS
    if not current_user.patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only patients can create appointments"
            ),
        )

    service = AppointmentService()

    return await service.create_appointment(
        db=db,
        patient_id=current_user.patient.id,
        data=payload,
        actor_user_id=current_user.id,
    )


@router.get(
    "/me",
    response_model=list[AppointmentResponse],
)
async def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    repository = AppointmentRepository(db)

    # PROVIDER APPOINTMENTS (check first — providers also have a patient record from registration)
    if current_user.provider_profile:

        return await repository.get_provider_appointments(
            current_user.provider_profile.id,
        )

    # PATIENT APPOINTMENTS
    if current_user.patient:

        return await repository.get_patient_appointments(
            current_user.patient.id,
        )

    return []


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
async def get_appointment(
    appointment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = AppointmentService()

    appointment = await service.get_appointment(
        db=db,
        appointment_id=appointment_id,
    )

    # OWNERSHIP VALIDATION
    await service.validate_appointment_access(
        appointment=appointment,
        current_user=current_user,
    )

    return appointment


@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
async def update_appointment(
    appointment_id: UUID,
    payload: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = AppointmentService()

    appointment = await service.get_appointment(
        db=db,
        appointment_id=appointment_id,
    )

    # OWNERSHIP VALIDATION
    await service.validate_appointment_access(
        appointment=appointment,
        current_user=current_user,
    )

    updated_appointment = (
        await service.update_appointment(
            db=db,
            appointment=appointment,
            data=payload,
            actor_user_id=current_user.id,
        )
    )

    return updated_appointment