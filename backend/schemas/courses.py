from pydantic import BaseModel


class CourseAlignment(BaseModel):
    course_name: str
    iti_count: int
    skill_count: int
    demand_score: float
    average_placement_rate_pct: float | None
    allocated_skill_seats: float
    high_demand_skills: list[str]
    skill_gaps: list[str]


class CourseAlignmentResponse(BaseModel):
    total_courses: int
    courses: list[CourseAlignment]