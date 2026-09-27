import asyncio
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.assessment import router as assessment_router
from app.api.auth import router as auth_router
from app.api.badges import router as badges_router
from app.api.career import router as career_router
from app.api.certificates import router as certificates_router
from app.api.companies import router as companies_router
from app.api.dashboard import router as dashboard_router
from app.api.interviews import router as interviews_router
from app.api.jobs import router as jobs_router
from app.api.onboarding import router as onboarding_router
from app.api.progress import router as progress_router
from app.api.recommendations import router as recommendations_router
from app.api.resume import router as resume_router
import app.models  # noqa: F401
from app.database.database import Base, engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield




app = FastAPI(
    title="AI Interviewer API",
    description="Full-stack AI Mock Interview, Assessment, and Career Guidance Engine",
    version="2.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Include all module routers
app.include_router(auth_router)
app.include_router(onboarding_router)
app.include_router(resume_router)
app.include_router(interviews_router)
app.include_router(assessment_router)
app.include_router(jobs_router)
app.include_router(companies_router)
app.include_router(career_router)
app.include_router(progress_router)
app.include_router(recommendations_router)
app.include_router(badges_router)
app.include_router(certificates_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {
        "message": "AI Interviewer API is running",
        "version": "2.0.0",
        "modules": [
            "auth",
            "resume",
            "interviews",
            "assessment",
            "jobs",
            "companies",
            "career",
            "progress",
            "recommendations",
            "badges",
            "certificates",
            "dashboard",
        ],
    }