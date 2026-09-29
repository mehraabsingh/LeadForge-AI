from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.db.database import get_db
from app.schemas.pipeline import PipelineResponse, PipelineStageResponse
from app.core.security import get_current_user
from app.models.user import User
from app.models.pipeline import Pipeline, PipelineStage
from app.models.opportunity import Opportunity, OpportunityStatus

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


@router.get("", response_model=List[PipelineResponse])
def list_pipelines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all pipelines with their stages and opportunity counts."""
    pipelines = (
        db.query(Pipeline)
        .options(joinedload(Pipeline.stages))
        .order_by(Pipeline.is_default.desc())
        .all()
    )
    results = []
    for pipeline in pipelines:
        stages = []
        for stage in sorted(pipeline.stages, key=lambda s: s.order):
            opps = (
                db.query(Opportunity)
                .filter(
                    Opportunity.stage_id == stage.id,
                    Opportunity.status == OpportunityStatus.OPEN,
                )
                .all()
            )
            stage_value = sum(o.value or 0 for o in opps)
            sr = PipelineStageResponse.model_validate(stage)
            sr.opportunity_count = len(opps)
            sr.stage_value = round(stage_value, 2)
            stages.append(sr)

        pr = PipelineResponse.model_validate(pipeline)
        pr.stages = stages
        results.append(pr)
    return results


@router.get("/{pipeline_id}", response_model=PipelineResponse)
def get_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pipeline = (
        db.query(Pipeline)
        .options(joinedload(Pipeline.stages))
        .filter(Pipeline.id == pipeline_id)
        .first()
    )
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    stages = []
    for stage in sorted(pipeline.stages, key=lambda s: s.order):
        opps = (
            db.query(Opportunity)
            .filter(
                Opportunity.stage_id == stage.id,
                Opportunity.status == OpportunityStatus.OPEN,
            )
            .all()
        )
        sr = PipelineStageResponse.model_validate(stage)
        sr.opportunity_count = len(opps)
        sr.stage_value = round(sum(o.value or 0 for o in opps), 2)
        stages.append(sr)

    pr = PipelineResponse.model_validate(pipeline)
    pr.stages = stages
    return pr
