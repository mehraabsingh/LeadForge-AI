"""
Gemini AI service implementation.
Uses Google Generative AI API for lead scoring, summaries, and emails.
"""
import json
import logging
from typing import Dict, Any
from app.ai.base import BaseAIService
from app.ai.fallback import FallbackAIService

logger = logging.getLogger(__name__)


class GeminiAIService(BaseAIService):
    """Google Gemini AI provider."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._fallback = FallbackAIService()
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("Gemini AI client initialized successfully")
        except ImportError:
            logger.warning("google-generativeai not installed. Install it with: pip install google-generativeai")
            self._model = None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self._model = None

    @property
    def provider_name(self) -> str:
        return "gemini"

    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API and return text response."""
        if not self._model:
            raise RuntimeError("Gemini model not initialized")
        response = self._model.generate_content(prompt)
        return response.text

    def _safe_call(self, prompt: str, fallback_result: Dict) -> Dict:
        """Call Gemini with fallback on any error."""
        try:
            text = self._call_gemini(prompt)
            # Extract JSON from response
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return fallback_result
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}, using fallback")
            return fallback_result

    def score_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        fallback_result = self._fallback.score_lead(lead_data)
        if not self._model:
            return fallback_result

        name = lead_data.get("full_name", "Unknown")
        prompt = f"""
You are a sales expert AI. Score this lead from 0-100 based on their profile.

Lead profile:
- Name: {name}
- Company: {lead_data.get('company', 'Unknown')}
- Job Title: {lead_data.get('job_title', 'Unknown')}
- Industry: {lead_data.get('industry', 'Unknown')}
- Company Size: {lead_data.get('company_size', 'Unknown')}
- Lead Source: {lead_data.get('source', 'Unknown')}
- Estimated Value: ${lead_data.get('estimated_value', 0):,.0f}
- Location: {lead_data.get('location', 'Unknown')}
- Has Email: {bool(lead_data.get('email'))}
- Has Phone: {bool(lead_data.get('phone'))}

Return a JSON object with these exact fields:
{{
  "score": <integer 0-100>,
  "label": <"HOT" | "WARM" | "COLD">,
  "explanation": <string explaining the score>,
  "key_factors": [<list of 3-4 string factors>],
  "recommended_action": <string action to take>
}}
"""
        result = self._safe_call(prompt, fallback_result)
        result["lead_id"] = lead_data.get("id", "")
        result["provider"] = self.provider_name
        return result

    def summarize_lead(
        self, lead_data: Dict[str, Any], activities: list, notes: list
    ) -> Dict[str, Any]:
        fallback_result = self._fallback.summarize_lead(lead_data, activities, notes)
        if not self._model:
            return fallback_result

        activity_text = "\n".join([f"- {a.get('type')}: {a.get('title')}" for a in activities[:10]])
        notes_text = "\n".join([f"- {n.get('content', '')[:200]}" for n in notes[:5]])

        prompt = f"""
You are a CRM AI assistant. Provide a comprehensive summary of this lead.

Lead: {lead_data.get('full_name')} at {lead_data.get('company')}
Job Title: {lead_data.get('job_title')}
Status: {lead_data.get('status')}
Score: {lead_data.get('score')}/100
Estimated Value: ${lead_data.get('estimated_value', 0):,.0f}
Industry: {lead_data.get('industry')}
Source: {lead_data.get('source')}

Recent Activities:
{activity_text or 'No activities yet'}

Notes:
{notes_text or 'No notes yet'}

Return a JSON object:
{{
  "profile_summary": <2-3 sentence profile>,
  "activity_summary": <summary of engagement history>,
  "pipeline_status": <current pipeline status and value>,
  "estimated_value": <number or null>,
  "key_risks": [<list of 2-3 risks>],
  "recommended_next_step": <specific action>,
  "overall_assessment": <one sentence overall assessment>
}}
"""
        result = self._safe_call(prompt, fallback_result)
        result["lead_id"] = lead_data.get("id", "")
        result["provider"] = self.provider_name
        return result

    def generate_follow_up_email(
        self, lead_data: Dict[str, Any], email_type: str
    ) -> Dict[str, Any]:
        fallback_result = self._fallback.generate_follow_up_email(lead_data, email_type)
        if not self._model:
            return fallback_result

        email_type_descriptions = {
            "first_outreach": "First cold outreach email",
            "follow_up": "Second follow-up to a cold outreach",
            "proposal_follow_up": "Follow-up after sending a proposal",
            "re_engagement": "Re-engaging a stale/cold prospect",
        }

        prompt = f"""
Write a professional sales email for this lead.

Email Type: {email_type_descriptions.get(email_type, email_type)}
Lead Name: {lead_data.get('first_name')} {lead_data.get('last_name')}
Company: {lead_data.get('company')}
Job Title: {lead_data.get('job_title')}
Industry: {lead_data.get('industry')}
Lead Source: {lead_data.get('source')}

Write a concise, professional email. Do NOT use placeholder text like [Your Name] - keep the sender as the LeadForge AI sales team.

Return JSON:
{{
  "subject": <email subject line>,
  "body": <full email body with proper formatting, newlines as \\n>
}}
"""
        result = self._safe_call(prompt, fallback_result)
        result["email_type"] = email_type
        result["provider"] = self.provider_name
        return result

    def generate_sales_insights(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._fallback.generate_sales_insights(pipeline_data)
