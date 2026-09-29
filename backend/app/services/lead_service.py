"""
Lead service - business logic for lead management.
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from fastapi import HTTPException, status
from app.models.lead import Lead, LeadStatus, LeadPriority
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadListResponse
import logging
import math

logger = logging.getLogger(__name__)


class LeadService:

    def get_leads(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        source: Optional[str] = None,
        owner_id: Optional[str] = None,
        min_score: Optional[int] = None,
        max_score: Optional[int] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> LeadListResponse:
        query = db.query(Lead).options(joinedload(Lead.owner))

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Lead.first_name.ilike(search_term),
                    Lead.last_name.ilike(search_term),
                    Lead.email.ilike(search_term),
                    Lead.company.ilike(search_term),
                )
            )

        if status:
            query = query.filter(Lead.status == status)
        if priority:
            query = query.filter(Lead.priority == priority)
        if source:
            query = query.filter(Lead.source == source)
        if owner_id:
            query = query.filter(Lead.owner_id == owner_id)
        if min_score is not None:
            query = query.filter(Lead.score >= min_score)
        if max_score is not None:
            query = query.filter(Lead.score <= max_score)

        # Sorting
        sort_column = getattr(Lead, sort_by, Lead.created_at)
        if sort_dir == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        total = query.count()
        offset = (page - 1) * page_size
        leads = query.offset(offset).limit(page_size).all()

        lead_responses = []
        for lead in leads:
            resp = LeadResponse.model_validate(lead)
            resp.activity_count = len(lead.activities)
            lead_responses.append(resp)

        return LeadListResponse(
            leads=lead_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 1,
        )

    def get_lead(self, db: Session, lead_id: str) -> Lead:
        lead = (
            db.query(Lead)
            .options(
                joinedload(Lead.owner),
                joinedload(Lead.activities),
                joinedload(Lead.notes),
                joinedload(Lead.tasks),
            )
            .filter(Lead.id == lead_id)
            .first()
        )
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return lead

    def create_lead(self, db: Session, lead_in: LeadCreate, current_user: User) -> Lead:
        # Auto-assign to current user if no owner specified
        owner_id = lead_in.owner_id or current_user.id

        lead = Lead(
            **lead_in.model_dump(exclude={"owner_id"}),
            owner_id=owner_id,
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        logger.info(f"Lead created: {lead.full_name} by user {current_user.email}")
        return lead

    def update_lead(self, db: Session, lead_id: str, lead_in: LeadUpdate, current_user: User) -> Lead:
        lead = self.get_lead(db, lead_id)

        update_data = lead_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(lead, key, value)

        db.commit()
        db.refresh(lead)
        logger.info(f"Lead updated: {lead.full_name} by {current_user.email}")
        return lead

    def delete_lead(self, db: Session, lead_id: str, current_user: User) -> None:
        lead = self.get_lead(db, lead_id)
        # Only admin/manager or owner can delete
        if current_user.role == "SALES_REP" and lead.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete leads you own",
            )
        db.delete(lead)
        db.commit()
        logger.info(f"Lead deleted: {lead_id} by {current_user.email}")


lead_service = LeadService()
