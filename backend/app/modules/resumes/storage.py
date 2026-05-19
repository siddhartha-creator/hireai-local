from pathlib import Path
from uuid import uuid4

from app.core.config import settings


class ResumeStorageService:
    def __init__(self, storage_dir: str | None = None) -> None:
        self.storage_dir = Path(storage_dir or settings.RESUME_UPLOAD_DIR)

    def save(self, *, content: bytes, file_type: str) -> tuple[str, str]:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{uuid4().hex}.{file_type}"
        file_path = self.storage_dir / file_name
        file_path.write_bytes(content)
        return file_name, str(file_path)

    def delete(self, file_path: str) -> None:
        path = Path(file_path)
        if path.exists() and path.is_file():
            path.unlink()
