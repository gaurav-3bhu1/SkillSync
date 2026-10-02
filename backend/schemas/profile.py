from pydantic import BaseModel


class ProfileAnalysisRequest(BaseModel):
    district: str
    skills: list[str]


class SkillGap(BaseModel):
    skill: str
    skill_id: str | None = None
    demand_job_count: int
    demand_percentage: float
    priority: str
    reason: str


class CourseRecommendation(BaseModel):
    course_name: str
    iti_name: str
    district: str
    placement_rate_pct: float
    matched_skills: list[str]


class ProfileAnalysisResponse(BaseModel):
    district: str
    current_skills: list[str]
    normalized_skills: list[str]
    inferred_sector: str | None = None
    skill_gaps: list[SkillGap]
    recommended_courses: list[CourseRecommendation]