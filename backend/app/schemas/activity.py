from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.activity import ActivityType


class ActivityCreate(BaseModel):
    type: ActivityType
    title: str
    description: Optional[str] = None
    outcome: Optional[str] = None
    lead_id: Optional[str] = None
    company_id: Optional[str] = None
    opportunity_id: Optional[str] = None


class ActivityUserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    full_name: str


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: ActivityType
    title: str
    description: Optional[str] = None
    outcome: Optional[str] = None
    user_id: Optional[str] = None
    user: Optional[ActivityUserInfo] = None
    lead_id: Optional[str] = None
    company_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
