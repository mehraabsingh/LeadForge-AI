import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Float, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class LeadStatus(str, enum.Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    UNQUALIFIED = "UNQUALIFIED"
    CONVERTED = "CONVERTED"
    LOST = "LOST"


class LeadPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class LeadSource(str, enum.Enum):
    WEBSITE = "WEBSITE"
    REFERRAL = "REFERRAL"
    LINKEDIN = "LINKEDIN"
    COLD_OUTREACH = "COLD_OUTREACH"
    CONFERENCE = "CONFERENCE"
    ADVERTISEMENT = "ADVERTISEMENT"
    PARTNER = "PARTNER"
    OTHER = "OTHER"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=True, index=True)
    job_title = Column(String(150), nullable=True)
    source = Column(SAEnum(LeadSource), nullable=True, default=LeadSource.OTHER)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    estimated_value = Column(Float, nullable=True)
    status = Column(SAEnum(LeadStatus), nullable=False, default=LeadStatus.NEW, index=True)
    priority = Column(SAEnum(LeadPriority), nullable=False, default=LeadPriority.MEDIUM)
    score = Column(Integer, nullable=True)  # 0-100 AI-generated
    score_label = Column(String(20), nullable=True)  # HOT, WARM, COLD
    description = Column(Text, nullable=True)

    # Relationships
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner = relationship("User", back_populates="leads", foreign_keys=[owner_id])
    company_rel = relationship("Company", back_populates="leads")
    opportunity = relationship("Opportunity", back_populates="lead", uselist=False)
    tasks = relationship("Task", back_populates="lead")
    activities = relationship("Activity", back_populates="lead", order_by="Activity.created_at.desc()")
    notes = relationship("Note", back_populates="lead", order_by="Note.created_at.desc()")
    ai_analyses = relationship("AIAnalysis", back_populates="lead")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Lead {self.full_name} ({self.status})>"
