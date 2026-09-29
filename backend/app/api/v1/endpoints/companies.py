from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.db.database import get_db
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.schemas.contact import ContactResponse
from app.schemas.activity import ActivityResponse
from app.core.security import get_current_user
from app.models.user import User
from app.models.company import Company
from app.models.contact import Contact
from app.models.activity import Activity

router = APIRouter(prefix="/companies", tags=["Companies"])


def _company_to_response(company: Company) -> CompanyResponse:
    r = CompanyResponse.model_validate(company)
    r.contact_count = len(company.contacts) if company.contacts else 0
    r.lead_count = len(company.leads) if company.leads else 0
    return r


@router.get("", response_model=List[CompanyResponse])
def list_companies(
    search: Optional[str] = None,
    industry: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all companies."""
    query = db.query(Company).options(joinedload(Company.contacts), joinedload(Company.leads))
    if search:
        query = query.filter(Company.name.ilike(f"%{search}%"))
    if industry:
        query = query.filter(Company.industry.ilike(f"%{industry}%"))
    offset = (page - 1) * page_size
    companies = query.order_by(Company.name).offset(offset).limit(page_size).all()
    return [_company_to_response(c) for c in companies]


@router.post("", response_model=CompanyResponse, status_code=201)
def create_company(
    company_in: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new company."""
    company = Company(**company_in.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return _company_to_response(company)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get company details with contacts and leads count."""
    company = (
        db.query(Company)
        .options(joinedload(Company.contacts), joinedload(Company.leads))
        .filter(Company.id == company_id)
        .first()
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return _company_to_response(company)


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: str,
    company_in: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update company details."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for key, value in company_in.model_dump(exclude_unset=True).items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return _company_to_response(company)


@router.delete("/{company_id}", status_code=204)
def delete_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a company. Admin/Manager only."""
    if current_user.role == "SALES_REP":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(company)
    db.commit()


@router.get("/{company_id}/contacts", response_model=List[ContactResponse])
def get_company_contacts(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all contacts for a company."""
    contacts = db.query(Contact).filter(Contact.company_id == company_id).all()
    result = []
    for c in contacts:
        r = ContactResponse.model_validate(c)
        if c.company:
            r.company_name = c.company.name
        result.append(r)
    return result


@router.get("/{company_id}/activities", response_model=List[ActivityResponse])
def get_company_activities(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get recent activities for a company."""
    activities = (
        db.query(Activity)
        .filter(Activity.company_id == company_id)
        .order_by(Activity.created_at.desc())
        .limit(50)
        .all()
    )
    return [ActivityResponse.model_validate(a) for a in activities]
