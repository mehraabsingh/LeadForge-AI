"""
Tests for AI fallback engine - no API key required.
"""
import pytest
from app.ai.fallback import FallbackAIService


@pytest.fixture
def ai():
    return FallbackAIService()


@pytest.fixture
def hot_lead_data():
    return {
        "id": "test-lead-1",
        "full_name": "Jane Smith",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@bigcorp.com",
        "phone": "+1-415-555-0100",
        "company": "BigCorp Enterprise",
        "job_title": "CTO",
        "source": "REFERRAL",
        "industry": "Technology",
        "company_size": "500+",
        "location": "San Francisco, CA",
        "estimated_value": 150000,
        "status": "QUALIFIED",
    }


@pytest.fixture
def cold_lead_data():
    return {
        "id": "test-lead-2",
        "full_name": "John Doe",
        "first_name": "John",
        "last_name": "Doe",
        "email": None,
        "phone": None,
        "company": "Small Biz",
        "job_title": "Owner",
        "source": "COLD_OUTREACH",
        "industry": "Other",
        "company_size": "1-10",
        "location": None,
        "estimated_value": 2000,
        "status": "NEW",
    }


class TestFallbackLeadScoring:

    def test_hot_lead_scores_high(self, ai, hot_lead_data):
        """HOT lead should score >= 70."""
        result = ai.score_lead(hot_lead_data)
        assert result["score"] >= 70
        assert result["label"] == "HOT"
        assert result["provider"] == "fallback"

    def test_cold_lead_scores_low(self, ai, cold_lead_data):
        """Cold lead with poor signals should score < 40."""
        result = ai.score_lead(cold_lead_data)
        assert result["score"] < 40
        assert result["label"] == "COLD"

    def test_score_is_bounded(self, ai, hot_lead_data):
        """Score must always be between 0 and 100."""
        result = ai.score_lead(hot_lead_data)
        assert 0 <= result["score"] <= 100

    def test_result_has_required_fields(self, ai, hot_lead_data):
        """Score result must include all required fields."""
        result = ai.score_lead(hot_lead_data)
        required = ["lead_id", "score", "label", "explanation", "key_factors", "recommended_action", "provider"]
        for field in required:
            assert field in result, f"Missing field: {field}"

    def test_key_factors_are_list(self, ai, hot_lead_data):
        """key_factors must be a non-empty list."""
        result = ai.score_lead(hot_lead_data)
        assert isinstance(result["key_factors"], list)
        assert len(result["key_factors"]) > 0

    def test_warm_lead_classification(self, ai):
        """Medium-quality lead should be WARM."""
        lead_data = {
            "id": "warm-lead",
            "full_name": "Test Person",
            "email": "test@medium.com",
            "phone": "+1-555-0000",
            "company": "Medium Co",
            "job_title": "Manager",
            "source": "WEBSITE",
            "industry": "Retail",
            "company_size": "51-200",
            "location": "Chicago, IL",
            "estimated_value": 25000,
            "status": "CONTACTED",
        }
        result = ai.score_lead(lead_data)
        assert 40 <= result["score"] < 70
        assert result["label"] == "WARM"

    def test_executive_title_increases_score(self, ai):
        """Executive title should increase score more than non-executive."""
        base_data = {
            "id": "test",
            "full_name": "Test Person",
            "email": "test@corp.com",
            "phone": "+1-555-0000",
            "company": "Corp",
            "source": "WEBSITE",
            "industry": "Technology",
            "company_size": "51-200",
            "location": "NYC",
            "estimated_value": 20000,
            "status": "NEW",
        }
        exec_data = {**base_data, "job_title": "CEO"}
        non_exec_data = {**base_data, "job_title": "Analyst"}

        exec_result = ai.score_lead(exec_data)
        non_exec_result = ai.score_lead(non_exec_data)
        assert exec_result["score"] > non_exec_result["score"]


