"""
Dashboard service - analytics calculations from real database data.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.models.lead import Lead, LeadStatus
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.models.activity import Activity
import logging

logger = logging.getLogger(__name__)


class DashboardService:

    def get_stats(self, db: Session) -> Dict[str, Any]:
        """Calculate all dashboard KPIs from live database data."""
        # Lead stats
        total_leads = db.query(Lead).count()
        new_leads = db.query(Lead).filter(Lead.status == LeadStatus.NEW).count()
        qualified_leads = db.query(Lead).filter(Lead.status == LeadStatus.QUALIFIED).count()
        converted_leads = db.query(Lead).filter(Lead.status == LeadStatus.CONVERTED).count()

        # Opportunity stats
        open_opps = db.query(Opportunity).filter(Opportunity.status == OpportunityStatus.OPEN).all()
        won_opps = db.query(Opportunity).filter(Opportunity.status == OpportunityStatus.WON).all()
        lost_opps = db.query(Opportunity).filter(Opportunity.status == OpportunityStatus.LOST).count()

        pipeline_value = sum(o.value or 0 for o in open_opps)
        weighted_pipeline = sum(
            (o.value or 0) * ((o.probability or 0) / 100) for o in open_opps
        )
        won_revenue = sum(o.value or 0 for o in won_opps)

        total_closed = len(won_opps) + lost_opps
        win_rate = (len(won_opps) / total_closed * 100) if total_closed > 0 else 0.0

        # Conversion rate: converted leads / total leads
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0.0

        # Average deal size
        avg_deal_size = (won_revenue / len(won_opps)) if won_opps else 0.0

        # Open tasks
        open_tasks = db.query(Task).filter(Task.status != TaskStatus.COMPLETED).count()
        overdue_tasks = (
            db.query(Task)
            .filter(
                and_(
                    Task.status != TaskStatus.COMPLETED,
                    Task.due_date < datetime.utcnow(),
                )
            )
            .count()
        )

        # Leads this month
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        leads_this_month = (
            db.query(Lead).filter(Lead.created_at >= start_of_month).count()
        )

        return {
            "total_leads": total_leads,
            "new_leads": new_leads,
            "qualified_leads": qualified_leads,
            "converted_leads": converted_leads,
            "leads_this_month": leads_this_month,
            "open_opportunities": len(open_opps),
            "pipeline_value": round(pipeline_value, 2),
            "weighted_pipeline": round(weighted_pipeline, 2),
            "won_revenue": round(won_revenue, 2),
            "win_rate": round(win_rate, 1),
            "conversion_rate": round(conversion_rate, 1),
            "avg_deal_size": round(avg_deal_size, 2),
            "open_tasks": open_tasks,
            "overdue_tasks": overdue_tasks,
        }

    def get_charts_data(self, db: Session) -> Dict[str, Any]:
        """Return data for all dashboard charts."""
        # 1. Leads over last 6 months
        leads_over_time = self._leads_by_month(db, months=6)

        # 2. Revenue by month (won opportunities)
        revenue_by_month = self._revenue_by_month(db, months=6)

        # 3. Pipeline by stage
        pipeline_by_stage = self._pipeline_by_stage(db)

        # 4. Lead sources distribution
        lead_sources = self._lead_sources(db)

        # 5. Opportunity status breakdown
        opp_status = self._opportunity_status(db)

        # 6. Sales rep performance
        rep_performance = self._rep_performance(db)

        return {
            "leads_over_time": leads_over_time,
            "revenue_by_month": revenue_by_month,
            "pipeline_by_stage": pipeline_by_stage,
            "lead_sources": lead_sources,
            "opportunity_status": opp_status,
            "rep_performance": rep_performance,
        }

    def _leads_by_month(self, db: Session, months: int = 6) -> List[Dict]:
        results = []
        now = datetime.utcnow()
        for i in range(months - 1, -1, -1):
            target = now - timedelta(days=30 * i)
            count = (
                db.query(Lead)
                .filter(
                    extract("year", Lead.created_at) == target.year,
                    extract("month", Lead.created_at) == target.month,
                )
                .count()
            )
            results.append({
                "month": target.strftime("%b %Y"),
                "leads": count,
            })
        return results

    def _revenue_by_month(self, db: Session, months: int = 6) -> List[Dict]:
        results = []
        now = datetime.utcnow()
        for i in range(months - 1, -1, -1):
            target = now - timedelta(days=30 * i)
            opps = (
                db.query(Opportunity)
                .filter(
                    Opportunity.status == OpportunityStatus.WON,
                    extract("year", Opportunity.updated_at) == target.year,
                    extract("month", Opportunity.updated_at) == target.month,
                )
                .all()
            )
            revenue = sum(o.value or 0 for o in opps)
            results.append({
                "month": target.strftime("%b %Y"),
                "revenue": round(revenue, 2),
                "deals": len(opps),
            })
        return results

    def _pipeline_by_stage(self, db: Session) -> List[Dict]:
        from app.models.pipeline import PipelineStage
        stages = db.query(PipelineStage).order_by(PipelineStage.order).all()
        results = []
        for stage in stages:
            opps = (
                db.query(Opportunity)
                .filter(
                    Opportunity.stage_id == stage.id,
                    Opportunity.status == OpportunityStatus.OPEN,
                )
                .all()
            )
            value = sum(o.value or 0 for o in opps)
            results.append({
                "stage": stage.name,
                "count": len(opps),
                "value": round(value, 2),
                "color": stage.color,
            })
        return results

    def _lead_sources(self, db: Session) -> List[Dict]:
        results = (
            db.query(Lead.source, func.count(Lead.id).label("count"))
            .group_by(Lead.source)
            .all()
        )
        return [
            {"source": r.source or "OTHER", "count": r.count}
            for r in results
        ]

    def _opportunity_status(self, db: Session) -> List[Dict]:
        results = (
            db.query(Opportunity.status, func.count(Opportunity.id).label("count"))
            .group_by(Opportunity.status)
            .all()
        )
        return [{"status": r.status, "count": r.count} for r in results]

    def _rep_performance(self, db: Session) -> List[Dict]:
        users = db.query(User).filter(User.is_active == True).all()
        performance = []
        for user in users:
            leads = db.query(Lead).filter(Lead.owner_id == user.id).count()
            won = (
                db.query(Opportunity)
                .filter(
                    Opportunity.owner_id == user.id,
                    Opportunity.status == OpportunityStatus.WON,
                )
                .all()
            )
            revenue = sum(o.value or 0 for o in won)
            performance.append({
                "name": user.full_name,
                "leads": leads,
                "won_deals": len(won),
                "revenue": round(revenue, 2),
            })
        return sorted(performance, key=lambda x: x["revenue"], reverse=True)


dashboard_service = DashboardService()
