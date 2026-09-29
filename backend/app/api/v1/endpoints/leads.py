from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.database import get_db
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadListResponse
from app.schemas.activity import ActivityCreate, ActivityResponse
from app.schemas.note import NoteCreate, NoteResponse
from app.services.lead_service import lead_service
from app.core.security import get_current_user
from app.models.user import User
from app.models.activity import Activity
from app.models.note import Note

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("", response_model=LeadListResponse)
def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    source: Optional[str] = None,
    owner_id: Optional[str] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List leads with server-side filtering, search, and pagination."""
    return lead_service.get_leads(
        db, page, page_size, search, status, priority, source,
        owner_id, min_score, max_score, sort_by, sort_dir
    )


@router.post("", response_model=LeadResponse, status_code=201)
def create_lead(
    lead_in: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new lead."""
    lead = lead_service.create_lead(db, lead_in, current_user)
    resp = LeadResponse.model_validate(lead)
    resp.activity_count = 0
    return resp


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single lead by ID."""
    lead = lead_service.get_lead(db, lead_id)
    resp = LeadResponse.model_validate(lead)
    resp.activity_count = len(lead.activities)
    return resp


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: str,
    lead_in: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing lead."""
    lead = lead_service.update_lead(db, lead_id, lead_in, current_user)
    resp = LeadResponse.model_validate(lead)
    resp.activity_count = len(lead.activities)
    return resp


@router.delete("/{lead_id}", status_code=204)
def delete_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a lead. Sales reps can only delete their own leads."""
    lead_service.delete_lead(db, lead_id, current_user)


@router.get("/{lead_id}/activities", response_model=List[ActivityResponse])
def get_lead_activities(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all activities for a lead."""
    activities = (
        db.query(Activity)
        .filter(Activity.lead_id == lead_id)
        .order_by(Activity.created_at.desc())
        .all()
    )
    return [ActivityResponse.model_validate(a) for a in activities]


@router.post("/{lead_id}/activities", response_model=ActivityResponse, status_code=201)
def create_lead_activity(
    lead_id: str,
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record an activity for a lead."""
    lead_service.get_lead(db, lead_id)  # Validates lead exists
    activity = Activity(
        **activity_in.model_dump(exclude={"lead_id"}),
        lead_id=lead_id,
        user_id=current_user.id,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return ActivityResponse.model_validate(activity)


@router.get("/{lead_id}/notes", response_model=List[NoteResponse])
def get_lead_notes(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all notes for a lead."""
    notes = (
        db.query(Note)
        .filter(Note.lead_id == lead_id)
        .order_by(Note.created_at.desc())
        .all()
    )
    result = []
    for note in notes:
        nr = NoteResponse.model_validate(note)
        if note.author:
            nr.author_name = note.author.full_name
        result.append(nr)
    return result


@router.post("/{lead_id}/notes", response_model=NoteResponse, status_code=201)
def create_lead_note(
    lead_id: str,
    note_in: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a note to a lead."""
    lead_service.get_lead(db, lead_id)  # Validates lead exists
    note = Note(
        content=note_in.content,
        lead_id=lead_id,
        author_id=current_user.id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    nr = NoteResponse.model_validate(note)
    nr.author_name = current_user.full_name
    return nr
