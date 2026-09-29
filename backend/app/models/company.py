import uuid
from sqlalchemy import Column, String, DateTime, Text, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True)
    size = Column(String(50), nullable=True)  # e.g., "1-10", "11-50", "51-200"
    location = Column(String(255), nullable=True)
    annual_revenue = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    contacts = relationship("Contact", back_populates="company")
    leads = relationship("Lead", back_populates="company_rel")
    activities = relationship("Activity", back_populates="company")
    notes = relationship("Note", back_populates="company")

    def __repr__(self) -> str:
        return f"<Company {self.name}>"
