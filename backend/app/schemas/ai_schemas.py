from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class EmailType(str, Enum):
    FIRST_OUTREACH = "first_outreach"
    FOLLOW_UP = "follow_up"
    PROPOSAL_FOLLOW_UP = "proposal_follow_up"
    RE_ENGAGEMENT = "re_engagement"


class LeadScoreResponse(BaseModel):
    lead_id: str
    score: int  # 0-100
    label: str  # HOT, WARM, COLD
    explanation: str
    key_factors: List[str]
    recommended_action: str
    provider: str


class LeadSummaryResponse(BaseModel):
    lead_id: str
    profile_summary: str
    activity_summary: str
    pipeline_status: str
    estimated_value: Optional[float] = None
    key_risks: List[str]
    recommended_next_step: str
    overall_assessment: str
    provider: str


class FollowUpEmailResponse(BaseModel):
    subject: str
    body: str
    email_type: EmailType
    provider: str


class InsightItem(BaseModel):
    title: str
    description: str
    severity: str  # low, medium, high, critical
    action: str
    lead_ids: Optional[List[str]] = None
    opportunity_ids: Optional[List[str]] = None


class SalesInsightsResponse(BaseModel):
    insights: List[InsightItem]
    generated_at: str
    provider: str
    total_insights: int
