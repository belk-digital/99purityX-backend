import hashlib
import secrets

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from app.modules.auth.models.otp_verification import (
    OTPVerification,
)

from app.modules.auth.repositories.otp_repository import (
    OTPRepository,
)

from app.modules.auth.enums.otp_purpose import (
    OTPPurpose,
)
from app.modules.audit.enums.audit_enums import (
    AuditAction,
    AuditResource,
)

from app.modules.audit.schemas.audit_schema import (
    AuditLogCreate,
)

from app.modules.audit.services.audit_service import (
    AuditService,
)

class OTPService:

    OTP_EXPIRY_MINUTES = 5

    def __init__(self, db):
        self.repository = OTPRepository(db)

    @staticmethod
    def generate_otp():
        return "".join(
            str(secrets.randbelow(10))
            for _ in range(6)
        )

    @staticmethod
    def hash_otp(
        otp: str,
    ):
        return hashlib.sha256(
            otp.encode()
        ).hexdigest()

    async def create_otp(
        self,
        email: str,
        purpose: OTPPurpose,
    ):
        await self.repository.invalidate_existing_otps(
            email=email,
            purpose=purpose.value,
        )

        otp = self.generate_otp()

        otp_record = OTPVerification(
            email=email,
            otp_hash=self.hash_otp(otp),
            purpose=purpose.value,
            expires_at=datetime.now(
                timezone.utc
            ) + timedelta(
                minutes=self.OTP_EXPIRY_MINUTES
            ),
        )

        await self.repository.create(
            otp_record
        )
        
        await AuditService.create_log(
            db=self.repository.db,
            actor_user_id=None,
            payload=AuditLogCreate(
                action=AuditAction.OTP_GENERATED.value,
                resource=AuditResource.OTP.value,
                description="Verification OTP generated",
            ),
        )

        return otp

    async def verify_otp(
        self,
        email: str,
        otp: str,
        purpose: OTPPurpose,
    ):
        record = (
            await self.repository.get_latest_otp(
                email,
                purpose.value,
            )
        )

        if not record:
            raise ValueError(
                "OTP not found"
            )
            
        if record.attempts >= 5:
            raise ValueError(
                "Maximum OTP attempts exceeded"
            )

        if record.is_used:
            raise ValueError(
                "OTP already used"
            )

        if (
            datetime.now(timezone.utc)
            > record.expires_at
        ):
            raise ValueError(
                "OTP expired"
            )

        if (
            record.otp_hash
            != self.hash_otp(otp)
        ):
            record.attempts += 1

            if record.attempts >= 5:
                record.is_used = True

            await self.repository.update(
                record
            )

            await AuditService.create_log(
                db=self.repository.db,
                actor_user_id=None,
                payload=AuditLogCreate(
                    action=AuditAction.OTP_VERIFICATION_FAILED.value,
                    resource=AuditResource.OTP.value,
                    description="Invalid OTP verification attempt",
                ),
            )

            raise ValueError(
                "Invalid OTP"
            )

        record.is_used = True

        await self.repository.update(
            record
        )

        return True