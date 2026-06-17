import hashlib
from datetime import datetime, timedelta, timezone
import secrets

from fastapi import Request
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings

from app.modules.auth.enums.roles import RoleEnum

from app.modules.auth.models.role import Role
from app.modules.auth.models.session import (
    UserSession,
)
from app.modules.auth.models.user import User
from app.modules.auth.models.user_profile import (
    UserProfile,
)

from app.modules.auth.repositories.auth_repository import (
    AuthRepository,
)

from app.modules.auth.services.jwt_service import (
    JWTService,
)

from app.modules.auth.services.password_service import (
    PasswordService,
)

from app.modules.audit.schemas.audit_schema import (
    AuditLogCreate,
)

from app.modules.audit.services.audit_service import (
    AuditService,
)

from app.modules.patients.services.patient_service import (
    PatientService,
)

from app.modules.audit.enums.audit_enums import (
    AuditAction,
    AuditResource,
)

from app.modules.auth.services.otp_service import (
    OTPService,
)

from app.modules.auth.services.email_service import (
    EmailService,
)

from app.modules.auth.enums.otp_purpose import (
    OTPPurpose,
)

from app.modules.auth.services.google_service import (
    GoogleService,
)

from app.modules.auth.enums.auth_provider import (
    AuthProvider,
)


