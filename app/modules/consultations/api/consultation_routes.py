import os
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant

from app.infrastructure.database.session import (
    get_db,
)

from app.modules.auth.api.dependencies import (
    get_current_user,
)

from app.modules.consultations.enums.consultation_enums import (
    ConsultationStatus,
)

from app.modules.consultations.schemas.consultation_schema import (
    ConsultationCreate,
    ConsultationResponse,
    ConsultationUpdate,
    VideoTokenResponse,
)

from app.modules.consultations.services.consultation_service import (
    ConsultationService,
)

router = APIRouter(
    prefix="/consultations",
    tags=["Consultations"],
)


@router.post(
    "",
    response_model=ConsultationResponse,
)
async def create_consultation(
    payload: ConsultationCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):

    service = ConsultationService(db)

    return await service.create_consultation(
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/me",
    response_model=list[
        ConsultationResponse
    ],
)
async def get_my_consultations(
    status: ConsultationStatus | None = Query(
        default=None,
        description="Filter by consultation status",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):

    service = ConsultationService(db)

    return await service.get_my_consultations(
        current_user=current_user,
        limit=limit,
        offset=offset,
        status=status,
    )


@router.get(
    "/{consultation_id}",
    response_model=ConsultationResponse,
)
async def get_consultation_by_id(
    consultation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):

    service = ConsultationService(db)

    return await service.get_consultation_by_id(
        consultation_id=consultation_id,
        current_user=current_user,
    )


@router.put(
    "/{consultation_id}",
    response_model=ConsultationResponse,
)
async def update_consultation(
    consultation_id: UUID,
    payload: ConsultationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):

    service = ConsultationService(db)

    return await service.update_consultation(
        consultation_id=consultation_id,
        payload=payload,
        current_user=current_user,
    )


@router.post(
    "/{consultation_id}/video-token",
    response_model=VideoTokenResponse,
)
async def get_video_token(
    consultation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    api_key_sid = os.getenv("TWILIO_API_KEY_SID", "")
    api_key_secret = os.getenv("TWILIO_API_KEY_SECRET", "")

    if not all([account_sid, api_key_sid, api_key_secret]) or account_sid.startswith("AC" + "x"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Video service not configured. Add Twilio credentials to .env",
        )

    # Verify the consultation exists and the user has access
    service = ConsultationService(db)
    consultation = await service.get_consultation_by_id(
        consultation_id=consultation_id,
        current_user=current_user,
    )

    room_name = f"consultation-{consultation.id}"
    identity = str(current_user.id)

    token = AccessToken(
        account_sid,
        api_key_sid,
        api_key_secret,
        identity=identity,
        ttl=3600,
    )
    token.add_grant(VideoGrant(room=room_name))

    return VideoTokenResponse(
        token=token.to_jwt(),
        room_name=room_name,
        identity=identity,
    )