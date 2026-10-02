from pydantic import BaseModel


class SkillDemand(BaseModel):
    skill: str
    job_count: int
    demand_percentage: float


class MarketSummary(BaseModel):
    job_count: int
    skill_count: int
    top_skills: list[SkillDemand]