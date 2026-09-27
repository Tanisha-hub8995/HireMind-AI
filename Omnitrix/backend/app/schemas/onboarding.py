from pydantic import BaseModel


class OnboardingRequest(BaseModel):
    education: str | None = None
    experience: str | None = None
    career_goal: str | None = None


class OnboardingResponse(BaseModel):
    message: str
    user_id: int
    education: str | None = None
    experience: str | None = None
    career_goal: str | None = None