import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services import task_service
from app.services.file_service import validate_image_file, save_upload_file

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskBrief(BaseModel):
    id: str
    file_name: str
    media_type: str
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    items: list[TaskBrief]
    page: int
    page_size: int
    total: int


class ClassificationItem(BaseModel):
    keyword: str
    root: str
    score: float


class DetectionResultData(BaseModel):
    task_id: str
    result_num: int
    items: list[ClassificationItem]
    raw_log_id: str | None = None


class TaskDetail(BaseModel):
    id: str
    user_id: str
    file_name: str
    media_type: str
    status: str
    created_at: str
    updated_at: str
    original_file_url: str | None = None
    result_file_url: str | None = None
    error_message: str | None = None


class TaskDetailResponse(BaseModel):
    task: TaskDetail
    result: DetectionResultData | None = None


def _task_to_brief(task) -> TaskBrief:
    return TaskBrief(
        id=task.id,
        file_name=task.file_name,
        media_type=task.media_type,
        status=task.status,
        created_at=task.created_at.isoformat() if task.created_at else "",
        updated_at=task.updated_at.isoformat() if task.updated_at else "",
    )


def _task_to_detail(task) -> TaskDetail:
    return TaskDetail(
        id=task.id,
        user_id=task.user_id,
        file_name=task.file_name,
        media_type=task.media_type,
        status=task.status,
        created_at=task.created_at.isoformat() if task.created_at else "",
        updated_at=task.updated_at.isoformat() if task.updated_at else "",
        original_file_url=task.original_file_url,
        result_file_url=task.result_file_url,
        error_message=task.error_message,
    )


def _run_detection_sync(task_id: str):
    """Run detection in a separate thread (for BackgroundTasks)."""
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        task = db.query(task_service.DetectionTask).filter(
            task_service.DetectionTask.id == task_id
        ).first()
        if task:
            task_service.run_detection(db, task)
    finally:
        db.close()


@router.post("", response_model=dict)
async def create_task(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    media_type: str = Form("image"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload an image and create a detection task."""
    validate_image_file(file)
    task = task_service.create_task(
        db, user_id=current_user.id, file_name=file.filename or "unknown.jpg", file_path=""
    )
    # Save file with task_id as directory name
    file_path = await save_upload_file(file, task.id)
    task.original_file_url = f"/api/files/{task.id}/original"
    db.commit()

    # Run detection in background
    background_tasks.add_task(_run_detection_sync, task.id)

    return {"id": task.id, "status": task.status, "media_type": task.media_type}


@router.get("", response_model=TaskListResponse)
def list_tasks(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get paginated task list for current user."""
    tasks, total = task_service.get_user_tasks(
        db, user_id=current_user.id, page=page, page_size=page_size, status=status
    )
    return TaskListResponse(
        items=[_task_to_brief(t) for t in tasks],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{task_id}", response_model=TaskDetailResponse)
def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get task detail with detection result."""
    task = task_service.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    result_data = task_service.get_task_result(db, task_id)
    result = None
    if result_data:
        result = DetectionResultData(**result_data)

    return TaskDetailResponse(
        task=_task_to_detail(task),
        result=result,
    )
