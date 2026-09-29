import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_type = Column(String(50), nullable=False)  # score, summary, email, insights
    provider = Column(String(50), nullable=True)  # gemini, openai, fallback
    score = Column(Integer, nullable=True)
    score_label = Column(String(20), nullable=True)
    result_data = Column(JSON, nullable=True)  # Full structured result
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)

    lead_id = Column(String(36), ForeignKey("leads.id"), nullable=True, index=True)
    created_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lead = relationship("Lead", back_populates="ai_analyses")
    created_by = relationship("User")

    def __repr__(self) -> str:
        return f"<AIAnalysis {self.analysis_type} lead={self.lead_id}>"
