"""
Database seed script.
Creates realistic demo data for LeadForge AI.

Demo credentials:
  Admin:    admin@leadforge.ai / Admin@123456
  Manager:  manager@leadforge.ai / Manager@123456
  Sales:    sarah.chen@leadforge.ai / Sales@123456
  Sales:    marcus.johnson@leadforge.ai / Sales@123456
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, date
import random
import uuid

# Set up environment
os.environ.setdefault("DATABASE_URL", "sqlite:///./leadforge.db")

from app.db.database import SessionLocal, engine, Base
import app.models  # noqa - register all models
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.contact import Contact
from app.models.lead import Lead, LeadStatus, LeadPriority, LeadSource
from app.models.pipeline import Pipeline, PipelineStage
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.activity import Activity, ActivityType
from app.models.note import Note
from app.models.notification import Notification


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).count() > 0:
            print("✓ Database already seeded. Skipping.")
            return

        print("🌱 Seeding LeadForge AI database...")

        # ── USERS ──────────────────────────────────────────────────────────────
        admin = User(
            id=str(uuid.uuid4()),
            email="admin@leadforge.ai",
            hashed_password=hash_password("Admin@123456"),
            first_name="Alex",
            last_name="Rivera",
            role=UserRole.ADMIN,
            is_active=True,
        )
        manager = User(
            id=str(uuid.uuid4()),
            email="manager@leadforge.ai",
            hashed_password=hash_password("Manager@123456"),
            first_name="Jordan",
            last_name="Kim",
            role=UserRole.MANAGER,
            is_active=True,
        )
        sarah = User(
            id=str(uuid.uuid4()),
            email="sarah.chen@leadforge.ai",
            hashed_password=hash_password("Sales@123456"),
            first_name="Sarah",
            last_name="Chen",
            role=UserRole.SALES_REP,
            is_active=True,
        )
        marcus = User(
            id=str(uuid.uuid4()),
            email="marcus.johnson@leadforge.ai",
            hashed_password=hash_password("Sales@123456"),
            first_name="Marcus",
            last_name="Johnson",
            role=UserRole.SALES_REP,
            is_active=True,
        )
        db.add_all([admin, manager, sarah, marcus])
        db.flush()
        print("  ✓ Users created")

        # ── PIPELINE ───────────────────────────────────────────────────────────
        pipeline = Pipeline(
            id=str(uuid.uuid4()),
            name="Sales Pipeline",
            description="Main sales pipeline for all opportunities",
            is_default=True,
        )
        db.add(pipeline)
        db.flush()

        stage_data = [
            ("New Lead", 0, "#6366f1", 10),
            ("Contacted", 1, "#8b5cf6", 20),
            ("Discovery", 2, "#3b82f6", 40),
            ("Proposal", 3, "#f59e0b", 60),
            ("Negotiation", 4, "#f97316", 80),
            ("Won", 5, "#10b981", 100),
            ("Lost", 6, "#ef4444", 0),
        ]
        stages = {}
        for name, order, color, prob in stage_data:
            stage = PipelineStage(
                id=str(uuid.uuid4()),
                name=name,
                order=order,
                color=color,
                probability=prob,
                pipeline_id=pipeline.id,
            )
            db.add(stage)
            stages[name] = stage
        db.flush()
        print("  ✓ Pipeline and stages created")

        # ── COMPANIES ──────────────────────────────────────────────────────────
        companies_data = [
            {
                "name": "Acme Technologies",
                "industry": "Technology",
                "website": "https://acme.tech",
                "size": "201-500",
                "location": "San Francisco, CA",
                "annual_revenue": 45000000,
                "description": "Enterprise software solutions provider specializing in cloud infrastructure.",
            },
            {
                "name": "GlobalHealth Systems",
                "industry": "Healthcare",
                "website": "https://globalhealth.com",
                "size": "500+",
                "location": "Boston, MA",
                "annual_revenue": 120000000,
                "description": "Leading healthcare technology company providing EHR and practice management solutions.",
            },
            {
                "name": "FinEdge Capital",
                "industry": "Financial Services",
                "website": "https://finedge.com",
                "size": "51-200",
                "location": "New York, NY",
                "annual_revenue": 28000000,
                "description": "Boutique investment firm focused on growth-stage technology companies.",
            },
            {
                "name": "RetailMax",
                "industry": "Retail",
                "website": "https://retailmax.co",
                "size": "201-500",
                "location": "Chicago, IL",
                "annual_revenue": 67000000,
                "description": "Omnichannel retail platform serving mid-market retailers.",
            },
            {
                "name": "BuildRight Construction",
                "industry": "Construction",
                "website": "https://buildright.com",
                "size": "51-200",
                "location": "Austin, TX",
                "annual_revenue": 35000000,
                "description": "Commercial and residential construction company with a focus on sustainable building.",
            },
            {
                "name": "Nexus Logistics",
                "industry": "Logistics",
                "website": "https://nexuslogistics.com",
                "size": "500+",
                "location": "Dallas, TX",
                "annual_revenue": 89000000,
                "description": "Third-party logistics provider specializing in last-mile delivery.",
            },
            {
                "name": "EduSpark Learning",
                "industry": "Education Technology",
                "website": "https://eduspark.io",
                "size": "11-50",
                "location": "Seattle, WA",
                "annual_revenue": 8500000,
                "description": "Online learning platform for corporate training and upskilling.",
            },
        ]
        companies = []
        for cd in companies_data:
            c = Company(id=str(uuid.uuid4()), **cd)
            db.add(c)
            companies.append(c)
        db.flush()
        print("  ✓ Companies created")

        # ── CONTACTS ───────────────────────────────────────────────────────────
        contacts_data = [
            {"first_name": "Michael", "last_name": "Torres", "email": "m.torres@acme.tech", "job_title": "CTO", "phone": "+1-415-555-0101", "company_idx": 0},
            {"first_name": "Jennifer", "last_name": "Walsh", "email": "j.walsh@acme.tech", "job_title": "VP Engineering", "phone": "+1-415-555-0102", "company_idx": 0},
            {"first_name": "Robert", "last_name": "Chen", "email": "r.chen@globalhealth.com", "job_title": "CEO", "phone": "+1-617-555-0201", "company_idx": 1},
            {"first_name": "Amanda", "last_name": "Foster", "email": "a.foster@globalhealth.com", "job_title": "CISO", "phone": "+1-617-555-0202", "company_idx": 1},
            {"first_name": "David", "last_name": "Park", "email": "d.park@finedge.com", "job_title": "Managing Director", "phone": "+1-212-555-0301", "company_idx": 2},
            {"first_name": "Rachel", "last_name": "Thompson", "email": "r.thompson@retailmax.co", "job_title": "Head of Digital", "phone": "+1-312-555-0401", "company_idx": 3},
            {"first_name": "James", "last_name": "Williams", "email": "j.williams@buildright.com", "job_title": "CEO", "phone": "+1-512-555-0501", "company_idx": 4},
            {"first_name": "Lisa", "last_name": "Martinez", "email": "l.martinez@nexuslogistics.com", "job_title": "VP Operations", "phone": "+1-214-555-0601", "company_idx": 5},
            {"first_name": "Kevin", "last_name": "Zhang", "email": "k.zhang@eduspark.io", "job_title": "Founder & CEO", "phone": "+1-206-555-0701", "company_idx": 6},
        ]
        for cd in contacts_data:
            c = Contact(
                id=str(uuid.uuid4()),
                first_name=cd["first_name"],
                last_name=cd["last_name"],
                email=cd["email"],
                job_title=cd["job_title"],
                phone=cd["phone"],
                company_id=companies[cd["company_idx"]].id,
            )
            db.add(c)
        db.flush()
        print("  ✓ Contacts created")

        # ── LEADS ──────────────────────────────────────────────────────────────
        leads_raw = [
            {
                "first_name": "Michael", "last_name": "Torres",
                "email": "m.torres@acme.tech", "phone": "+1-415-555-0101",
                "company": "Acme Technologies", "job_title": "CTO",
                "source": LeadSource.LINKEDIN, "industry": "Technology",
                "company_size": "201-500", "location": "San Francisco, CA",
                "estimated_value": 85000, "status": LeadStatus.QUALIFIED,
                "priority": LeadPriority.HIGH, "score": 82, "score_label": "HOT",
                "owner": sarah, "company_obj": companies[0],
                "description": "Interested in full CRM migration. Has budget approved.",
            },
            {
                "first_name": "Robert", "last_name": "Chen",
                "email": "r.chen@globalhealth.com", "phone": "+1-617-555-0201",
                "company": "GlobalHealth Systems", "job_title": "CEO",
                "source": LeadSource.REFERRAL, "industry": "Healthcare",
                "company_size": "500+", "location": "Boston, MA",
                "estimated_value": 250000, "status": LeadStatus.CONTACTED,
                "priority": LeadPriority.URGENT, "score": 91, "score_label": "HOT",
                "owner": marcus, "company_obj": companies[1],
                "description": "Referred by existing customer. Looking for enterprise CRM solution.",
            },
            {
                "first_name": "David", "last_name": "Park",
                "email": "d.park@finedge.com", "phone": "+1-212-555-0301",
                "company": "FinEdge Capital", "job_title": "Managing Director",
                "source": LeadSource.CONFERENCE, "industry": "Financial Services",
                "company_size": "51-200", "location": "New York, NY",
                "estimated_value": 120000, "status": LeadStatus.QUALIFIED,
                "priority": LeadPriority.HIGH, "score": 78, "score_label": "HOT",
                "owner": sarah, "company_obj": companies[2],
                "description": "Met at SaaStr conference. Very interested in AI lead scoring.",
            },
            {
                "first_name": "Rachel", "last_name": "Thompson",
                "email": "r.thompson@retailmax.co", "phone": "+1-312-555-0401",
                "company": "RetailMax", "job_title": "Head of Digital",
                "source": LeadSource.WEBSITE, "industry": "Retail",
                "company_size": "201-500", "location": "Chicago, IL",
                "estimated_value": 65000, "status": LeadStatus.NEW,
                "priority": LeadPriority.MEDIUM, "score": 55, "score_label": "WARM",
                "owner": marcus, "company_obj": companies[3],
                "description": "Downloaded whitepaper from website. Needs follow-up.",
            },
            {
                "first_name": "Jennifer", "last_name": "Walsh",
                "email": "j.walsh@acme.tech", "phone": "+1-415-555-0102",
                "company": "Acme Technologies", "job_title": "VP Engineering",
                "source": LeadSource.LINKEDIN, "industry": "Technology",
                "company_size": "201-500", "location": "San Francisco, CA",
                "estimated_value": 45000, "status": LeadStatus.CONTACTED,
                "priority": LeadPriority.MEDIUM, "score": 62, "score_label": "WARM",
                "owner": sarah, "company_obj": companies[0],
                "description": "Secondary contact at Acme. Involved in tech evaluation.",
            },
            {
                "first_name": "James", "last_name": "Williams",
                "email": "j.williams@buildright.com", "phone": "+1-512-555-0501",
                "company": "BuildRight Construction", "job_title": "CEO",
                "source": LeadSource.COLD_OUTREACH, "industry": "Construction",
                "company_size": "51-200", "location": "Austin, TX",
                "estimated_value": 35000, "status": LeadStatus.NEW,
                "priority": LeadPriority.LOW, "score": 38, "score_label": "COLD",
                "owner": marcus, "company_obj": companies[4],
                "description": "Cold outreach. Hasn't responded yet.",
            },
            {
                "first_name": "Lisa", "last_name": "Martinez",
                "email": "l.martinez@nexuslogistics.com", "phone": "+1-214-555-0601",
                "company": "Nexus Logistics", "job_title": "VP Operations",
                "source": LeadSource.PARTNER, "industry": "Logistics",
                "company_size": "500+", "location": "Dallas, TX",
                "estimated_value": 180000, "status": LeadStatus.QUALIFIED,
                "priority": LeadPriority.HIGH, "score": 85, "score_label": "HOT",
                "owner": sarah, "company_obj": companies[5],
                "description": "Partner referral. VP of Ops looking for CRM + analytics solution.",
            },
            {
                "first_name": "Kevin", "last_name": "Zhang",
                "email": "k.zhang@eduspark.io", "phone": "+1-206-555-0701",
                "company": "EduSpark Learning", "job_title": "Founder & CEO",
                "source": LeadSource.WEBSITE, "industry": "Education Technology",
                "company_size": "11-50", "location": "Seattle, WA",
                "estimated_value": 18000, "status": LeadStatus.CONTACTED,
                "priority": LeadPriority.MEDIUM, "score": 45, "score_label": "WARM",
                "owner": marcus, "company_obj": companies[6],
                "description": "Early stage startup. Interested but budget is limited.",
            },
            {
                "first_name": "Amanda", "last_name": "Foster",
                "email": "a.foster@globalhealth.com", "phone": "+1-617-555-0202",
                "company": "GlobalHealth Systems", "job_title": "CISO",
                "source": LeadSource.REFERRAL, "industry": "Healthcare",
                "company_size": "500+", "location": "Boston, MA",
                "estimated_value": 95000, "status": LeadStatus.CONVERTED,
                "priority": LeadPriority.HIGH, "score": 88, "score_label": "HOT",
                "owner": marcus, "company_obj": companies[1],
                "description": "Security-focused lead who has been converted to an opportunity.",
            },
            {
                "first_name": "Carlos", "last_name": "Mendez",
                "email": "carlos.m@techstartup.io", "phone": "+1-408-555-0890",
                "company": "TechStartup Inc", "job_title": "Head of Product",
                "source": LeadSource.LINKEDIN, "industry": "Technology",
                "company_size": "11-50", "location": "Palo Alto, CA",
                "estimated_value": 28000, "status": LeadStatus.UNQUALIFIED,
                "priority": LeadPriority.LOW, "score": 30, "score_label": "COLD",
                "owner": sarah, "company_obj": None,
                "description": "Not a good fit - too small and no budget this quarter.",
            },
        ]

        leads = []
        now = datetime.utcnow()
        for i, ld in enumerate(leads_raw):
            created_at = now - timedelta(days=random.randint(5, 60))
            lead = Lead(
                id=str(uuid.uuid4()),
                first_name=ld["first_name"],
                last_name=ld["last_name"],
                email=ld["email"],
                phone=ld["phone"],
                company=ld["company"],
                job_title=ld["job_title"],
                source=ld["source"],
                industry=ld["industry"],
                company_size=ld["company_size"],
                location=ld["location"],
                estimated_value=ld["estimated_value"],
                status=ld["status"],
                priority=ld["priority"],
                score=ld.get("score"),
                score_label=ld.get("score_label"),
                description=ld["description"],
                owner_id=ld["owner"].id,
                company_id=ld["company_obj"].id if ld["company_obj"] else None,
            )
            db.add(lead)
            leads.append(lead)
        db.flush()
        print("  ✓ Leads created")

        # ── OPPORTUNITIES ──────────────────────────────────────────────────────
        opps_data = [
            {
                "title": "Acme Technologies - CRM Migration",
                "description": "Full CRM platform migration including custom integrations",
                "value": 85000, "probability": 70,
                "status": OpportunityStatus.OPEN,
                "expected_close_date": date.today() + timedelta(days=30),
                "lead": leads[0], "stage": stages["Proposal"],
                "owner": sarah, "company": companies[0],
            },
            {
                "title": "GlobalHealth Systems - Enterprise License",
                "description": "Enterprise CRM license for 500+ users with advanced AI features",
                "value": 250000, "probability": 60,
                "status": OpportunityStatus.OPEN,
                "expected_close_date": date.today() + timedelta(days=45),
                "lead": leads[1], "stage": stages["Discovery"],
                "owner": marcus, "company": companies[1],
            },
            {
                "title": "FinEdge Capital - AI Lead Scoring Module",
                "description": "AI-powered lead scoring and sales insights for investment team",
                "value": 120000, "probability": 55,
                "status": OpportunityStatus.OPEN,
                "expected_close_date": date.today() + timedelta(days=21),
                "lead": leads[2], "stage": stages["Negotiation"],
                "owner": sarah, "company": companies[2],
            },
            {
                "title": "Nexus Logistics - Analytics Platform",
                "description": "Sales analytics and pipeline management solution",
                "value": 180000, "probability": 45,
                "status": OpportunityStatus.OPEN,
                "expected_close_date": date.today() + timedelta(days=60),
                "lead": leads[6], "stage": stages["Proposal"],
                "owner": sarah, "company": companies[5],
            },
            {
                "title": "GlobalHealth - Security Compliance Module",
                "description": "HIPAA-compliant CRM with security audit trails",
                "value": 95000, "probability": 100,
                "status": OpportunityStatus.WON,
                "expected_close_date": date.today() - timedelta(days=10),
                "actual_close_date": date.today() - timedelta(days=10),
                "lead": leads[8], "stage": stages["Won"],
                "owner": marcus, "company": companies[1],
            },
            {
                "title": "RetailMax - Starter Package",
                "description": "Entry-level CRM for retail operations team",
                "value": 32000, "probability": 100,
                "status": OpportunityStatus.WON,
                "expected_close_date": date.today() - timedelta(days=25),
                "actual_close_date": date.today() - timedelta(days=25),
                "lead": leads[3], "stage": stages["Won"],
                "owner": marcus, "company": companies[3],
            },
            {
                "title": "BuildRight Construction - CRM Setup",
                "description": "Basic CRM setup for construction project management",
                "value": 35000, "probability": 0,
                "status": OpportunityStatus.LOST,
                "expected_close_date": date.today() - timedelta(days=15),
                "lead": leads[5], "stage": stages["Lost"],
                "owner": marcus, "company": companies[4],
                "notes": "Lost to competitor. Price was too high for their budget.",
            },
        ]

        opps = []
        for od in opps_data:
            opp_kwargs = {
                "id": str(uuid.uuid4()),
                "title": od["title"],
                "description": od["description"],
                "value": od["value"],
                "probability": od["probability"],
                "status": od["status"],
                "expected_close_date": od["expected_close_date"],
                "lead_id": od["lead"].id,
                "pipeline_id": pipeline.id,
                "stage_id": od["stage"].id,
                "owner_id": od["owner"].id,
                "company_id": od["company"].id,
                "notes": od.get("notes"),
            }
            if od.get("actual_close_date"):
                opp_kwargs["actual_close_date"] = od["actual_close_date"]
            opp = Opportunity(**opp_kwargs)
            db.add(opp)
            opps.append(opp)
        db.flush()
        print("  ✓ Opportunities created")

        # ── ACTIVITIES ─────────────────────────────────────────────────────────
        activities_raw = [
            (leads[0], sarah, ActivityType.CALL, "Initial Discovery Call", "Discussed pain points with current CRM. Very interested in AI features.", "Lead is highly engaged. Wants to see proposal ASAP."),
            (leads[0], sarah, ActivityType.EMAIL, "Proposal Email Sent", "Sent detailed proposal covering CRM migration plan.", "Waiting for feedback from their procurement team."),
            (leads[1], marcus, ActivityType.MEETING, "Executive Intro Meeting", "30-min intro with CEO Robert Chen and 3 stakeholders.", "Very positive. CEO wants to move fast. Decision by Q4."),
            (leads[1], marcus, ActivityType.CALL, "Technical Requirements Call", "Discussed HIPAA compliance requirements and data migration.", "Security is a major concern. Need to involve their CISO."),
            (leads[2], sarah, ActivityType.MEETING, "SaaStr Conference Meeting", "Met at booth, discussed AI lead scoring use case for their investment team.", "Great fit. Requested a demo ASAP."),
            (leads[2], sarah, ActivityType.DEMO, "Product Demo", "Gave full product walkthrough focusing on AI features.", "Loved the scoring algorithm. Now in negotiation."),
            (leads[6], sarah, ActivityType.EMAIL, "Partner Referral Follow-up", "Sent welcome email referencing partner introduction.", "Opened email, clicked pricing link."),
            (leads[6], sarah, ActivityType.CALL, "Qualification Call", "Discussed current logistics CRM challenges.", "Using spreadsheets. Huge opportunity for us."),
            (leads[3], marcus, ActivityType.EMAIL, "Website Lead Follow-up", "Reached out after whitepaper download.", "Opened but no reply yet."),
            (leads[7], marcus, ActivityType.CALL, "Initial Outreach Call", "Brief intro call with Kevin Zhang.", "Small budget but growing fast. Worth nurturing."),
        ]

        for lead, user, atype, title, desc, outcome in activities_raw:
            a = Activity(
                id=str(uuid.uuid4()),
                type=atype,
                title=title,
                description=desc,
                outcome=outcome,
                user_id=user.id,
                lead_id=lead.id,
                company_id=lead.company_id,
            )
            db.add(a)
        db.flush()
        print("  ✓ Activities created")

        # ── NOTES ──────────────────────────────────────────────────────────────
        notes_raw = [
            (leads[0], sarah, "Decision maker confirmed: Michael Torres has sign-off authority up to $100K. No procurement involvement needed."),
            (leads[0], sarah, "Competitor analysis: They're currently evaluating Salesforce vs. us. Our AI features and pricing are differentiated."),
            (leads[1], marcus, "HIPAA compliance is non-negotiable. Involve security team in next call. They will also require a BAA."),
            (leads[2], sarah, "FinEdge is looking to close before end of fiscal year (Dec 31). Budget is approved and allocated."),
            (leads[6], sarah, "Nexus runs 3 separate systems for their operations. Consolidation is the main value prop. IT team will need to be involved."),
        ]

        for lead, user, content in notes_raw:
            note = Note(
                id=str(uuid.uuid4()),
                content=content,
                author_id=user.id,
                lead_id=lead.id,
                company_id=lead.company_id,
            )
            db.add(note)
        db.flush()
        print("  ✓ Notes created")

        # ── TASKS ──────────────────────────────────────────────────────────────
        tasks_raw = [
            {
                "title": "Send contract to Acme Technologies",
                "description": "Prepare and send MSA + SOW based on agreed terms",
                "due_date": datetime.utcnow() + timedelta(days=3),
                "priority": TaskPriority.URGENT,
                "status": TaskStatus.TODO,
                "assigned_to": sarah,
                "lead": leads[0],
            },
            {
                "title": "Follow up with GlobalHealth CEO",
                "description": "Check status of internal review and timeline",
                "due_date": datetime.utcnow() + timedelta(days=2),
                "priority": TaskPriority.HIGH,
                "status": TaskStatus.IN_PROGRESS,
                "assigned_to": marcus,
                "lead": leads[1],
            },
            {
                "title": "Prepare FinEdge negotiation strategy",
                "description": "Review pricing flexibility and package options",
                "due_date": datetime.utcnow() + timedelta(days=1),
                "priority": TaskPriority.HIGH,
                "status": TaskStatus.TODO,
                "assigned_to": sarah,
                "lead": leads[2],
            },
            {
                "title": "Send whitepaper to RetailMax lead",
                "description": "Follow up on website form submission with relevant content",
                "due_date": datetime.utcnow() - timedelta(days=1),  # Overdue!
                "priority": TaskPriority.MEDIUM,
                "status": TaskStatus.TODO,
                "assigned_to": marcus,
                "lead": leads[3],
            },
            {
                "title": "Schedule Nexus Logistics technical call",
                "description": "Set up call with their IT team to discuss integration requirements",
                "due_date": datetime.utcnow() + timedelta(days=5),
                "priority": TaskPriority.HIGH,
                "status": TaskStatus.TODO,
                "assigned_to": sarah,
                "lead": leads[6],
            },
            {
                "title": "Quarterly pipeline review",
                "description": "Review all open opportunities and update probability scores",
                "due_date": datetime.utcnow() + timedelta(days=7),
                "priority": TaskPriority.MEDIUM,
                "status": TaskStatus.TODO,
                "assigned_to": manager,
                "lead": None,
            },
            {
                "title": "Update CRM demo script",
                "description": "Refresh demo with latest AI scoring features for upcoming demos",
                "due_date": datetime.utcnow() + timedelta(days=4),
                "priority": TaskPriority.LOW,
                "status": TaskStatus.COMPLETED,
                "assigned_to": sarah,
                "lead": None,
            },
        ]

        for td in tasks_raw:
            task = Task(
                id=str(uuid.uuid4()),
                title=td["title"],
                description=td["description"],
                due_date=td["due_date"],
                priority=td["priority"],
                status=td["status"],
                assigned_to_id=td["assigned_to"].id,
                created_by_id=manager.id,
                lead_id=td["lead"].id if td["lead"] else None,
            )
            db.add(task)
        db.flush()
        print("  ✓ Tasks created")

        # ── NOTIFICATIONS ──────────────────────────────────────────────────────
        notifications = [
            Notification(
                id=str(uuid.uuid4()),
                title="New Hot Lead Assigned",
                message="You've been assigned a HOT lead: Robert Chen from GlobalHealth Systems ($250K potential)",
                type="success",
                user_id=marcus.id,
                link="/leads",
            ),
            Notification(
                id=str(uuid.uuid4()),
                title="Overdue Task",
                message="Task 'Send whitepaper to RetailMax lead' is overdue",
                type="warning",
                user_id=marcus.id,
                link="/tasks",
            ),
            Notification(
                id=str(uuid.uuid4()),
                title="Deal Won! 🎉",
                message="GlobalHealth Systems - Security Compliance Module ($95,000) has been marked as WON",
                type="success",
                user_id=admin.id,
                link="/opportunities",
            ),
        ]
        for n in notifications:
            db.add(n)

        db.commit()
        print("  ✓ Notifications created")
        print("\n✅ Seed complete! Demo credentials:")
        print("   Admin:   admin@leadforge.ai / Admin@123456")
        print("   Manager: manager@leadforge.ai / Manager@123456")
        print("   Sales:   sarah.chen@leadforge.ai / Sales@123456")
        print("   Sales:   marcus.johnson@leadforge.ai / Sales@123456")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
