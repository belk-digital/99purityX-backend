from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class PasswordService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password[:72])

    @staticmethod
    def verify_password(
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        return pwd_context.verify(
            plain_password[:72],
            hashed_password,
        )
