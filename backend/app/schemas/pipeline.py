from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class PipelineStageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    order: int
    color: Optional[str] = None
    probability: Optional[float] = None
    pipeline_id: str
    opportunity_count: Optional[int] = None
    stage_value: Optional[float] = None


class PipelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    is_default: bool
    stages: List[PipelineStageResponse] = []
    created_at: datetime
    updated_at: datetime
