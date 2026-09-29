"""
Deterministic fallback AI engine.
Works without any API key. Uses rule-based scoring and templated outputs.
This ensures the project runs locally for evaluation without external API dependencies.
"""
from typing import Dict, Any, List
from datetime import datetime
from app.ai.base import BaseAIService
import logging

logger = logging.getLogger(__name__)


class FallbackAIService(BaseAIService):
    """
    Deterministic rule-based AI service.
    Used when no AI provider is configured or as a circuit breaker fallback.
    """

    @property
    def provider_name(self) -> str:
        return "fallback"

    def score_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based lead scoring 0-100."""
        score = 0
        factors = []

        # Company size scoring (0-20)
        company_size = lead_data.get("company_size", "")
        size_scores = {
            "1-10": 5,
            "11-50": 10,
            "51-200": 15,
            "201-500": 18,
            "500+": 20,
            "1000+": 20,
        }
        size_score = size_scores.get(company_size, 5)
        score += size_score
        if size_score >= 15:
            factors.append(f"Large company size ({company_size}) indicates higher budget potential")

        # Estimated value scoring (0-25)
        estimated_value = lead_data.get("estimated_value") or 0
        if estimated_value >= 100000:
            score += 25
            factors.append(f"High estimated deal value (${estimated_value:,.0f})")
        elif estimated_value >= 50000:
            score += 20
            factors.append(f"Strong estimated deal value (${estimated_value:,.0f})")
        elif estimated_value >= 10000:
            score += 12
            factors.append(f"Moderate estimated deal value (${estimated_value:,.0f})")
        elif estimated_value > 0:
            score += 6

        # Lead source scoring (0-15)
        source = lead_data.get("source", "")
        source_scores = {
            "REFERRAL": 15,
            "PARTNER": 12,
            "LINKEDIN": 10,
            "CONFERENCE": 10,
            "WEBSITE": 8,
            "COLD_OUTREACH": 5,
            "ADVERTISEMENT": 6,
            "OTHER": 3,
        }
        source_score = source_scores.get(source, 3)
        score += source_score
        if source_score >= 10:
            factors.append(f"High-quality lead source: {source}")

        # Industry scoring (0-10)
        high_value_industries = [
            "Technology", "Finance", "Healthcare", "SaaS", "Enterprise Software",
            "Financial Services", "Pharmaceuticals", "Consulting",
        ]
        industry = lead_data.get("industry", "")
        if any(ind.lower() in industry.lower() for ind in high_value_industries):
            score += 10
            factors.append(f"High-value industry: {industry}")
        else:
            score += 3

        # Contact info completeness (0-10)
        completeness_score = 0
        if lead_data.get("email"):
            completeness_score += 3
        if lead_data.get("phone"):
            completeness_score += 3
        if lead_data.get("job_title"):
            completeness_score += 2
        if lead_data.get("location"):
            completeness_score += 2
        score += completeness_score
        if completeness_score >= 8:
            factors.append("Complete contact information improves reachability")

        # Job title / seniority scoring (0-20)
        job_title = (lead_data.get("job_title") or "").lower()
        executive_titles = ["ceo", "cto", "cfo", "coo", "vp", "president", "founder", "director", "head of"]
        manager_titles = ["manager", "lead", "senior", "principal"]
        if any(t in job_title for t in executive_titles):
            score += 20
            factors.append("Executive-level contact has decision-making authority")
        elif any(t in job_title for t in manager_titles):
            score += 12
            factors.append("Manager-level contact influences purchasing decisions")
        else:
            score += 5

        # Clamp to 0-100
        score = min(100, max(0, score))

        # Determine label
        if score >= 70:
            label = "HOT"
            explanation = f"This lead scores {score}/100, indicating strong deal potential. The combination of company profile, deal value, and lead source makes this a high-priority opportunity."
            recommended_action = "Schedule a discovery call within 24 hours. Prepare a tailored presentation based on their industry needs."
        elif score >= 40:
            label = "WARM"
            explanation = f"This lead scores {score}/100, showing moderate potential. There are positive signals but some gaps in qualification data."
            recommended_action = "Send a personalized outreach email and follow up in 2-3 days. Try to gather more qualification information."
        else:
            label = "COLD"
            explanation = f"This lead scores {score}/100, indicating lower immediate potential. This may be an early-stage prospect or require more nurturing."
            recommended_action = "Add to a nurture sequence. Check in monthly and look for trigger events that might increase their readiness."

        if not factors:
            factors = ["Limited information available for scoring", "Consider gathering more qualification data"]

        return {
            "lead_id": lead_data.get("id", ""),
            "score": score,
            "label": label,
            "explanation": explanation,
            "key_factors": factors[:4],  # Top 4 factors
            "recommended_action": recommended_action,
            "provider": self.provider_name,
        }

    def summarize_lead(
        self, lead_data: Dict[str, Any], activities: list, notes: list
    ) -> Dict[str, Any]:
        """Generate a structured lead summary."""
        name = lead_data.get("full_name") or f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}".strip()
        company = lead_data.get("company", "Unknown Company")
        status = lead_data.get("status", "NEW")
        score = lead_data.get("score")
        estimated_value = lead_data.get("estimated_value")

        profile_summary = (
            f"{name} is a {lead_data.get('job_title', 'professional')} at {company}. "
            f"This lead was sourced via {lead_data.get('source', 'unknown channel')} "
            f"and is currently in {status} status."
        )
        if lead_data.get("industry"):
            profile_summary += f" They operate in the {lead_data['industry']} industry."
        if lead_data.get("location"):
            profile_summary += f" Located in {lead_data['location']}."

        activity_count = len(activities)
        if activity_count == 0:
            activity_summary = "No activities have been recorded for this lead yet. Initial outreach is recommended."
        elif activity_count == 1:
            activity_summary = f"One activity has been recorded. The lead has been contacted once."
        else:
            activity_types = set(a.get("type", "") for a in activities)
            activity_summary = (
                f"{activity_count} activities recorded including "
                f"{', '.join(activity_types).lower()}. The lead has had regular engagement."
            )

        pipeline_status = f"Lead is in {status} stage."
        if estimated_value:
            pipeline_status += f" Estimated deal value: ${estimated_value:,.2f}."
        if score:
            pipeline_status += f" AI lead score: {score}/100."

        # Risk assessment
        key_risks = []
        if activity_count == 0:
            key_risks.append("No contact attempts recorded — lead may go cold")
        if not lead_data.get("email") and not lead_data.get("phone"):
            key_risks.append("No contact information available")
        if status in ["NEW", "CONTACTED"] and activity_count > 3:
            key_risks.append("Multiple contact attempts without qualification progress")
        if not estimated_value:
            key_risks.append("Deal value not yet established")
        if not key_risks:
            key_risks = ["No critical risks identified at this time"]

        # Recommended next step
        status_actions = {
            "NEW": "Initiate first contact via email or phone. Introduce your solution and schedule a discovery call.",
            "CONTACTED": "Follow up on previous outreach. Try to schedule a meeting to qualify the opportunity.",
            "QUALIFIED": "Prepare and send a tailored proposal. Address their specific pain points.",
            "UNQUALIFIED": "Consider if there is a future opportunity or if this lead should be closed.",
            "CONVERTED": "Focus on successful onboarding and relationship management.",
            "LOST": "Send a polite closing email. Mark for re-engagement in 6 months.",
        }
        recommended_next_step = status_actions.get(
            status, "Review the lead profile and determine the appropriate next action."
        )

        return {
            "lead_id": lead_data.get("id", ""),
            "profile_summary": profile_summary,
            "activity_summary": activity_summary,
            "pipeline_status": pipeline_status,
            "estimated_value": estimated_value,
            "key_risks": key_risks,
            "recommended_next_step": recommended_next_step,
            "overall_assessment": f"This lead requires {'immediate attention' if (score or 0) >= 70 else 'regular follow-up' if (score or 0) >= 40 else 'a nurture approach'}.",
            "provider": self.provider_name,
        }

    def generate_follow_up_email(
        self, lead_data: Dict[str, Any], email_type: str
    ) -> Dict[str, Any]:
        """Generate professional follow-up email templates."""
        name = lead_data.get("first_name", "there")
        company = lead_data.get("company", "your company")
        job_title = lead_data.get("job_title", "")

        templates = {
            "first_outreach": {
                "subject": f"Quick question about {company}'s growth strategy",
                "body": f"""Hi {name},

