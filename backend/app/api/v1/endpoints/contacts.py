from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.db.database import get_db
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.core.security import get_current_user
from app.models.user import User
from app.models.contact import Contact

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("", response_model=List[ContactResponse])
def list_contacts(
    search: Optional[str] = None,
    company_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Contact).options(joinedload(Contact.company))
    if search:
        term = f"%{search}%"
        query = query.filter(
            Contact.first_name.ilike(term) |
            Contact.last_name.ilike(term) |
            Contact.email.ilike(term)
        )
    if company_id:
        query = query.filter(Contact.company_id == company_id)
    offset = (page - 1) * page_size
    contacts = query.order_by(Contact.first_name).offset(offset).limit(page_size).all()
    result = []
    for c in contacts:
        r = ContactResponse.model_validate(c)
        if c.company:
            r.company_name = c.company.name
        result.append(r)
    return result


@router.post("", response_model=ContactResponse, status_code=201)
def create_contact(
    contact_in: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = Contact(**contact_in.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    r = ContactResponse.model_validate(contact)
    if contact.company:
        r.company_name = contact.company.name
    return r


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = db.query(Contact).options(joinedload(Contact.company)).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    r = ContactResponse.model_validate(contact)
    if contact.company:
        r.company_name = contact.company.name
    return r


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: str,
    contact_in: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    for key, value in contact_in.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)
    db.commit()
    db.refresh(contact)
    r = ContactResponse.model_validate(contact)
    if contact.company:
        r.company_name = contact.company.name
    return r


@router.delete("/{contact_id}", status_code=204)
def delete_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
