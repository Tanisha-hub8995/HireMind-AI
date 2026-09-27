from pydantic import BaseModel

from app.database.enums import QuestionStatus


# ============================================================
# SAVE ANSWER REQUEST
# ============================================================

class SaveAnswerRequest(BaseModel):
    selected_option: str | None = None
    time_spent_seconds: int = 0


# ============================================================
# SAVE ANSWER RESPONSE
# ============================================================

class SaveAnswerResponse(BaseModel):
    assessment_id: int
    question_id: int
    selected_option: str | None
    status: QuestionStatus
    time_spent_seconds: int