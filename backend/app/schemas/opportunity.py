from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from app.models.opportunity import OpportunityStatus


class OpportunityCreate(BaseModel):
    title: str
    description: Optional[str] = None
    value: Optional[float] = 0.0
    probability: Optional[float] = 50.0
    expected_close_date: Optional[date] = None
    notes: Optional[str] = None
    lead_id: Optional[str] = None
    pipeline_id: str
    stage_id: str
    owner_id: Optional[str] = None
    company_id: Optional[str] = None


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    value: Optional[float] = None
    probability: Optional[float] = None
    status: Optional[OpportunityStatus] = None
    expected_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    notes: Optional[str] = None
    stage_id: Optional[str] = None
    owner_id: Optional[str] = None
    company_id: Optional[str] = None


class OpportunityStageInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    color: Optional[str] = None
    order: int


class OpportunityOwnerInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    full_name: str
    email: str


class OpportunityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: Optional[str] = None
    value: Optional[float] = None
    probability: Optional[float] = None
    weighted_value: Optional[float] = None
    status: OpportunityStatus
    expected_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    notes: Optional[str] = None
    lead_id: Optional[str] = None
    pipeline_id: str
    stage_id: str
    stage: Optional[OpportunityStageInfo] = None
    owner_id: Optional[str] = None
    owner: Optional[OpportunityOwnerInfo] = None
    company_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class OpportunityListResponse(BaseModel):
    opportunities: List[OpportunityResponse]
    total: int
    pipeline_value: float
    weighted_value: float
    won_value: float
    win_rate: float
