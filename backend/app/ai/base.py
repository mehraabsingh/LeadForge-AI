"""
AI Service abstraction layer.
Supports: gemini, openai, fallback (no API key required)
Configure via AI_PROVIDER environment variable.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseAIService(ABC):
    """Abstract base for all AI providers."""

    @abstractmethod
    def score_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score a lead and return structured result."""
        pass

    @abstractmethod
    def summarize_lead(self, lead_data: Dict[str, Any], activities: list, notes: list) -> Dict[str, Any]:
        """Generate a summary for a lead."""
        pass

    @abstractmethod
    def generate_follow_up_email(
        self, lead_data: Dict[str, Any], email_type: str
    ) -> Dict[str, Any]:
        """Generate a follow-up email for a lead."""
        pass

    @abstractmethod
    def generate_sales_insights(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sales insights from pipeline data."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
