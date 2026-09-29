from fastapi import APIRouter
from app.api.v1.endpoints import auth, leads, companies, contacts, opportunities, tasks, pipelines, dashboard, ai, users

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(leads.router)
api_router.include_router(companies.router)
api_router.include_router(contacts.router)
api_router.include_router(opportunities.router)
api_router.include_router(tasks.router)
api_router.include_router(pipelines.router)
api_router.include_router(dashboard.router)
api_router.include_router(ai.router)
api_router.include_router(users.router)
