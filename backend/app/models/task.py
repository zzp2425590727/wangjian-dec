import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class DetectionTask(Base):
    __tablename__ = "detection_tasks"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: f"task_{uuid.uuid4().hex[:8]}"
    )
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    media_type: Mapped[str] = mapped_column(String, default="image")
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, processing, success, failed
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    original_file_url: Mapped[str | None] = mapped_column(String, nullable=True)
    result_file_url: Mapped[str | None] = mapped_column(String, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="tasks")
    detection_result = relationship("DetectionResult", back_populates="task", uselist=False)
