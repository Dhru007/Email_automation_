from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine, SessionLocal
from app.config import settings
from app import models
from app.core.security import hash_password
from app.scheduler import start_scheduler

from app.routers import auth, gmail, emails, knowledge_base, settings_router, analytics, pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _seed_admin()
    start_scheduler()
    yield


def _seed_admin():
    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.email == settings.admin_email).first()
        if not existing:
            admin = models.User(
                email=settings.admin_email,
                hashed_password=hash_password(settings.admin_password),
                name="Admin",
                role=models.UserRole.admin,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


app = FastAPI(title="AI Email Automation API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(gmail.router)
app.include_router(emails.router)
app.include_router(knowledge_base.router)
app.include_router(settings_router.router)
app.include_router(analytics.router)
app.include_router(pipeline.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