class AuthService:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db
        self.repository = AuthRepository(db)

    def hash_token(
        self,
        token: str,
    ):
        return hashlib.sha256(
            token.encode()
        ).hexdigest()

    async def register_user(
        self,
        data,
    ):
        existing_user = (
            await self.repository.get_user_by_email(
                data.email
            )
        )

        if existing_user:
            raise ValueError(
                "Email already registered"
            )

        role_name = getattr(data, "role", None) or RoleEnum.PATIENT.value

        result = await self.db.execute(
            select(Role).where(
                Role.name == role_name
            )
        )

        role = result.scalar_one_or_none()

        if not role:
            raise ValueError(
                f"Role '{role_name}' not found"
            )

        user = User(
            email=data.email,
            hashed_password=PasswordService.hash_password(
                data.password
            ),
            role_id=role.id,
        )

        created_user = (
            await self.repository.create_user(
                user
            )
        )

        profile = UserProfile(
            user_id=created_user.id,
            first_name=data.first_name,
            last_name=data.last_name,
        )

        await self.repository.create_profile(
            profile
        )
        
        patient_service = PatientService(
            self.db
        )

        await patient_service.create_patient_profile(
            created_user.id
        )

        otp_service = OTPService(
            self.db
        )

        otp = await otp_service.create_otp(
            email=created_user.email,
            purpose=OTPPurpose.EMAIL_VERIFICATION,
        )

        await EmailService.send_verification_otp(
            created_user.email,
            otp,
        )

        return created_user

    async def login_user(
        self,
        data,
        request: Request,
    ):
        
        user = (
            await self.repository.get_user_by_email(
                data.email
            )
        )

        if not user:

            await AuditService.create_log(
                db=self.db,
                actor_user_id=None,
                payload=AuditLogCreate(
                    action=AuditAction.LOGIN.value,
                    resource=AuditResource.USER.value,
                    description=f"Failed login attempt for email {data.email}",
                    ip_address=request.client.host,
                    user_agent=request.headers.get(
                        "user-agent"
                    ),
                ),
            )

            raise ValueError(
                "Invalid credentials"
            )
            
        if (
            user.auth_provider
            == AuthProvider.GOOGLE.value
        ):
            raise ValueError(
                "Please continue with Google"
            )

        valid_password = (
            PasswordService.verify_password(
                data.password,
                user.hashed_password,
            )
        )

        if not valid_password:

            await AuditService.create_log(
                db=self.db,
                actor_user_id=user.id,
                payload=AuditLogCreate(
                    action=AuditAction.LOGIN.value,
                    resource=AuditResource.USER.value,
                    resource_id=str(user.id),
                    description="Failed login attempt due to invalid password",
                    ip_address=request.client.host,
                    user_agent=request.headers.get(
                        "user-agent"
                    ),
                ),
            )

            raise ValueError(
                "Invalid credentials"
            )
            
        if not user.is_active:
            raise ValueError(
                "Account inactive"
            )

        if not user.is_verified:
            raise ValueError(
                "Please verify your email"
            )

        access_token = (
            JWTService.create_access_token(
                str(user.id)
            )
        )

        refresh_token = (
            JWTService.create_refresh_token(
                str(user.id)
            )
        )

        refresh_token_hash = (
            self.hash_token(refresh_token)
        )

        session = UserSession(
            user_id=user.id,
            refresh_token_hash=refresh_token_hash,
            expires_at=datetime.now(
                timezone.utc
            ) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            ),
        )

        await self.repository.create_session(
            session
        )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=user.id,
            payload=AuditLogCreate(
                action=AuditAction.LOGIN.value,
                resource=AuditResource.USER.value,
                resource_id=str(user.id),
                description="User logged in successfully",
                ip_address=request.client.host,
                user_agent=request.headers.get(
                    "user-agent"
                ),
            ),
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_access_token(
        self,
        refresh_token: str,
        request: Request,
    ):
        payload = JWTService.decode_token(
            refresh_token
        )

        if not payload:
            raise ValueError(
                "Invalid refresh token"
            )

        if payload.get("type") != "refresh":
            raise ValueError(
                "Invalid token type"
            )

        refresh_token_hash = (
            self.hash_token(refresh_token)
        )

        session = (
            await self.repository.get_session_by_token(
                refresh_token_hash
            )
        )

        if not session:
            raise ValueError(
                "Session not found"
            )

        access_token = (
            JWTService.create_access_token(
                payload["sub"]
            )
        )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=payload["sub"],
            payload=AuditLogCreate(
                action=AuditAction.TOKEN_REFRESH.value,
                resource=AuditResource.USER.value,
                resource_id=payload["sub"],
                description="Access token refreshed successfully",
                ip_address=request.client.host,
                user_agent=request.headers.get(
                    "user-agent"
                ),
            ),
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
        
    async def verify_email(
        self,
        email: str,
        otp: str,
    ):
        otp_service = OTPService(
            self.db
        )

        await otp_service.verify_otp(
            email=email,
            otp=otp,
            purpose=OTPPurpose.EMAIL_VERIFICATION,
        )

        user = (
            await self.repository.get_user_by_email(
                email
            )
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        user.is_verified = True

        await self.db.commit()
        await self.db.refresh(user)

        await AuditService.create_log(
            db=self.db,
            actor_user_id=user.id,
            payload=AuditLogCreate(
                action=AuditAction.OTP_VERIFIED.value,
                resource=AuditResource.USER.value,
                resource_id=str(user.id),
                description="Email verified successfully",
            ),
        )

        return {
            "message": "Email verified successfully"
        }

    async def logout(
        self,
        refresh_token: str,
        request: Request,
    ):
        payload = JWTService.decode_token(
            refresh_token
        )

        refresh_token_hash = (
            self.hash_token(refresh_token)
        )

        await self.repository.delete_session(
            refresh_token_hash
        )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=payload["sub"],
            payload=AuditLogCreate(
                action=AuditAction.LOGOUT.value,
                resource=AuditResource.USER.value,
                resource_id=payload["sub"],
                description="User logged out successfully",
                ip_address=request.client.host,
                user_agent=request.headers.get(
                    "user-agent"
                ),
            ),
        )

        return {
            "message": "Logged out successfully"
        }
        
    async def resend_verification_otp(
        self,
        email: str,
    ):
        user = (
            await self.repository.get_user_by_email(
                email
            )
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        if user.is_verified:
            raise ValueError(
                "Email already verified"
            )

        otp_service = OTPService(
            self.db
        )

        latest_otp = (
            await otp_service.repository.get_latest_otp(
                email=email,
                purpose=OTPPurpose.EMAIL_VERIFICATION.value,
            )
        )

        if latest_otp:
            seconds_since_last_otp = (
                datetime.now(timezone.utc)
                - latest_otp.created_at
            ).total_seconds()

            if seconds_since_last_otp < 60:
                raise ValueError(
                    "Please wait 60 seconds before requesting another OTP"
                )

        otp = await otp_service.create_otp(
            email=email,
            purpose=OTPPurpose.EMAIL_VERIFICATION,
        )

        await EmailService.send_verification_otp(
            email,
            otp,
        )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=user.id,
            payload=AuditLogCreate(
                action=AuditAction.OTP_GENERATED.value,
                resource=AuditResource.OTP.value,
                resource_id=str(user.id),
                description="Verification OTP resent",
            ),
        )

        return {
            "message": "OTP sent successfully"
        }
        
    async def forgot_password(
        self,
        email: str,
    ):
        user = (
            await self.repository.get_user_by_email(
                email
            )
        )

        if not user:
            return {
                "message": "If the email exists, a password reset OTP has been sent"
            }
            
        if (
            user.auth_provider
            == AuthProvider.GOOGLE.value
        ):
            raise ValueError(
                "Google account password cannot be reset here"
            )

        otp_service = OTPService(
            self.db
        )

        otp = await otp_service.create_otp(
            email=email,
            purpose=OTPPurpose.PASSWORD_RESET,
        )

        await EmailService.send_verification_otp(
            email,
            otp,
        )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=user.id,
            payload=AuditLogCreate(
                action=AuditAction.OTP_GENERATED.value,
                resource=AuditResource.USER.value,
                resource_id=str(user.id),
                description="Password reset OTP generated",
            ),
        )

        return {
            "message": "Password reset OTP sent"
        }
        
    async def reset_password(
        self,
        email: str,
        otp: str,
        new_password: str,
    ):
        otp_service = OTPService(
            self.db
        )

        await otp_service.verify_otp(
            email=email,
            otp=otp,
            purpose=OTPPurpose.PASSWORD_RESET,
        )

        user = (
            await self.repository.get_user_by_email(
                email
            )
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        user.hashed_password = (
            PasswordService.hash_password(
                new_password
            )
        )
        
        await self.db.execute(
            delete(UserSession).where(
                UserSession.user_id == user.id
            )
        )

        await self.db.commit()

        await AuditService.create_log(
            db=self.db,
            actor_user_id=user.id,
            payload=AuditLogCreate(
                action=AuditAction.UPDATE.value,
                resource=AuditResource.USER.value,
                resource_id=str(user.id),
                description="Password reset successfully",
            ),
        )

        return {
            "message": "Password reset successful"
        }
        
    async def google_login(
        self,
        id_token_str: str,
        request: Request,
    ):
        payload = GoogleService.verify_token(
            id_token_str
        )

        email = payload["email"]

        google_id = payload["sub"]

        first_name = payload.get(
            "given_name",
            ""
        )

        last_name = payload.get(
            "family_name",
            ""
        )

        user = (
            await self.repository.get_user_by_email(
                email
            )
        )

        if not user:

            result = await self.db.execute(
                select(Role).where(
                    Role.name
                    == RoleEnum.PATIENT.value
                )
            )

            role = result.scalar_one()

            user = User(
                email=email,
                hashed_password=PasswordService.hash_password(
                    secrets.token_urlsafe(32)
                ),
                role_id=role.id,
                is_verified=True,
                google_id=google_id,
                auth_provider=AuthProvider.GOOGLE.value,
            )

            user = (
                await self.repository.create_user(
                    user
                )
            )

            profile = UserProfile(
                user_id=user.id,
                first_name=first_name,
                last_name=last_name,
            )

            await self.repository.create_profile(
                profile
            )

            patient_service = PatientService(
                self.db
            )

            await patient_service.create_patient_profile(
                user.id
            )

        access_token = (
            JWTService.create_access_token(
                str(user.id)
            )
        )

        refresh_token = (
            JWTService.create_refresh_token(
                str(user.id)
            )
        )

        session = UserSession(
            user_id=user.id,
            refresh_token_hash=self.hash_token(
                refresh_token
            ),
            expires_at=datetime.now(
                timezone.utc
            ) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            ),
        )

        await self.repository.create_session(
            session
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }