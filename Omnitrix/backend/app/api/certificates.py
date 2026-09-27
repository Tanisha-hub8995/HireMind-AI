from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.certificate import CertificateGenerateRequest, CertificateItem, CertificatesResponse
from app.services.certificate_service import CertificateService

router = APIRouter(prefix="/certificates", tags=["Certificates"])
certificate_service = CertificateService()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=CertificatesResponse)
def get_user_certificates(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Retrieve all assessment completion certificates generated for the current user."""
    return certificate_service.get_user_certificates(db=db, user=current_user)


@router.post("/generate", response_model=CertificatesResponse)
def generate_assessment_certificate(
    request: CertificateGenerateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Generate or retrieve a certificate after completing an assessment."""
    return certificate_service.get_user_certificates(db=db, user=current_user)


@router.get("/download/latest")
def download_latest_certificate_pdf(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Download the latest assessment completion certificate as a high-resolution PDF file."""
    pdf_bytes = certificate_service.generate_certificate_pdf(db=db, user=current_user)
    filename = f"Certificate_{current_user.id}_Latest.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf",
        },
    )


@router.get("/{assessment_id}/download")
def download_assessment_certificate_pdf(
    assessment_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Download an assessment-specific certificate as a high-resolution PDF file."""
    pdf_bytes = certificate_service.generate_certificate_pdf(db=db, user=current_user, assessment_id=assessment_id)
    filename = f"Assessment_Certificate_{assessment_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf",
        },
    )
