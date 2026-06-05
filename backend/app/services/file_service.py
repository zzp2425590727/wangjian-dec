import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


def validate_image_file(file: UploadFile) -> None:
    """Validate file extension and MIME type."""
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: {ext}")


async def save_upload_file(file: UploadFile, task_id: str) -> str:
    """Save uploaded file to disk and return the relative file path."""
    ext = Path(file.filename or ".jpg").suffix.lower()
    task_dir = Path(settings.UPLOAD_DIR) / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    file_path = task_dir / f"original{ext}"

    # Check file size by reading content
    content = await file.read()
    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {settings.MAX_IMAGE_SIZE_MB}MB")

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return str(file_path)


def get_file_path(task_id: str, file_name: str) -> Path:
    """Get the absolute path of a file, with path traversal protection."""
    task_dir = Path(settings.UPLOAD_DIR) / task_id
    file_path = (task_dir / file_name).resolve()

    # Ensure the resolved path is within the task directory
    if not str(file_path).startswith(str(task_dir.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return file_path
