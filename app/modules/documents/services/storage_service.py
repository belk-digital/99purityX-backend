from pathlib import Path
from uuid import uuid4

from app.config.settings import settings


class StorageService:
    async def upload_file(
        self,
        original_file_name: str,
        content: bytes,
        mime_type: str,
    ) -> tuple[str, str]:
        raise NotImplementedError

    async def generate_download_url(
        self,
        storage_key: str,
        document_id,
    ) -> str:
        raise NotImplementedError

    async def delete_file(
        self,
        storage_key: str,
    ) -> None:
        raise NotImplementedError


class LocalStorageService(StorageService):
    def __init__(self):
        self.base_path = Path(settings.DOCUMENT_STORAGE_DIR)

    async def upload_file(
        self,
        original_file_name: str,
        content: bytes,
        mime_type: str,
    ) -> tuple[str, str]:
        extension = Path(original_file_name).suffix.lower()
        generated_name = f"{uuid4()}{extension}"
        storage_key = generated_name

        self.base_path.mkdir(parents=True, exist_ok=True)

        file_path = self.base_path / generated_name
        file_path.write_bytes(content)

        return generated_name, storage_key

    async def generate_download_url(
        self,
        storage_key: str,
        document_id,
    ) -> str:
        return f"/documents/{document_id}/download"

    async def delete_file(
        self,
        storage_key: str,
    ) -> None:
        file_path = self.base_path / storage_key

        if file_path.exists():
            file_path.unlink()


def get_storage_service() -> StorageService:
    return LocalStorageService()
