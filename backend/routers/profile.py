from fastapi import APIRouter

from backend.schemas.profile import (
    ProfileAnalysisRequest,
    ProfileAnalysisResponse,
)

from backend.services.profile_service import (
    analyze_profile,
)


router = APIRouter(
    prefix="/api/profile",
    tags=["Skill Profile"],
)


@router.post(
    "/analyze",
    response_model=ProfileAnalysisResponse,
)
def profile_analysis(
    request: ProfileAnalysisRequest,
):
    return analyze_profile(
        district=request.district,
        skills=request.skills,
    )