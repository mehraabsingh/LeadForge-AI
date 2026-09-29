from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Any, Dict
from app.db.database import get_db
from app.services.ai_service import ai_lead_service
from app.schemas.ai_schemas import (
    LeadScoreResponse, LeadSummaryResponse, FollowUpEmailResponse,
    SalesInsightsResponse, EmailType
)
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ai", tags=["AI Features"])


@router.post("/leads/{lead_id}/score", response_model=LeadScoreResponse)
def score_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    AI-powered lead scoring (0-100).
    Works with fallback engine when no AI API key is configured.
    """
    return ai_lead_service.score_lead(db, lead_id, current_user.id)


@router.post("/leads/{lead_id}/summary", response_model=LeadSummaryResponse)
def summarize_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Generate an AI summary of a lead's profile, activities, and recommendations."""
    return ai_lead_service.summarize_lead(db, lead_id, current_user.id)


@router.post("/leads/{lead_id}/follow-up-email", response_model=FollowUpEmailResponse)
def generate_follow_up_email(
    lead_id: str,
    email_type: EmailType = Body(EmailType.FIRST_OUTREACH, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Generate a professional follow-up email for a lead."""
    return ai_lead_service.generate_follow_up_email(
        db, lead_id, email_type.value, current_user.id
    )


@router.get("/insights", response_model=SalesInsightsResponse)
def get_sales_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get AI-generated sales insights based on actual pipeline data.
    Identifies leads needing attention, at-risk opportunities, and bottlenecks.
    """
    return ai_lead_service.get_insights(db)
