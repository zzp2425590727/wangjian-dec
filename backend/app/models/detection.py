from sqlalchemy import String, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class DetectionResult(Base):
    __tablename__ = "detection_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String, ForeignKey("detection_tasks.id"), unique=True, nullable=False, index=True)
    result_num: Mapped[int] = mapped_column(Integer, default=0)
    items_json: Mapped[str] = mapped_column(Text, default="[]")  # JSON string of ClassificationItem list
    raw_log_id: Mapped[str | None] = mapped_column(String, nullable=True)

    task = relationship("DetectionTask", back_populates="detection_result")
