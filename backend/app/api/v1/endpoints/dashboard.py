from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.dashboard_service import dashboard_service
from app.core.security import get_current_user
from app.models.user import User
from typing import Any, Dict

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get all dashboard KPI statistics from live database."""
    return dashboard_service.get_stats(db)


@router.get("/charts")
def get_dashboard_charts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get chart data for the analytics dashboard."""
    return dashboard_service.get_charts_data(db)
