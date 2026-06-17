from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.modules.auth.models.otp_verification import (
    OTPVerification,
)


class OTPRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        otp: OTPVerification,
    ):
        self.db.add(otp)

        await self.db.commit()

        await self.db.refresh(otp)

        return otp

    async def get_latest_otp(
        self,
        email: str,
        purpose: str,
    ):
        result = await self.db.execute(
            select(OTPVerification)
            .where(
                OTPVerification.email == email,
                OTPVerification.purpose == purpose,
                OTPVerification.is_used.is_(False),
            )
            .order_by(
                OTPVerification.created_at.desc()
            )
        )

        return result.scalars().first()

    async def update(
        self,
        otp: OTPVerification,
    ):
        await self.db.commit()

        await self.db.refresh(otp)

        return otp
    
    async def invalidate_existing_otps(
        self,
        email: str,
        purpose: str,
    ):
        await self.db.execute(
            update(OTPVerification)
            .where(
                OTPVerification.email == email,
                OTPVerification.purpose == purpose,
                OTPVerification.is_used.is_(False),
            )
            .values(
                is_used=True,
            )
        )

        await self.db.commit()