"""
Tests for dashboard analytics calculations.
"""
import pytest
from app.models.pipeline import Pipeline, PipelineStage
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.lead import Lead, LeadStatus
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.services.dashboard_service import DashboardService
import uuid


def create_test_pipeline(db):
    pipeline = Pipeline(
        id=str(uuid.uuid4()), name="Test Pipeline", is_default=True
    )
    db.add(pipeline)
    db.flush()
    stage1 = PipelineStage(
        id=str(uuid.uuid4()), name="Open", order=0, probability=50, pipeline_id=pipeline.id
    )
    stage2 = PipelineStage(
        id=str(uuid.uuid4()), name="Won", order=1, probability=100, pipeline_id=pipeline.id
    )
    stage3 = PipelineStage(
        id=str(uuid.uuid4()), name="Lost", order=2, probability=0, pipeline_id=pipeline.id
    )
    db.add_all([stage1, stage2, stage3])
    db.flush()
    return pipeline, stage1, stage2, stage3


def create_test_user(db):
    user = User(
        id=str(uuid.uuid4()),
        email=f"rep{uuid.uuid4().hex[:6]}@test.com",
        hashed_password=hash_password("Test@123456"),
        first_name="Sales", last_name="Rep",
        role=UserRole.SALES_REP, is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def test_pipeline_value_calculation(db, db_setup):
    """Pipeline value should sum only OPEN opportunity values."""
    pipeline, open_stage, won_stage, lost_stage = create_test_pipeline(db)
    user = create_test_user(db)

    # Add some opportunities
    opp1 = Opportunity(
        id=str(uuid.uuid4()), title="Deal 1", value=100000, probability=50,
        status=OpportunityStatus.OPEN, pipeline_id=pipeline.id,
        stage_id=open_stage.id, owner_id=user.id,
    )
    opp2 = Opportunity(
        id=str(uuid.uuid4()), title="Deal 2 (Won)", value=50000, probability=100,
        status=OpportunityStatus.WON, pipeline_id=pipeline.id,
        stage_id=won_stage.id, owner_id=user.id,
    )
    opp3 = Opportunity(
        id=str(uuid.uuid4()), title="Deal 3", value=75000, probability=60,
        status=OpportunityStatus.OPEN, pipeline_id=pipeline.id,
        stage_id=open_stage.id, owner_id=user.id,
    )
    db.add_all([opp1, opp2, opp3])
    db.commit()

    svc = DashboardService()
    stats = svc.get_stats(db)

    # Pipeline value = sum of OPEN opportunities only
    assert stats["pipeline_value"] == 175000.0  # 100k + 75k
    assert stats["won_revenue"] == 50000.0


def test_weighted_pipeline_calculation(db, db_setup):
    """Weighted pipeline = value * (probability / 100)."""
    pipeline, open_stage, won_stage, _ = create_test_pipeline(db)
    user = create_test_user(db)

    opp = Opportunity(
        id=str(uuid.uuid4()), title="Deal", value=100000, probability=40,
        status=OpportunityStatus.OPEN, pipeline_id=pipeline.id,
        stage_id=open_stage.id, owner_id=user.id,
    )
    db.add(opp)
    db.commit()

    svc = DashboardService()
    stats = svc.get_stats(db)
    assert stats["weighted_pipeline"] == 40000.0  # 100000 * 0.40


def test_win_rate_calculation(db, db_setup):
    """Win rate = won / (won + lost) * 100."""
    pipeline, open_stage, won_stage, lost_stage = create_test_pipeline(db)
    user = create_test_user(db)

    db.add(Opportunity(
        id=str(uuid.uuid4()), title="Won Deal", value=50000, probability=100,
        status=OpportunityStatus.WON, pipeline_id=pipeline.id,
        stage_id=won_stage.id, owner_id=user.id,
    ))
    db.add(Opportunity(
        id=str(uuid.uuid4()), title="Lost Deal", value=50000, probability=0,
        status=OpportunityStatus.LOST, pipeline_id=pipeline.id,
        stage_id=lost_stage.id, owner_id=user.id,
    ))
    db.add(Opportunity(
        id=str(uuid.uuid4()), title="Lost Deal 2", value=50000, probability=0,
        status=OpportunityStatus.LOST, pipeline_id=pipeline.id,
        stage_id=lost_stage.id, owner_id=user.id,
    ))
    db.commit()

    svc = DashboardService()
    stats = svc.get_stats(db)
    # 1 won / (1 + 2) = 33.3%
    assert stats["win_rate"] == pytest.approx(33.3, abs=0.2)


def test_dashboard_stats_with_empty_db(db, db_setup):
    """Dashboard should return zeros gracefully on empty database."""
    svc = DashboardService()
    stats = svc.get_stats(db)
    assert stats["total_leads"] == 0
    assert stats["pipeline_value"] == 0
    assert stats["win_rate"] == 0.0
    assert stats["won_revenue"] == 0


def test_lead_counts(db, db_setup):
    """Lead counts should reflect actual database state."""
    user = create_test_user(db)
    pipeline, stage, _, _ = create_test_pipeline(db)

    # Create leads in different statuses
    for status in [LeadStatus.NEW, LeadStatus.NEW, LeadStatus.QUALIFIED, LeadStatus.CONVERTED]:
        lead = Lead(
            id=str(uuid.uuid4()),
            first_name="Test", last_name="Lead",
            email=f"{uuid.uuid4().hex}@test.com",
            status=status, priority="MEDIUM",
            owner_id=user.id,
        )
        db.add(lead)
    db.commit()

    svc = DashboardService()
    stats = svc.get_stats(db)
    assert stats["total_leads"] == 4
    assert stats["new_leads"] == 2
    assert stats["qualified_leads"] == 1
    assert stats["converted_leads"] == 1
