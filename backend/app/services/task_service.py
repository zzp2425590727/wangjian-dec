import json
import logging
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.task import DetectionTask
from app.models.detection import DetectionResult
from app.adapters.detection_api import detect_image, parse_detection_result, build_detection_result
from app.core.config import settings

logger = logging.getLogger(__name__)


def create_task(db: Session, user_id: str, file_name: str, file_path: str) -> DetectionTask:
    """Create a new detection task."""
    task = DetectionTask(
        user_id=user_id,
        file_name=file_name,
        media_type="image",
        status="pending",
        original_file_url=file_path,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task_by_id(db: Session, task_id: str, user_id: str) -> DetectionTask | None:
    """Get a task by ID, only if it belongs to the user."""
    return db.query(DetectionTask).filter(
        DetectionTask.id == task_id,
        DetectionTask.user_id == user_id,
    ).first()


def get_user_tasks(
    db: Session, user_id: str, page: int = 1, page_size: int = 20, status: str | None = None
) -> tuple[list[DetectionTask], int]:
    """Get paginated tasks for a user."""
    query = db.query(DetectionTask).filter(DetectionTask.user_id == user_id)
    if status:
        query = query.filter(DetectionTask.status == status)
    total = query.count()
    tasks = (
        query.order_by(DetectionTask.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return tasks, total


def get_task_result(db: Session, task_id: str) -> dict | None:
    """Get the detection result for a task."""
    result = db.query(DetectionResult).filter(DetectionResult.task_id == task_id).first()
    if not result:
        return None
    return {
        "task_id": result.task_id,
        "result_num": result.result_num,
        "items": json.loads(result.items_json),
        "raw_log_id": result.raw_log_id,
    }


def find_original_file(task_id: str) -> str | None:
    """Find the actual original file path on disk."""
    task_dir = Path(settings.UPLOAD_DIR) / task_id
    if not task_dir.exists():
        return None
    for f in task_dir.iterdir():
        if f.name.startswith("original"):
            return str(f)
    return None


def run_detection(db: Session, task: DetectionTask) -> None:
    """
    Run image detection synchronously.
    Updates task status and saves result.
    """
    try:
        task.status = "processing"
        task.updated_at = datetime.now(timezone.utc)
        db.commit()

        # Find the actual file on disk
        file_path = find_original_file(task.id)
        if not file_path:
            raise FileNotFoundError(f"Upload file not found for task {task.id}")

        # Call Baidu API
        loop = asyncio.new_event_loop()
        try:
            raw_data = loop.run_until_complete(detect_image(file_path))
        finally:
            loop.close()

        parsed = parse_detection_result(raw_data)
        result = build_detection_result(task.id, parsed)

        db.add(result)
        task.status = "success"
        task.updated_at = datetime.now(timezone.utc)
        db.commit()

    except ValueError as e:
        task.status = "failed"
        task.error_message = str(e)
        task.updated_at = datetime.now(timezone.utc)
        db.commit()
        logger.error(f"Detection failed for task {task.id}: {e}")

    except Exception as e:
        task.status = "failed"
        task.error_message = f"Detection error: {str(e)}"
        task.updated_at = datetime.now(timezone.utc)
        db.commit()
        logger.error(f"Detection error for task {task.id}: {e}")
