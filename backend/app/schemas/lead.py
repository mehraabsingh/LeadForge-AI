from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.lead import LeadStatus, LeadPriority, LeadSource


class LeadCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    source: Optional[LeadSource] = LeadSource.OTHER
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    estimated_value: Optional[float] = None
    status: Optional[LeadStatus] = LeadStatus.NEW
    priority: Optional[LeadPriority] = LeadPriority.MEDIUM
    description: Optional[str] = None
    owner_id: Optional[str] = None
    company_id: Optional[str] = None


class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    source: Optional[LeadSource] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    estimated_value: Optional[float] = None
    status: Optional[LeadStatus] = None
    priority: Optional[LeadPriority] = None
    score: Optional[int] = None
    score_label: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None
    company_id: Optional[str] = None


class LeadOwnerInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    full_name: str
    email: str


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    first_name: str
    last_name: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    source: Optional[LeadSource] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    estimated_value: Optional[float] = None
    status: LeadStatus
    priority: LeadPriority
    score: Optional[int] = None
    score_label: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None
    owner: Optional[LeadOwnerInfo] = None
    company_id: Optional[str] = None
    activity_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class LeadListResponse(BaseModel):
    leads: List[LeadResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
