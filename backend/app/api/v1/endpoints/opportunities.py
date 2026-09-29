from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.db.database import get_db
from app.schemas.opportunity import (
    OpportunityCreate, OpportunityUpdate, OpportunityResponse, OpportunityListResponse
)
from app.core.security import get_current_user
from app.models.user import User
from app.models.opportunity import Opportunity, OpportunityStatus

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


def _opp_to_response(opp: Opportunity) -> OpportunityResponse:
    r = OpportunityResponse.model_validate(opp)
    r.weighted_value = opp.weighted_value
    return r


@router.get("", response_model=OpportunityListResponse)
def list_opportunities(
    stage_id: Optional[str] = None,
    pipeline_id: Optional[str] = None,
    status: Optional[str] = None,
    owner_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all opportunities with pipeline metrics."""
    query = db.query(Opportunity).options(
        joinedload(Opportunity.stage),
        joinedload(Opportunity.owner),
    )
    if stage_id:
        query = query.filter(Opportunity.stage_id == stage_id)
    if pipeline_id:
        query = query.filter(Opportunity.pipeline_id == pipeline_id)
    if status:
        query = query.filter(Opportunity.status == status)
    if owner_id:
        query = query.filter(Opportunity.owner_id == owner_id)

    opps = query.order_by(Opportunity.updated_at.desc()).all()

    open_opps = [o for o in opps if o.status == OpportunityStatus.OPEN]
    won_opps = [o for o in opps if o.status == OpportunityStatus.WON]
    lost_count = sum(1 for o in opps if o.status == OpportunityStatus.LOST)
    total_closed = len(won_opps) + lost_count
    win_rate = (len(won_opps) / total_closed * 100) if total_closed > 0 else 0.0

    return OpportunityListResponse(
        opportunities=[_opp_to_response(o) for o in opps],
        total=len(opps),
        pipeline_value=round(sum(o.value or 0 for o in open_opps), 2),
        weighted_value=round(sum(o.weighted_value for o in open_opps), 2),
        won_value=round(sum(o.value or 0 for o in won_opps), 2),
        win_rate=round(win_rate, 1),
    )


@router.post("", response_model=OpportunityResponse, status_code=201)
def create_opportunity(
    opp_in: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new opportunity."""
    opp = Opportunity(
        **opp_in.model_dump(),
        owner_id=opp_in.owner_id or current_user.id,
    )
    db.add(opp)
    db.commit()
    db.refresh(opp)
    # Reload with joins
    opp = db.query(Opportunity).options(
        joinedload(Opportunity.stage), joinedload(Opportunity.owner)
    ).filter(Opportunity.id == opp.id).first()
    return _opp_to_response(opp)


@router.get("/{opp_id}", response_model=OpportunityResponse)
def get_opportunity(
    opp_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    opp = (
        db.query(Opportunity)
        .options(joinedload(Opportunity.stage), joinedload(Opportunity.owner))
        .filter(Opportunity.id == opp_id)
        .first()
    )
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return _opp_to_response(opp)


@router.put("/{opp_id}", response_model=OpportunityResponse)
def update_opportunity(
    opp_id: str,
    opp_in: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an opportunity (including moving pipeline stage)."""
    opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    for key, value in opp_in.model_dump(exclude_unset=True).items():
        setattr(opp, key, value)
    db.commit()
    opp = db.query(Opportunity).options(
        joinedload(Opportunity.stage), joinedload(Opportunity.owner)
    ).filter(Opportunity.id == opp_id).first()
    return _opp_to_response(opp)


@router.delete("/{opp_id}", status_code=204)
def delete_opportunity(
    opp_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    db.delete(opp)
    db.commit()
