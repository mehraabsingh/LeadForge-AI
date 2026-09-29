from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    assigned_to_id: Optional[str] = None
    lead_id: Optional[str] = None
    company_id: Optional[str] = None
    opportunity_id: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to_id: Optional[str] = None
    lead_id: Optional[str] = None


class TaskAssigneeInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    full_name: str


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: TaskStatus
    priority: TaskPriority
    assigned_to_id: Optional[str] = None
    assigned_to: Optional[TaskAssigneeInfo] = None
    created_by_id: Optional[str] = None
    lead_id: Optional[str] = None
    lead_name: Optional[str] = None
    company_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    is_overdue: Optional[bool] = None
    created_at: datetime
    updated_at: datetime
