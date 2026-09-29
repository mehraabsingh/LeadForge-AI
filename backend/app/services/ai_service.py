"""
AI service for leads - scoring, summary, email, insights.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.lead import Lead
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.ai_analysis import AIAnalysis
from app.ai.factory import get_ai_service
from app.schemas.ai_schemas import EmailType
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AILeadService:

    def score_lead(self, db: Session, lead_id: str, user_id: str) -> dict:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        ai_service = get_ai_service()
        lead_data = {
            "id": lead.id,
            "full_name": lead.full_name,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "job_title": lead.job_title,
            "source": lead.source.value if lead.source else None,
            "industry": lead.industry,
            "company_size": lead.company_size,
            "location": lead.location,
            "estimated_value": lead.estimated_value,
            "status": lead.status.value if lead.status else None,
        }

        result = ai_service.score_lead(lead_data)

        # Update lead score
        lead.score = result["score"]
        lead.score_label = result["label"]

        # Store AI analysis
        analysis = AIAnalysis(
            analysis_type="score",
            provider=result["provider"],
            score=result["score"],
            score_label=result["label"],
            result_data=result,
            lead_id=lead_id,
            created_by_id=user_id,
        )
        db.add(analysis)
        db.commit()
        return result

    def summarize_lead(self, db: Session, lead_id: str, user_id: str) -> dict:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        activities = [
            {"type": a.type.value, "title": a.title, "created_at": a.created_at.isoformat()}
            for a in (lead.activities or [])
        ]
        notes = [{"content": n.content} for n in (lead.notes or [])]

        ai_service = get_ai_service()
        lead_data = {
            "id": lead.id,
            "full_name": lead.full_name,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "company": lead.company,
            "job_title": lead.job_title,
            "industry": lead.industry,
            "source": lead.source.value if lead.source else None,
            "status": lead.status.value if lead.status else None,
            "score": lead.score,
            "estimated_value": lead.estimated_value,
            "location": lead.location,
        }

        result = ai_service.summarize_lead(lead_data, activities, notes)

        analysis = AIAnalysis(
            analysis_type="summary",
            provider=result["provider"],
            result_data=result,
            lead_id=lead_id,
            created_by_id=user_id,
        )
        db.add(analysis)
        db.commit()
        return result

    def generate_follow_up_email(
        self, db: Session, lead_id: str, email_type: str, user_id: str
    ) -> dict:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        ai_service = get_ai_service()
        lead_data = {
            "id": lead.id,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "full_name": lead.full_name,
            "company": lead.company,
            "job_title": lead.job_title,
            "industry": lead.industry,
            "source": lead.source.value if lead.source else None,
        }

        result = ai_service.generate_follow_up_email(lead_data, email_type)

        analysis = AIAnalysis(
            analysis_type="email",
            provider=result["provider"],
            result_data=result,
            lead_id=lead_id,
            created_by_id=user_id,
        )
        db.add(analysis)
        db.commit()
        return result

    def get_insights(self, db: Session) -> dict:
        """Generate sales insights from live pipeline data."""
        leads = db.query(Lead).all()
        opps = db.query(Opportunity).all()

        lead_data = []
        for lead in leads:
            lead_data.append({
                "id": lead.id,
                "status": lead.status.value,
                "estimated_value": lead.estimated_value,
                "activity_count": len(lead.activities) if lead.activities else 0,
            })

        opp_data = []
        for opp in opps:
            opp_data.append({
                "id": opp.id,
                "status": opp.status.value,
                "value": opp.value,
                "probability": opp.probability,
            })

        pipeline_data = {"leads": lead_data, "opportunities": opp_data}
        ai_service = get_ai_service()
        return ai_service.generate_sales_insights(pipeline_data)


ai_lead_service = AILeadService()
