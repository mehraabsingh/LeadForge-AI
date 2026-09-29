"""
AI service factory. Returns the configured AI provider.
"""
import logging
from typing import Optional
from app.ai.base import BaseAIService
from app.ai.fallback import FallbackAIService
from app.core.config import settings

logger = logging.getLogger(__name__)

_ai_service: Optional[BaseAIService] = None


def get_ai_service() -> BaseAIService:
    """
    Factory function returning the configured AI service.
    Falls back gracefully if API key is missing or provider fails.
    """
    global _ai_service
    if _ai_service is not None:
        return _ai_service

    provider = settings.AI_PROVIDER.lower()
    logger.info(f"Initializing AI provider: {provider}")

    if provider == "gemini" and settings.GEMINI_API_KEY:
        try:
            from app.ai.gemini_service import GeminiAIService
            _ai_service = GeminiAIService(api_key=settings.GEMINI_API_KEY)
            logger.info("Using Gemini AI provider")
            return _ai_service
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini: {e}. Falling back to deterministic engine.")

    elif provider == "openai" and settings.OPENAI_API_KEY:
        try:
            from app.ai.openai_service import OpenAIService
            _ai_service = OpenAIService(api_key=settings.OPENAI_API_KEY)
            logger.info("Using OpenAI provider")
            return _ai_service
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI: {e}. Falling back to deterministic engine.")

    # Default: deterministic fallback
    logger.info("Using deterministic fallback AI engine (no API key required)")
    _ai_service = FallbackAIService()
    return _ai_service


def reset_ai_service():
    """Reset the service singleton (useful for testing)."""
    global _ai_service
    _ai_service = None
