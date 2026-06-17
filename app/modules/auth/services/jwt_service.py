from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config.settings import settings


class JWTService:
    @staticmethod
    def create_access_token(
        user_id: str,
    ) -> str:
        expire = datetime.now(
            timezone.utc
        ) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload = {
            "sub": user_id,
            "type": "access",
            "exp": expire,
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def create_refresh_token(
        user_id: str,
    ) -> str:
        expire = datetime.now(
            timezone.utc
        ) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def decode_token(token: str):
        try:
            return jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[
                    settings.JWT_ALGORITHM
                ],
            )

        except JWTError:
            return None