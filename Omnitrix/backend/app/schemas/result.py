from datetime import datetime
from app.database.enums import AssessmentSection
from pydantic import BaseModel


class SectionResultResponse(BaseModel):
    section: str
    score: float
    maximum_score: float
    percentage: float
    correct_count: int
    wrong_count: int
    skipped_count: int
    attempted_count: int
    accuracy: float
    time_efficiency: float
    difficulty_score: float


class EvaluateSectionResponse(SectionResultResponse):
    next_section: AssessmentSection | None = None
    next_deadline: datetime | None = None


class AssessmentResultResponse(BaseModel):
    assessment_id: int
    total_score: float
    maximum_score: float
    percentage: float
    sections: list[SectionResultResponse]