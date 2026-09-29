"""Pydantic schemas package."""
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, Token, TokenData, LoginRequest
)
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadListResponse
from app.schemas.pipeline import PipelineResponse, PipelineStageResponse
from app.schemas.opportunity import (
    OpportunityCreate, OpportunityUpdate, OpportunityResponse, OpportunityListResponse
)
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.activity import ActivityCreate, ActivityResponse
from app.schemas.note import NoteCreate, NoteResponse
from app.schemas.ai_schemas import (
    LeadScoreResponse, LeadSummaryResponse, FollowUpEmailResponse,
    SalesInsightsResponse, EmailType
)

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse", "UserListResponse", "Token", "TokenData", "LoginRequest",
    "CompanyCreate", "CompanyUpdate", "CompanyResponse",
    "ContactCreate", "ContactUpdate", "ContactResponse",
    "LeadCreate", "LeadUpdate", "LeadResponse", "LeadListResponse",
    "PipelineResponse", "PipelineStageResponse",
    "OpportunityCreate", "OpportunityUpdate", "OpportunityResponse", "OpportunityListResponse",
    "TaskCreate", "TaskUpdate", "TaskResponse",
    "ActivityCreate", "ActivityResponse",
    "NoteCreate", "NoteResponse",
    "LeadScoreResponse", "LeadSummaryResponse", "FollowUpEmailResponse",
    "SalesInsightsResponse", "EmailType",
]
