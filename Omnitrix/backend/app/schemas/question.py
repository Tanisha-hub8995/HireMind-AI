from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, field_validator


class QuestionBase(BaseModel):
    section: Optional[str] = "TECHNICAL"
    question_text: str
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_option: Optional[str] = None
    difficulty: Optional[str] = "MEDIUM"
    expected_time_seconds: Optional[int] = 60
    positive_mark: Optional[float] = 1.0
    negative_mark: Optional[float] = 0.0
    is_active: Optional[bool] = True


class QuestionCreate(QuestionBase):
    pass


class QuestionResponse(QuestionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class QuestionCandidateView(BaseModel):
    id: int
    section: Optional[str] = None
    question_text: str
    difficulty: Optional[str] = None
    expected_time_seconds: Optional[int] = 60
    audio_url: Optional[str] = None

    @field_validator("section", "difficulty", mode="before")
    @classmethod
    def transform_enum_to_str(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if hasattr(v, "value"):
            return str(v.value)
        return str(v)

    model_config = ConfigDict(from_attributes=True)