I came across {company} and was impressed by what you're building. I wanted to reach out because we've been helping similar companies in the {lead_data.get('industry', 'your industry')} space streamline their sales processes and drive revenue growth.

I'd love to learn more about your current challenges and share how LeadForge AI has helped teams like yours:
• Increase qualified pipeline by 35% on average
• Reduce time-to-close by 20%
• Get AI-powered insights on which deals to prioritize

Would you be open to a 15-minute call this week or next? I promise to respect your time and only continue the conversation if there's a genuine fit.

Best regards,
[Your Name]
LeadForge AI""",
            },
            "follow_up": {
                "subject": f"Re: Quick question about {company}'s growth strategy",
                "body": f"""Hi {name},

I wanted to follow up on my previous message — I know your inbox is busy.

I genuinely believe there's something worth exploring here. We've recently helped a company in your space solve [specific problem], and the results have been impressive.

Would it be easier to connect via a quick 15-minute call, or would you prefer I send over some relevant case studies first?

Looking forward to hearing from you.

Best,
[Your Name]
LeadForge AI""",
            },
            "proposal_follow_up": {
                "subject": f"Following up on the LeadForge AI proposal for {company}",
                "body": f"""Hi {name},

I'm checking in on the proposal we sent over. I understand decisions like this take time, and I want to make sure you have everything you need to move forward.

