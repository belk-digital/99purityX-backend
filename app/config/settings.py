from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Telehealth Platform"
    APP_VERSION: str = "1.0.0"

    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str
    REDIS_URL: str
    
    GOOGLE_CLIENT_ID: str

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "Longevity Platform"

    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_API_KEY_SID: str = ""
    TWILIO_API_KEY_SECRET: str = ""

    DOCUMENT_STORAGE_DIR: str = "storage/documents"
    MAX_DOCUMENT_UPLOAD_BYTES: int = 10 * 1024 * 1024
    ALLOWED_DOCUMENT_MIME_TYPES: list[str] = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )



settings = Settings()

AUDIT_RETENTION_DAYS: int = 3650  # 10 years
