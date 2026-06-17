from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db
from app.modules.auth.api.rbac import require_permissions
from app.modules.auth.constants.permissions import (
    CREATE_PEPTIDE_PROTOCOLS,
    UPDATE_PEPTIDE_PROTOCOLS,
    VIEW_PEPTIDE_PROTOCOLS,
)
from app.modules.auth.models.user import User
from app.modules.optimization.enums.program_enums import PeptideProtocolStatus
from app.modules.optimization.schemas.peptide_schema import (
    PeptideProtocolCreate,
    PeptideProtocolResponse,
    PeptideProtocolUpdate,
)
from app.modules.optimization.services.peptide_service import (
    PeptideProtocolService,
)

router = APIRouter(
    prefix="/optimization",
    tags=["Peptide Protocols"],
)


@router.post(
    "/peptides",
    response_model=PeptideProtocolResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_peptide_protocol(
    payload: PeptideProtocolCreate,
    current_user: User = Depends(
        require_permissions(CREATE_PEPTIDE_PROTOCOLS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = PeptideProtocolService(db)

    return await service.create_protocol(
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/peptides",
    response_model=list[PeptideProtocolResponse],
)
async def get_peptide_protocols(
    status: PeptideProtocolStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(
        require_permissions(VIEW_PEPTIDE_PROTOCOLS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = PeptideProtocolService(db)

    return await service.get_protocols(
        current_user=current_user,
        limit=limit,
        offset=offset,
        status=status,
    )


@router.get(
    "/peptides/{protocol_id}",
    response_model=PeptideProtocolResponse,
)
async def get_peptide_protocol_by_id(
    protocol_id: UUID,
    current_user: User = Depends(
        require_permissions(VIEW_PEPTIDE_PROTOCOLS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = PeptideProtocolService(db)

    return await service.get_protocol_by_id(
        protocol_id=protocol_id,
        current_user=current_user,
    )


@router.put(
    "/peptides/{protocol_id}",
    response_model=PeptideProtocolResponse,
)
async def update_peptide_protocol(
    protocol_id: UUID,
    payload: PeptideProtocolUpdate,
    current_user: User = Depends(
        require_permissions(UPDATE_PEPTIDE_PROTOCOLS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = PeptideProtocolService(db)

    return await service.update_protocol(
        protocol_id=protocol_id,
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/patient/{patient_id}/peptides",
    response_model=list[PeptideProtocolResponse],
)
async def get_patient_peptide_protocols(
    patient_id: UUID,
    status: PeptideProtocolStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(
        require_permissions(VIEW_PEPTIDE_PROTOCOLS)
    ),
    db: AsyncSession = Depends(get_db),
):
    service = PeptideProtocolService(db)

    return await service.get_patient_protocols(
        patient_id=patient_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
        status=status,
    )
