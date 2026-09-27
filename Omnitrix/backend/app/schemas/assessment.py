from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.question import QuestionCandidateView


class AssessmentInstruction(BaseModel):
    section: str
    duration_minutes: int
    number_of_questions: int
    positive_mark: float
    negative_mark: float
    skipped_mark: float

    model_config = ConfigDict(from_attributes=True)


class AssessmentInstructionsResponse(BaseModel):
    total_duration_minutes: int
    sections: List[AssessmentInstruction]

    model_config = ConfigDict(from_attributes=True)


class StartAssessmentResponse(BaseModel):
    assessment_id: int
    status: Optional[str] = None
    started_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AssessmentStartRequest(BaseModel):
    mode: Optional[str] = "standard"  # standard, adaptive


class AssessmentQuestionItem(BaseModel):
    id: int
    section: Optional[str] = None
    question_text: str
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    difficulty: Optional[str] = None
    expected_time_seconds: Optional[int] = 60

    model_config = ConfigDict(from_attributes=True)


class AssessmentStartResponse(BaseModel):
    assessment_id: int
    status: str
    assessment_mode: str
    started_at: datetime
    questions: List[AssessmentQuestionItem]

    model_config = ConfigDict(from_attributes=True)


class AssessmentAnswerSubmitRequest(BaseModel):
    question_id: int
    selected_option: str  # A, B, C, D
    time_spent_seconds: Optional[int] = 0


class AssessmentSectionSubmitRequest(BaseModel):
    section: str
    answers: List[AssessmentAnswerSubmitRequest]


class AssessmentSectionResultResponse(BaseModel):
    section: str
    score: float
    maximum_score: float
    percentage: float
    correct_count: int
    wrong_count: int
    skipped_count: int
    accuracy: float
    time_efficiency: float

    model_config = ConfigDict(from_attributes=True)


class AssessmentCompleteResponse(BaseModel):
    assessment_id: int
    status: str
    total_score: float
    maximum_score: float
    percentage: float
    completed_at: datetime
    sections: List[AssessmentSectionResultResponse]

    model_config = ConfigDict(from_attributes=True)
