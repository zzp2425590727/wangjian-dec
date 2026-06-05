from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.task import DetectionTask
from app.core.security import get_current_user, decode_token
from app.core.config import settings
from app.services.file_service import get_file_path

router = APIRouter(prefix="/api/files", tags=["files"])


def _get_current_user_from_token_query(
    token: str | None,
    db: Session,
) -> User:
    """Authenticate user from query parameter token or Authorization header."""
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/{task_id}/{file_name}")
def serve_file(
    task_id: str,
    file_name: str,
    token: str | None = Query(None, description="Auth token for image loading"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Serve a file belonging to a task. Only the task owner can access it."""
    task = db.query(DetectionTask).filter(
        DetectionTask.id == task_id,
        DetectionTask.user_id == current_user.id,
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return _serve_task_file(task_id, file_name)


@router.get("/{task_id}/{file_name}/raw")
def serve_file_raw(
    task_id: str,
    file_name: str,
    token: str = Query(..., description="Auth token"),
    db: Session = Depends(get_db),
):
    """Serve a file using token query parameter (for <img> src)."""
    user = _get_current_user_from_token_query(token, db)
    task = db.query(DetectionTask).filter(
        DetectionTask.id == task_id,
        DetectionTask.user_id == user.id,
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return _serve_task_file(task_id, file_name)


def _serve_task_file(task_id: str, file_name: str) -> FileResponse:
    """Internal helper to serve a task file."""
    if file_name == "original":
        task_dir = Path(settings.UPLOAD_DIR) / task_id
        if not task_dir.exists():
            raise HTTPException(status_code=404, detail="File not found")

        for f in task_dir.iterdir():
            if f.name.startswith("original"):
                file_path = f
                break
        else:
            raise HTTPException(status_code=404, detail="File not found")
    else:
        file_path = get_file_path(task_id, file_name)

    # Determine media type from extension
    ext = file_path.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=file_path.name,
    )