class TestFallbackEmailGeneration:

    def test_generates_first_outreach_email(self, ai, hot_lead_data):
        """Should generate a first outreach email."""
        result = ai.generate_follow_up_email(hot_lead_data, "first_outreach")
        assert "subject" in result
        assert "body" in result
        assert result["provider"] == "fallback"
        assert len(result["subject"]) > 0
        assert len(result["body"]) > 0

    def test_generates_all_email_types(self, ai, hot_lead_data):
        """Should generate emails for all email types."""
        email_types = ["first_outreach", "follow_up", "proposal_follow_up", "re_engagement"]
        for email_type in email_types:
            result = ai.generate_follow_up_email(hot_lead_data, email_type)
            assert result["subject"], f"Empty subject for {email_type}"
            assert result["body"], f"Empty body for {email_type}"

    def test_email_includes_company_name(self, ai, hot_lead_data):
        """Email body should reference the lead's company."""
        result = ai.generate_follow_up_email(hot_lead_data, "first_outreach")
        # The company name or first name should appear
        assert hot_lead_data["first_name"] in result["body"] or hot_lead_data["company"] in result["subject"]


class TestFallbackLeadSummary:

    def test_summary_has_required_fields(self, ai, hot_lead_data):
        """Summary result must include all required fields."""
        result = ai.summarize_lead(hot_lead_data, [], [])
        required = [
            "lead_id", "profile_summary", "activity_summary",
            "pipeline_status", "key_risks", "recommended_next_step",
            "overall_assessment", "provider"
        ]
        for field in required:
            assert field in result, f"Missing field: {field}"

    def test_no_activity_flagged_as_risk(self, ai, cold_lead_data):
        """Lead with no activities should have a risk about no contact."""
        result = ai.summarize_lead(cold_lead_data, [], [])
        risks_text = " ".join(result["key_risks"]).lower()
        assert "contact" in risks_text or "activity" in risks_text or "no" in risks_text

    def test_activity_count_reflected_in_summary(self, ai, hot_lead_data):
        """Activity count should be reflected in the activity summary."""
        activities = [
            {"type": "CALL", "title": "Discovery call", "created_at": "2024-01-01"},
            {"type": "EMAIL", "title": "Follow-up email", "created_at": "2024-01-02"},
        ]
        result = ai.summarize_lead(hot_lead_data, activities, [])
        assert "2" in result["activity_summary"] or "two" in result["activity_summary"].lower()


class TestFallbackSalesInsights:

    def test_no_contact_leads_flagged(self, ai):
        """NEW leads with no activities should be flagged."""
        pipeline_data = {
            "leads": [
                {"id": "l1", "status": "NEW", "estimated_value": 50000, "activity_count": 0},
                {"id": "l2", "status": "NEW", "estimated_value": 30000, "activity_count": 0},
            ],
            "opportunities": [],
        }
        result = ai.generate_sales_insights(pipeline_data)
        assert result["total_insights"] > 0

        titles = [i["title"] for i in result["insights"]]
        assert any("contact" in t.lower() or "first" in t.lower() for t in titles)

    def test_high_value_leads_flagged(self, ai):
        """High-value leads with no activities should be flagged as critical."""
        pipeline_data = {
            "leads": [
                {"id": "l1", "status": "NEW", "estimated_value": 100000, "activity_count": 0},
            ],
            "opportunities": [],
        }
        result = ai.generate_sales_insights(pipeline_data)
        critical_insights = [i for i in result["insights"] if i["severity"] == "critical"]
        assert len(critical_insights) > 0

    def test_insights_have_required_fields(self, ai):
        """Each insight must have required fields."""
        pipeline_data = {"leads": [], "opportunities": []}
        result = ai.generate_sales_insights(pipeline_data)
        for insight in result["insights"]:
            assert "title" in insight
            assert "description" in insight
            assert "severity" in insight
            assert "action" in insight
