from google.auth.transport import requests
from google.oauth2 import id_token

from app.config.settings import settings


class GoogleService:

    @staticmethod
    def verify_token(
        token: str,
    ):
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        return payload