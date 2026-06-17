from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db
from app.modules.auth.api.rbac import require_permissions
from app.modules.auth.constants.permissions import (
    CREATE_LAB_ORDERS,
    CREATE_LAB_RESULTS,
    UPDATE_LAB_ORDERS,
    VIEW_LABS,
)
from app.modules.auth.models.user import User
from app.modules.labs.enums.lab_enums import LabOrderStatus
from app.modules.labs.schemas.lab_schema import (
    LabOrderCreate,
    LabOrderDetailResponse,
    LabOrderResponse,
    LabOrderUpdate,
    LabResultCreate,
    LabResultResponse,
)
from app.modules.labs.services.lab_service import LabService

router = APIRouter(
    prefix="/labs",
    tags=["Labs"],
)


@router.post(
    "/orders",
    response_model=LabOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_lab_order(
    payload: LabOrderCreate,
    current_user: User = Depends(
        require_permissions(CREATE_LAB_ORDERS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = LabService(db)

    return await service.create_lab_order(
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/orders",
    response_model=list[LabOrderResponse],
)
async def get_lab_orders(
    status: LabOrderStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_permissions(VIEW_LABS)),
    db: AsyncSession = Depends(get_db),
):
    service = LabService(db)

    return await service.get_lab_orders(
        current_user=current_user,
        limit=limit,
        offset=offset,
        status=status,
    )


@router.get(
    "/orders/{lab_order_id}",
    response_model=LabOrderDetailResponse,
)
async def get_lab_order_by_id(
    lab_order_id: UUID,
    current_user: User = Depends(require_permissions(VIEW_LABS)),
    db: AsyncSession = Depends(get_db),
):
    service = LabService(db)

    return await service.get_lab_order_by_id(
        lab_order_id=lab_order_id,
        current_user=current_user,
    )


@router.put(
    "/orders/{lab_order_id}",
    response_model=LabOrderResponse,
)
async def update_lab_order(
    lab_order_id: UUID,
    payload: LabOrderUpdate,
    current_user: User = Depends(
        require_permissions(UPDATE_LAB_ORDERS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = LabService(db)

    return await service.update_lab_order(
        lab_order_id=lab_order_id,
        payload=payload,
        current_user=current_user,
    )


@router.post(
    "/results",
    response_model=LabResultResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_lab_result(
    payload: LabResultCreate,
    current_user: User = Depends(
        require_permissions(CREATE_LAB_RESULTS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = LabService(db)

    return await service.create_lab_result(
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/results/{lab_result_id}",
    response_model=LabResultResponse,
)
async def get_lab_result_by_id(
    lab_result_id: UUID,
    current_user: User = Depends(require_permissions(VIEW_LABS)),
    db: AsyncSession = Depends(get_db),
):
    service = LabService(db)

    return await service.get_lab_result_by_id(
        lab_result_id=lab_result_id,
        current_user=current_user,
    )


@router.get(
    "/patient/{patient_id}",
    response_model=list[LabOrderDetailResponse],
)
async def get_patient_labs(
    patient_id: UUID,
    status: LabOrderStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_permissions(VIEW_LABS)),
    db: AsyncSession = Depends(get_db),
):
    service = LabService(db)

    return await service.get_patient_labs(
        patient_id=patient_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
        status=status,
    )
