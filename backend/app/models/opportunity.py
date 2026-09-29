import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Enum as SAEnum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class OpportunityStatus(str, enum.Enum):
    OPEN = "OPEN"
    WON = "WON"
    LOST = "LOST"


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    value = Column(Float, nullable=True, default=0.0)
    probability = Column(Float, nullable=True, default=50.0)  # 0-100
    status = Column(SAEnum(OpportunityStatus), nullable=False, default=OpportunityStatus.OPEN)
    expected_close_date = Column(Date, nullable=True)
    actual_close_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Foreign Keys
    lead_id = Column(String(36), ForeignKey("leads.id"), nullable=True, index=True)
    pipeline_id = Column(String(36), ForeignKey("pipelines.id"), nullable=False, index=True)
    stage_id = Column(String(36), ForeignKey("pipeline_stages.id"), nullable=False, index=True)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    lead = relationship("Lead", back_populates="opportunity")
    pipeline = relationship("Pipeline", back_populates="opportunities")
    stage = relationship("PipelineStage", back_populates="opportunities")
    owner = relationship("User", back_populates="opportunities", foreign_keys=[owner_id])
    company = relationship("Company")
    activities = relationship("Activity", back_populates="opportunity")
    tasks = relationship("Task", back_populates="opportunity")

    @property
    def weighted_value(self) -> float:
        if self.value and self.probability:
            return self.value * (self.probability / 100)
        return 0.0

    def __repr__(self) -> str:
        return f"<Opportunity {self.title} ({self.status})>"
