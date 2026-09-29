from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class NoteCreate(BaseModel):
    content: str
    lead_id: Optional[str] = None
    company_id: Optional[str] = None
    opportunity_id: Optional[str] = None


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    content: str
    author_id: Optional[str] = None
    author_name: Optional[str] = None
    lead_id: Optional[str] = None
    company_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
