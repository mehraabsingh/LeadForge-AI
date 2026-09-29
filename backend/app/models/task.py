import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SAEnum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(SAEnum(TaskStatus), nullable=False, default=TaskStatus.TODO, index=True)
    priority = Column(SAEnum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)

    # Foreign Keys
    assigned_to_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    created_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    lead_id = Column(String(36), ForeignKey("leads.id"), nullable=True, index=True)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    opportunity_id = Column(String(36), ForeignKey("opportunities.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    assigned_to = relationship("User", back_populates="tasks_assigned", foreign_keys=[assigned_to_id])
    created_by = relationship("User", back_populates="tasks_created", foreign_keys=[created_by_id])
    lead = relationship("Lead", back_populates="tasks")
    opportunity = relationship("Opportunity", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task {self.title} ({self.status})>"
