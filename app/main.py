from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.core.config import CORS_ORIGINS, MEDIA_ROOT
from app.db.session import Base, engine
from app.services.blog_sync_service import ensure_blog_sync_schema, start_blog_sync_scheduler, stop_blog_sync_scheduler

from app.models import (  # noqa: F401
    blog,
    blog_sync,
    contact,
    page,
    project,
    site,
    user,
)

app = FastAPI(
    title="Modulux Homes API",
    description="Backend API for Modulux Homes CMS",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_blog_sync_schema()
    start_blog_sync_scheduler()


@app.on_event("shutdown")
def on_shutdown() -> None:
    stop_blog_sync_scheduler()


app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Modulux Homes API v2"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