A few things I wanted to highlight:
• [Key benefit 1 relevant to their situation]
• [Key benefit 2]
• Our implementation team has helped similar companies get up and running in under 2 weeks

Is there anything in the proposal you'd like to discuss or clarify? Or if timing has changed on your end, I'd love to know when might be a better time to revisit.

Best regards,
[Your Name]
LeadForge AI""",
            },
            "re_engagement": {
                "subject": f"Things have changed at LeadForge AI — worth a second look?",
                "body": f"""Hi {name},

It's been a while since we last connected, and a lot has changed since then. I wanted to reach out because we've made significant improvements that might be more relevant to where {company} is today.

Since we last spoke:
• [New feature/improvement 1]
• [New feature/improvement 2]
• We've onboarded several companies in your industry with great results

Would you be open to a brief conversation to see if our timing is better now? No pressure — just a quick check-in.

Best,
[Your Name]
LeadForge AI""",
            },
        }

        template = templates.get(email_type, templates["first_outreach"])

        return {
            "subject": template["subject"],
            "body": template["body"],
            "email_type": email_type,
            "provider": self.provider_name,
        }

    def generate_sales_insights(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable sales insights from pipeline data."""
        insights = []
        now = datetime.utcnow()

        leads = pipeline_data.get("leads", [])
        opportunities = pipeline_data.get("opportunities", [])
        stale_lead_ids = []
        no_contact_ids = []
        high_value_stale = []

        for lead in leads:
            activity_count = lead.get("activity_count", 0)
            status = lead.get("status", "")
            estimated_value = lead.get("estimated_value") or 0

            if activity_count == 0 and status == "NEW":
                no_contact_ids.append(lead.get("id"))
            elif status in ["CONTACTED"] and activity_count == 0:
                stale_lead_ids.append(lead.get("id"))

            # High-value lead with no recent activity
            if estimated_value >= 50000 and activity_count == 0:
                high_value_stale.append(lead.get("id"))

        if no_contact_ids:
            insights.append({
                "title": "Leads Requiring First Contact",
                "description": f"{len(no_contact_ids)} new lead(s) have never been contacted. These represent untapped pipeline opportunities.",
                "severity": "high",
                "action": "Initiate first outreach to these leads today to prevent them from going cold.",
                "lead_ids": no_contact_ids[:5],
                "opportunity_ids": None,
            })

        if high_value_stale:
            insights.append({
                "title": "High-Value Leads Without Activity",
                "description": f"{len(high_value_stale)} high-value lead(s) with $50K+ potential have no recorded activities.",
                "severity": "critical",
                "action": "These leads should be your top priority. Schedule calls or send personalized outreach immediately.",
                "lead_ids": high_value_stale[:5],
                "opportunity_ids": None,
            })

        # Opportunity insights
        open_opps = [o for o in opportunities if o.get("status") == "OPEN"]
        won_opps = [o for o in opportunities if o.get("status") == "WON"]
        lost_opps = [o for o in opportunities if o.get("status") == "LOST"]

        if open_opps:
            total_opp_value = sum(o.get("value") or 0 for o in open_opps)
            insights.append({
                "title": "Active Pipeline Overview",
                "description": f"You have {len(open_opps)} open opportunities worth ${total_opp_value:,.0f} in total pipeline value.",
                "severity": "low",
                "action": "Review each opportunity's probability and expected close date to prioritize effort.",
                "lead_ids": None,
                "opportunity_ids": [o.get("id") for o in open_opps[:3]],
            })

        total_opps = len(opportunities)
        if total_opps > 0:
            win_rate = len(won_opps) / total_opps * 100
            if win_rate < 20:
                insights.append({
                    "title": "Low Win Rate Alert",
                    "description": f"Your win rate is {win_rate:.1f}%. Industry average is typically 20-30%.",
                    "severity": "medium",
                    "action": "Review lost deals for common patterns. Consider refining your qualification criteria and discovery process.",
                    "lead_ids": None,
                    "opportunity_ids": None,
                })

        # Qualified leads without opportunities
        qualified_no_opp = [
            l for l in leads
            if l.get("status") == "QUALIFIED"
        ]
        if qualified_no_opp:
            insights.append({
                "title": "Qualified Leads Need Opportunities",
                "description": f"{len(qualified_no_opp)} lead(s) are marked as qualified but don't have associated opportunities in the pipeline.",
                "severity": "medium",
                "action": "Create opportunities for these qualified leads to properly track them through your sales pipeline.",
                "lead_ids": [l.get("id") for l in qualified_no_opp[:5]],
                "opportunity_ids": None,
            })

        if not insights:
            insights.append({
                "title": "Pipeline Looking Healthy",
                "description": "No critical issues detected in your current pipeline. Keep up the good work!",
                "severity": "low",
                "action": "Continue regular follow-ups and focus on closing open opportunities.",
                "lead_ids": None,
                "opportunity_ids": None,
            })

        return {
            "insights": insights,
            "generated_at": now.isoformat(),
            "provider": self.provider_name,
            "total_insights": len(insights),
        }
