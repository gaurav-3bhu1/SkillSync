from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.market import router as market_router
from backend.services.data_service import (
    get_districts,
    get_sectors,
)
from backend.routers.skills import router as skills_router
from backend.routers.courses import router as courses_router
from backend.routers.districts import router as districts_router
from backend.routers.profile import router as profile_router

app = FastAPI(
    title="SkillSync API",
    description=(
        "Labour-market intelligence and "
        "skill-development alignment API"
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(market_router)
app.include_router(skills_router)
app.include_router(courses_router)
app.include_router(districts_router)
app.include_router(profile_router)


@app.get("/")
def root():
    return {
        "name": "SkillSync API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/api/metadata")
def metadata():
    return {
        "districts": get_districts(),
        "sectors": get_sectors(),
    }