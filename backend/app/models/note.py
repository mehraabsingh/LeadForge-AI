import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)

    # Foreign Keys
    author_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    lead_id = Column(String(36), ForeignKey("leads.id"), nullable=True, index=True)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True, index=True)
    opportunity_id = Column(String(36), ForeignKey("opportunities.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    author = relationship("User")
    lead = relationship("Lead", back_populates="notes")
    company = relationship("Company", back_populates="notes")

    def __repr__(self) -> str:
        return f"<Note by {self.author_id}>"
