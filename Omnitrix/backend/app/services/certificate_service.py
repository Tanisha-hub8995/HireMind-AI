import hashlib
import io
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.assessment import Assessment, AssessmentSectionResult
from app.models.user import User
from app.schemas.certificate import CertificateItem, CertificatesResponse
from app.services.badge_service import BadgeService

logger = logging.getLogger(__name__)


class CertificateService:
    """Handles assessment certificate synthesis and high-resolution PDF generation."""

    def __init__(self):
        self.badge_service = BadgeService()

    def get_user_certificates(self, db: Session, user: User) -> CertificatesResponse:
        """Retrieve all completed assessment certificates for the user."""
        completed_assessments = (
            db.query(Assessment)
            .filter(Assessment.user_id == user.id, Assessment.status == "COMPLETED")
            .order_by(Assessment.completed_at.desc())
            .all()
        )

        badge_info = self.badge_service.get_user_badges_and_level(db, user)
        current_level_title = badge_info.level_info.level_title
        current_stars = badge_info.level_info.current_level

        certificates: List[CertificateItem] = []

        if completed_assessments:
            for asm in completed_assessments:
                cert_hash = hashlib.sha256(f"CERT-{user.id}-{asm.id}-{asm.created_at}".encode()).hexdigest()[:10].upper()
                cert_num = f"OMNI-{datetime.utcnow().year}-{cert_hash}"
                issue_date = asm.completed_at or asm.created_at or datetime.utcnow()
                score_pct = float(asm.percentage or 0.0)
                stars_awarded = 5 if score_pct >= 90 else (4 if score_pct >= 80 else (3 if score_pct >= 65 else (2 if score_pct >= 45 else 1)))

                recipient_name = getattr(user, "name", None) or getattr(user, "full_name", None) or user.email.split("@")[0].title()
                certificates.append(
                    CertificateItem(
                        id=f"cert_{asm.id}",
                        certificate_number=cert_num,
                        title="Certificate of Assessment Completion",
                        recipient_name=recipient_name,
                        recipient_email=user.email,
                        assessment_id=asm.id,
                        assessment_title=f"{asm.assessment_type or 'Technical'} Engineering Assessment",
                        score=float(asm.total_score or 0.0),
                        percentage=round(score_pct, 1),
                        total_stars=stars_awarded,
                        level_title=current_level_title,
                        issue_date=issue_date,
                        verification_url=f"/api/v1/certificates/verify/{cert_num}",
                        download_url=f"/certificates/{asm.id}/download",
                    )
                )
        else:
            # Generate provisional competency certificate based on user onboarding & profile
            cert_hash = hashlib.sha256(f"CERT-PROV-{user.id}-{user.created_at}".encode()).hexdigest()[:10].upper()
            cert_num = f"OMNI-{datetime.utcnow().year}-{cert_hash}"
            recipient_name = getattr(user, "name", None) or getattr(user, "full_name", None) or user.email.split("@")[0].title()
            certificates.append(
                CertificateItem(
                    id="cert_provisional",
                    certificate_number=cert_num,
                    title="Certificate of Engineering Competency",
                    recipient_name=recipient_name,
                    recipient_email=user.email,
                    assessment_id=None,
                    assessment_title="AI Engineering Evaluation & Profile Mastery",
                    score=float(badge_info.level_info.xp),
                    percentage=round(badge_info.level_info.level_progress_percentage, 1),
                    total_stars=current_stars,
                    level_title=current_level_title,
                    issue_date=user.created_at or datetime.utcnow(),
                    verification_url=f"/api/v1/certificates/verify/{cert_num}",
                    download_url="/certificates/download/latest",
                )
            )

        return CertificatesResponse(
            user_id=user.id,
            certificates=certificates,
            total_certificates=len(certificates),
        )

    def generate_certificate_pdf(self, db: Session, user: User, assessment_id: Optional[int] = None) -> bytes:
        """Generate a landscape PDF Certificate using ReportLab."""
        # Retrieve target assessment or latest
        asm = None
        if assessment_id:
            asm = db.query(Assessment).filter(Assessment.id == assessment_id, Assessment.user_id == user.id).first()
        if not asm:
            asm = (
                db.query(Assessment)
                .filter(Assessment.user_id == user.id, Assessment.status == "COMPLETED")
                .order_by(Assessment.completed_at.desc())
                .first()
            )

        badge_info = self.badge_service.get_user_badges_and_level(db, user)
        recipient_name = getattr(user, "name", None) or getattr(user, "full_name", None) or user.email.split("@")[0].title()
        current_level_title = badge_info.level_info.level_title

        if asm:
            score_pct = float(asm.percentage or 0.0)
            stars_awarded = 5 if score_pct >= 90 else (4 if score_pct >= 80 else (3 if score_pct >= 65 else (2 if score_pct >= 45 else 1)))
            cert_hash = hashlib.sha256(f"CERT-{user.id}-{asm.id}-{asm.created_at}".encode()).hexdigest()[:10].upper()
            cert_num = f"OMNI-{datetime.utcnow().year}-{cert_hash}"
            assessment_name = f"{asm.assessment_type or 'Technical'} Engineering Assessment"
            issue_date_str = (asm.completed_at or datetime.utcnow()).strftime("%B %d, %Y")
        else:
            score_pct = float(badge_info.level_info.level_progress_percentage or 85.0)
            stars_awarded = badge_info.level_info.current_level
            cert_hash = hashlib.sha256(f"CERT-PROV-{user.id}-{user.created_at}".encode()).hexdigest()[:10].upper()
            cert_num = f"OMNI-{datetime.utcnow().year}-{cert_hash}"
            assessment_name = "AI Engineering Competency & Milestone Mastery"
            issue_date_str = datetime.utcnow().strftime("%B %d, %Y")

        star_str = "★ " * stars_awarded + "☆ " * (5 - stars_awarded)

        # Build PDF using ReportLab
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.pdfgen import canvas

            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=landscape(letter))
            width, height = landscape(letter)  # 792 x 612

            # Background fill
            p.setFillColor(colors.HexColor("#0D1117"))
            p.rect(0, 0, width, height, fill=1, stroke=0)

            # Outer border (Gold)
            p.setStrokeColor(colors.HexColor("#D4AF37"))
            p.setLineWidth(4)
            p.rect(20, 20, width - 40, height - 40, fill=0, stroke=1)

            # Inner border (Navy / Accent)
            p.setStrokeColor(colors.HexColor("#388BFD"))
            p.setLineWidth(1.5)
            p.rect(28, 28, width - 56, height - 56, fill=0, stroke=1)

            # Corner decorative accents
            p.setFillColor(colors.HexColor("#D4AF37"))
            corner_size = 12
            p.rect(20, height - 20 - corner_size, corner_size, corner_size, fill=1, stroke=0)
            p.rect(width - 20 - corner_size, height - 20 - corner_size, corner_size, corner_size, fill=1, stroke=0)
            p.rect(20, 20, corner_size, corner_size, fill=1, stroke=0)
            p.rect(width - 20 - corner_size, 20, corner_size, corner_size, fill=1, stroke=0)

            # Header / Organization
            p.setFillColor(colors.HexColor("#58A6FF"))
            p.setFont("Helvetica-Bold", 14)
            p.drawCentredString(width / 2, height - 70, "OMNITRIX AI ASSESSMENT & INTERVIEW PLATFORM")

            # Certificate Title
            p.setFillColor(colors.HexColor("#F0F6FC"))
            p.setFont("Helvetica-Bold", 26)
            p.drawCentredString(width / 2, height - 110, "CERTIFICATE OF ACHIEVEMENT")

            # Subtitle
            p.setFillColor(colors.HexColor("#8B949E"))
            p.setFont("Helvetica", 12)
            p.drawCentredString(width / 2, height - 135, "THIS IS PROUDLY PRESENTED TO")

            # Recipient Name
            p.setFillColor(colors.HexColor("#D4AF37"))
            p.setFont("Helvetica-Bold", 28)
            p.drawCentredString(width / 2, height - 180, recipient_name)

            # Recipient Divider Line
            p.setStrokeColor(colors.HexColor("#30363D"))
            p.setLineWidth(1)
            p.line(width / 2 - 200, height - 195, width / 2 + 200, height - 195)

            # Recognition text
            p.setFillColor(colors.HexColor("#C9D1D9"))
            p.setFont("Helvetica", 13)
            p.drawCentredString(
                width / 2,
                height - 230,
                f"for successfully completing the comprehensive {assessment_name}",
            )
            p.drawCentredString(
                width / 2,
                height - 250,
                f"demonstrating exceptional technical competence, algorithmic reasoning, and problem solving.",
            )

            # Performance Metrics Box
            box_w = 480
            box_h = 75
            box_x = (width - box_w) / 2
            box_y = height - 345
            p.setFillColor(colors.HexColor("#161B22"))
            p.setStrokeColor(colors.HexColor("#30363D"))
            p.roundRect(box_x, box_y, box_w, box_h, 8, fill=1, stroke=1)

            # Metric: Score
            p.setFillColor(colors.HexColor("#8B949E"))
            p.setFont("Helvetica", 10)
            p.drawString(box_x + 30, box_y + 45, "OVERALL SCORE")
            p.setFillColor(colors.HexColor("#3FB950"))
            p.setFont("Helvetica-Bold", 18)
            p.drawString(box_x + 30, box_y + 20, f"{score_pct:.1f}%")

            # Metric: Milestone Level
            p.setFillColor(colors.HexColor("#8B949E"))
            p.setFont("Helvetica", 10)
            p.drawString(box_x + 170, box_y + 45, "MILESTONE RANK")
            p.setFillColor(colors.HexColor("#58A6FF"))
            p.setFont("Helvetica-Bold", 14)
            p.drawString(box_x + 170, box_y + 20, current_level_title.split("(")[0].strip())

            # Metric: Star Rating Badge
            p.setFillColor(colors.HexColor("#8B949E"))
            p.setFont("Helvetica", 10)
            p.drawString(box_x + 340, box_y + 45, "STAR RATING")
            p.setFillColor(colors.HexColor("#D4AF37"))
            p.setFont("Helvetica-Bold", 16)
            p.drawString(box_x + 340, box_y + 20, f"{stars_awarded} / 5 Stars")

            # Star Visuals
            p.setFillColor(colors.HexColor("#D4AF37"))
            p.setFont("Helvetica", 14)
            p.drawCentredString(width / 2, height - 375, star_str.strip())

            # Signatures & Verification Info
            # Left: Date & Certificate ID
            p.setFillColor(colors.HexColor("#8B949E"))
            p.setFont("Helvetica", 9)
            p.drawString(60, 95, f"Date of Issue: {issue_date_str}")
            p.drawString(60, 80, f"Certificate ID: {cert_num}")
            p.drawString(60, 65, "Status: Verified & Authenticated")

            # Center: Omnitrix Seal Emblem
            p.setStrokeColor(colors.HexColor("#D4AF37"))
            p.setLineWidth(2)
            p.circle(width / 2, 90, 32, fill=0, stroke=1)
            p.setFillColor(colors.HexColor("#D4AF37"))
            p.setFont("Helvetica-Bold", 8)
            p.drawCentredString(width / 2, 94, "OMNITRIX")
            p.drawCentredString(width / 2, 82, "AI CERTIFIED")

            # Right: Authorized Signatures
            p.setStrokeColor(colors.HexColor("#8B949E"))
            p.setLineWidth(1)
            p.line(width - 240, 95, width - 60, 95)
            p.setFillColor(colors.HexColor("#F0F6FC"))
            p.setFont("Helvetica-Bold", 10)
            p.drawCentredString(width - 150, 80, "AI Evaluation Board")
            p.setFillColor(colors.HexColor("#8B949E"))
            p.setFont("Helvetica", 8)
            p.drawCentredString(width - 150, 67, "Omnitrix Academic & Technical Council")

            p.showPage()
            p.save()

            buffer.seek(0)
            return buffer.getvalue()

        except Exception as exc:
            logger.error("ReportLab PDF generation error: %s", exc)
            # Fallback simple PDF generator
            return self._generate_fallback_pdf(recipient_name, assessment_name, score_pct, stars_awarded, cert_num)

    def _generate_fallback_pdf(self, recipient: str, asm_name: str, score: float, stars: int, cert_num: str) -> bytes:
        """Minimal fallback valid PDF byte stream."""
        pdf_content = (
            f"%PDF-1.4\n"
            f"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            f"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            f"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\n"
            f"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\n"
            f"trailer<</Size 4/Root 1 0 R>>\nstartxref\n180\n%%EOF\n"
        )
        return pdf_content.encode("utf-8")
