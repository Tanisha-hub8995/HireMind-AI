from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.question import QuestionCandidateView


class InterviewStartRequest(BaseModel):
    role: Optional[str] = "Software Engineer"
    job_id: Optional[int] = None
    interview_type: Optional[str] = "TECHNICAL"  # TECHNICAL, HR, BEHAVIORAL, SYSTEM_DESIGN
    difficulty: Optional[str] = "EASY"  # Starts at EASY by default
    target_company: Optional[str] = None
    resume_id: Optional[int] = None
    topics: Optional[List[str]] = None
    num_questions: Optional[int] = 5


class InterviewStartResponse(BaseModel):
    interview_id: int
    interview_type: str
    status: str
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    current_difficulty: str = "EASY"
    first_question: Optional[QuestionCandidateView] = None
    questions: List[QuestionCandidateView]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnswerSubmitRequest(BaseModel):
    question_id: Optional[int] = None
    question_text: Optional[str] = None
    answer_text: Optional[str] = None
    time_taken_seconds: Optional[int] = 60
    audio_path: Optional[str] = None
    generate_followup: Optional[bool] = False
    is_skipped: Optional[bool] = False


class QuestionPerformanceItem(BaseModel):
    question_id: Optional[int] = None
    question_text: Optional[str] = None
    candidate_answer: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    keywords_detected: List[str] = []
    time_taken_seconds: Optional[int] = 0


class InterviewCompleteResponse(BaseModel):
    interview_id: int
    status: str
    overall_score: float
    technical_score: float
    communication_score: float
    confidence_score: float
    problem_solving_score: Optional[float] = None
    summary: str
    overall_performance: Optional[str] = None
    technical_knowledge: Optional[str] = None
    problem_solving: Optional[str] = None
    communication: Optional[str] = None
    strong_areas: List[str] = []
    weak_areas: List[str] = []
    topics_needing_improvement: List[str] = []
    question_wise_performance: List[QuestionPerformanceItem] = []
    recommended_preparation_topics: List[str] = []
    strengths: List[str] = []
    improvements: List[str] = []
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnswerSubmitResponse(BaseModel):
    answer_id: int
    question_id: Optional[int] = None
    score: float
    correctness: Optional[float] = None
    technical_accuracy: Optional[float] = None
    reasoning_depth: Optional[float] = None
    relevance: Optional[float] = None
    completeness: Optional[float] = None
    communication_clarity: Optional[float] = None
    feedback: str
    keywords_detected: List[str] = []
    time_taken_seconds: int = 0
    adapted_difficulty: Optional[str] = None
    upgradation_analysis: Optional[str] = None
    interview_stopped: bool = False
    stop_reason: Optional[str] = None  # None, INCORRECT_ANSWER, SKIPPED_QUESTION, INTERVIEW_COMPLETED
    next_question: Optional[QuestionCandidateView] = None
    followup_question: Optional[QuestionCandidateView] = None
    final_report: Optional[InterviewCompleteResponse] = None


class FollowupQuestionRequest(BaseModel):
    question_id: Optional[int] = None
    question_text: str
    candidate_answer: str
    role: Optional[str] = "Software Engineer"
    difficulty: Optional[str] = "MEDIUM"


class TTSAudioRequest(BaseModel):
    text: str


class InterviewHistoryItem(BaseModel):
    id: int
    interview_type: str
    status: str
    score: Optional[float] = None
    job_id: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InterviewDetailResponse(BaseModel):
    id: int
    user_id: int
    job_id: Optional[int] = None
    interview_type: str
    status: str
    score: Optional[float] = None
    feedback: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    overall_performance: Optional[str] = None
    technical_knowledge: Optional[str] = None
    problem_solving: Optional[str] = None
    communication: Optional[str] = None
    strong_areas: List[str] = []
    weak_areas: List[str] = []
    topics_needing_improvement: List[str] = []
    question_wise_performance: List[Dict[str, Any]] = []
    recommended_preparation_topics: List[str] = []
    answers: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(from_attributes=True)
