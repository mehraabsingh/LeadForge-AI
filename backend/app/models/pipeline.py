import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Float, Enum as SAEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    stages = relationship("PipelineStage", back_populates="pipeline", order_by="PipelineStage.order")
    opportunities = relationship("Opportunity", back_populates="pipeline")

    def __repr__(self) -> str:
        return f"<Pipeline {self.name}>"


class PipelineStage(Base):
    __tablename__ = "pipeline_stages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    order = Column(Integer, nullable=False, default=0)
    color = Column(String(7), nullable=True, default="#6366f1")  # hex color
    probability = Column(Float, nullable=True, default=50.0)  # default win probability %
    pipeline_id = Column(String(36), ForeignKey("pipelines.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    pipeline = relationship("Pipeline", back_populates="stages")
    opportunities = relationship("Opportunity", back_populates="stage")

    def __repr__(self) -> str:
        return f"<PipelineStage {self.name} (order={self.order})>"
