from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class CertificateItem(BaseModel):
    id: str
    certificate_number: str
    title: str
    recipient_name: str
    recipient_email: str
    assessment_id: Optional[int] = None
    assessment_title: str
    score: float = 0.0
    percentage: float = 0.0
    total_stars: int = 1
    level_title: str = "Apprentice Engineer (1-Star)"
    issue_date: datetime
    verification_url: str
    download_url: str


class CertificatesResponse(BaseModel):
    user_id: int
    certificates: List[CertificateItem] = []
    total_certificates: int = 0


class CertificateGenerateRequest(BaseModel):
    assessment_id: Optional[int] = None
