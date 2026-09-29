from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime
from app.db.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.core.security import get_current_user
from app.models.user import User
from app.models.task import Task, TaskStatus

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _task_to_response(task: Task) -> TaskResponse:
    r = TaskResponse.model_validate(task)
    if task.due_date:
        r.is_overdue = task.due_date < datetime.utcnow() and task.status != TaskStatus.COMPLETED
    if task.lead:
        r.lead_name = task.lead.full_name
    return r


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to_id: Optional[str] = None,
    lead_id: Optional[str] = None,
    overdue_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tasks with optional filtering."""
    query = db.query(Task).options(
        joinedload(Task.assigned_to),
        joinedload(Task.lead),
    )
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assigned_to_id:
        query = query.filter(Task.assigned_to_id == assigned_to_id)
    if lead_id:
        query = query.filter(Task.lead_id == lead_id)
    if overdue_only:
        query = query.filter(
            Task.due_date < datetime.utcnow(),
            Task.status != TaskStatus.COMPLETED,
        )
    tasks = query.order_by(Task.due_date.asc().nullsfirst()).all()
    return [_task_to_response(t) for t in tasks]


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = Task(
        **task_in.model_dump(),
        created_by_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task = db.query(Task).options(
        joinedload(Task.assigned_to), joinedload(Task.lead)
    ).filter(Task.id == task.id).first()
    return _task_to_response(task)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).options(
        joinedload(Task.assigned_to), joinedload(Task.lead)
    ).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return _task_to_response(task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    task = db.query(Task).options(
        joinedload(Task.assigned_to), joinedload(Task.lead)
    ).filter(Task.id == task_id).first()
    return _task_to_response(task)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
