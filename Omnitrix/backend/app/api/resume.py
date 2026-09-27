import logging
import os
from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel as _BaseModel


class ResumeTextRequest(_BaseModel):
    text: str
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.resume_ai import ResumeAI
from app.database.database import SessionLocal
from app.dependencies.auth import get_current_user, get_optional_current_user
from app.models.resume import Resume
from app.models.resume_section import ResumeSection
from app.models.user import User
from app.schemas.resume import GeneratedResume, ResumeAnalysis, ResumeGenerateRequest
from app.services.career_recommendations import CareerRecommendationEngine
from app.services.resume_analyzer import ResumeAnalyzer
from app.services.resume_pdf import build_resume_pdf
from app.services.skill_normalizer import SkillNormalizer
from app.services.vector_store import InMemoryVectorStore


router = APIRouter(prefix="/resume", tags=["Resume"])
logger = logging.getLogger(__name__)

vector_store = InMemoryVectorStore()
resume_analyzer = ResumeAnalyzer()
career_engine = CareerRecommendationEngine()
resume_ai = ResumeAI()
skill_normalizer = SkillNormalizer()
MAX_RESUME_BYTES = int(os.getenv("MAX_RESUME_BYTES", str(10 * 1024 * 1024)))
RESUME_UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads" / "resumes"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def extract_document_text(content: bytes, filename: str, content_type: str | None) -> str:
    suffix = Path(filename).suffix.lower()
    try:
        if suffix == ".pdf" or content_type == "application/pdf":
            from io import BytesIO
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

        if suffix in (".docx",) or content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            from io import BytesIO
            from docx import Document
            document = Document(BytesIO(content))
            return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()

        return content.decode("utf-8", errors="ignore").strip()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read {suffix or 'document'} file: {exc}",
        ) from exc


def _normalise_skills(raw_skills: list) -> list[dict]:
    """Convert a list that may contain str or dict items to ExtractedSkill-compatible dicts."""
    normalised = []
    for item in raw_skills:
        if isinstance(item, dict):
            normalised.append({
                "name": item.get("name", ""),
                "category": item.get("category"),
                "evidence": item.get("evidence"),
                "confidence": float(item.get("confidence", 0.8)),
            })
        elif isinstance(item, str) and item.strip():
            normalised.append({
                "name": item.strip(),
                "category": "Technical Skill",
                "evidence": item.strip(),
                "confidence": 0.8,
            })
    return [s for s in normalised if s["name"]]


@router.post("/upload")
def upload_resume(
    file: UploadFile = File(...),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Session = Depends(get_db),
):
    suffix = Path(file.filename or "").suffix.lower() if file.filename else ""
    if suffix not in (".pdf", ".docx", ".txt"):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, or TXT resumes are accepted")

    content = file.file.read(MAX_RESUME_BYTES + 1)
    if len(content) > MAX_RESUME_BYTES:
        raise HTTPException(status_code=413, detail="Resume exceeds the maximum file size (10 MB)")

    if suffix == ".pdf" and not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF")

    RESUME_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid4().hex}{suffix}"
    stored_path = RESUME_UPLOAD_DIR / stored_filename
    stored_path.write_bytes(content)

    resume_record = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_path=str(stored_path),
        file_type=file.content_type or "application/octet-stream",
        title=f"Resume for {current_user.name}",
        processing_status="processing",
    )
    db.add(resume_record)
    db.commit()
    db.refresh(resume_record)

    try:
        # ── Step 1: Extract text ─────────────────────────────────────────────
        text = extract_document_text(content, file.filename, file.content_type)
        if len(text.strip()) < 40:
            raise ValueError("The document does not contain enough extractable text. "
                             "Make sure the PDF is not scanned/image-only.")

        # ── Step 2: Deterministic skill extraction ───────────────────────────
        deterministic = resume_analyzer.analyze(text, user_id=None)
        raw_skills = deterministic.get("skills", [])

        # ── Step 3: AI enrichment via Qwen (graceful fallback when unavailable)
        try:
            ai_result = resume_ai.evaluate(text, deterministic)
        except Exception as ai_exc:
            logger.warning("AI evaluation failed, using deterministic fallback: %s", ai_exc)
            ai_result = None

        if ai_result and ai_result.get("status") == "complete":
            # Merge AI skills with deterministic ones
            ai_skills = _normalise_skills(ai_result.get("skills", []))
            skill_names_seen = {s["name"].lower() for s in ai_skills}
            for s in _normalise_skills(raw_skills):
                if s["name"].lower() not in skill_names_seen:
                    ai_skills.append(s)
                    skill_names_seen.add(s["name"].lower())
            
            merged = {
                "skills": ai_skills,
                "education": ai_result.get("education") or deterministic.get("education", []),
                "experience": ai_result.get("experience") or deterministic.get("experience", []),
                "internships": ai_result.get("internships") or deterministic.get("internships", []),
                "projects": ai_result.get("projects") or deterministic.get("projects", []),
                "certifications": ai_result.get("certifications") or deterministic.get("certifications", []),
                "achievements": ai_result.get("achievements") or deterministic.get("achievements", []),
                "suggested_roles": ai_result.get("suggested_roles") or deterministic.get("suggested_roles", []),
                "domains": ai_result.get("domains") or deterministic.get("domains", []),
                "status": "complete",
                "provider": ai_result.get("provider", "qwen"),
            }
        else:
            # Deterministic path populated with rich parsed sections
            merged = {
                "skills": _normalise_skills(raw_skills),
                "education": deterministic.get("education", []),
                "experience": deterministic.get("experience", []),
                "internships": deterministic.get("internships", []),
                "projects": deterministic.get("projects", []),
                "certifications": deterministic.get("certifications", []),
                "achievements": deterministic.get("achievements", []),
                "suggested_roles": deterministic.get("suggested_roles", []),
                "domains": deterministic.get("domains", []),
                "status": "complete",
                "provider": "deterministic-nlp",
            }

        # ── Step 4: Validate with Pydantic schema ────────────────────────────
        try:
            validated = ResumeAnalysis.model_validate(merged)
        except ValidationError as ve:
            logger.warning("ResumeAnalysis validation error, rebuilding: %s", ve)
            validated = ResumeAnalysis(
                skills=_normalise_skills(raw_skills),
                education=deterministic.get("education", []),
                experience=deterministic.get("experience", []),
                internships=deterministic.get("internships", []),
                projects=deterministic.get("projects", []),
                certifications=deterministic.get("certifications", []),
                achievements=deterministic.get("achievements", []),
                suggested_roles=deterministic.get("suggested_roles", []),
                domains=deterministic.get("domains", []),
            )

        analysis = skill_normalizer.validate(validated.model_dump(), text)

        # ── Step 5: Section detection ────────────────────────────────────────
        sections = vector_store._split_sections(text)
        for section_type, section_text in sections:
            db.add(ResumeSection(
                resume_id=resume_record.id,
                section_type=section_type,
                section_text=section_text,
            ))

        # ── Step 6: Skill persistence to DB ─────────────────────────────────
        persisted_skills = skill_normalizer.persist(db, resume_record.id, analysis)

        # ── Step 7: FAISS vector indexing (graceful — skip if ST model unavailable)
        vectors_created = 0
        try:
            embedding_record = vector_store.add_document(
                current_user.id,
                text,
                metadata={"resume_id": resume_record.id, "skills": analysis["skills"]},
                section_name="full_resume",
                resume_id=resume_record.id,
            )
            vectors_created += len(embedding_record["sections"])

            for item in persisted_skills:
                skill_vec = vector_store.add_document(
                    current_user.id,
                    item["name"],
                    metadata={
                        "resume_id": resume_record.id,
                        "type": "skill",
                        "skill_id": item["id"],
                        "canonical_skill": item["name"],
                    },
                    section_name=f"skill:{item['name']}",
                    resume_id=resume_record.id,
                )
                vectors_created += len(skill_vec["sections"])
        except Exception as vec_exc:
            logger.warning("Vector indexing skipped (FAISS unavailable): %s", vec_exc)

        # ── Step 8: Persist final state ──────────────────────────────────────
        resume_record.raw_text = text
        resume_record.summary = text[:500]
        resume_record.extracted_skills = [item["name"] for item in analysis["skills"]]
        resume_record.payload = {"analysis": analysis, "skills": persisted_skills}
        resume_record.processing_status = "completed"
        db.commit()
        logger.info(
            "Resume processing completed resume_id=%s user_id=%s skills=%s",
            resume_record.id, current_user.id, len(persisted_skills)
        )

    except (ValueError, OSError) as exc:
        db.rollback()
        _mark_failed(db, resume_record.id, str(exc))
        raise HTTPException(status_code=422, detail=f"Resume processing failed: {exc}") from exc
    except Exception as exc:
        db.rollback()
        _mark_failed(db, resume_record.id, str(exc))
        logger.exception("Unexpected error during resume processing")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc

    return {
        "message": "Resume uploaded and analysed successfully",
        "user_id": current_user.id,
        "resume_id": resume_record.id,
        "filename": resume_record.original_filename,
        "processing_status": resume_record.processing_status,
        "sections_detected": len(sections),
        "skills_extracted": len(persisted_skills),
        "vectors_created": vectors_created,
        "analysis": analysis,
    }


def _mark_failed(db: Session, resume_id: int, error: str) -> None:
    try:
        r = db.query(Resume).filter(Resume.id == resume_id).first()
        if r:
            r.processing_status = "failed"
            r.payload = {"error": error}
            db.commit()
    except Exception:
        pass


@router.get("/", response_model=list[dict])
def list_resumes(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """List all resumes uploaded by the current user."""
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "filename": r.original_filename,
            "processing_status": r.processing_status,
            "skills_extracted": len(r.extracted_skills or []),
            "created_at": r.created_at,
        }
        for r in resumes
    ]


@router.get("/{resume_id}")
def get_resume(
    resume_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Get full analysis of a specific resume."""
    r = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
    ).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {
        "id": r.id,
        "filename": r.original_filename,
        "processing_status": r.processing_status,
        "extracted_skills": r.extracted_skills or [],
        "summary": r.summary,
        "analysis": (r.payload or {}).get("analysis", {}),
        "created_at": r.created_at,
    }


@router.post("/analyze")
def analyze_resume_text(
    body: ResumeTextRequest,
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
):
    """Analyse raw resume text and return skills, education, experience, projects,

    certifications, achievements, suggested roles, domains, career matches, and AI enrichment.

    Request body: {"text": "paste your resume text here"}
    """
    text = body.text
    if not text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty")

    # Step 1: comprehensive deterministic skill and section extraction
    analysis = resume_analyzer.analyze(text, user_id=None)
    raw_skills = analysis.get("skills", [])
    skill_names: list[str] = [
        (s["name"] if isinstance(s, dict) else s) for s in raw_skills if s
    ]

    # Step 2: career recommendations
    try:
        recommendations = career_engine.recommend(skill_names)
    except Exception as rec_exc:
        logger.warning("Career recommendations failed: %s", rec_exc)
        recommendations = []

    # Step 3: AI enrichment via Qwen/Gemini or rich semantic analysis
    ai_payload: dict = {}
    try:
        ai_result = resume_ai.evaluate(text, analysis)
        if ai_result and ai_result.get("status") == "complete":
            ai_skills = _normalise_skills(ai_result.get("skills", []))
            if ai_skills:
                skill_names = [s["name"] for s in ai_skills]
                analysis["skills"] = skill_names
            ai_payload = {
                k: v for k, v in ai_result.items()
                if k not in ("status", "provider", "skills")
            }
    except Exception as ai_exc:
        logger.warning("AI evaluation skipped: %s", ai_exc)

    return {
        "message": "Resume analysis complete",
        "user_id": current_user.id if current_user else None,
        "skills": skill_names,
        "education": analysis.get("education", []),
        "experience": analysis.get("experience", []),
        "internships": analysis.get("internships", []),
        "projects": analysis.get("projects", []),
        "certifications": analysis.get("certifications", []),
        "achievements": analysis.get("achievements", []),
        "suggested_roles": analysis.get("suggested_roles", []),
        "domains": analysis.get("domains", []),
        "career_recommendations": recommendations,
        "skill_gap": {
            "missing_skills": recommendations[0]["missing_skills"] if recommendations else [],
        },
        **({"ai_evaluation": ai_payload} if ai_payload else {}),
    }



@router.post("/generate", response_model=GeneratedResume)
def generate_resume(
    request: ResumeGenerateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    generated = resume_ai.generate_resume(request.name, request.choice)
    if generated.get("status") != "complete":
        raise HTTPException(
            status_code=503,
            detail=generated.get("message", "CV generation is unavailable"),
        )
    try:
        validated = GeneratedResume.model_validate(generated)
    except ValidationError as exc:
        raise HTTPException(status_code=502, detail="AI returned an invalid CV structure") from exc
    return validated


@router.post("/generate/pdf")
def generate_resume_pdf(
    request: ResumeGenerateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    generated = resume_ai.generate_resume(request.name, request.choice)
    if generated.get("status") != "complete":
        raise HTTPException(
            status_code=503,
            detail=generated.get("message", "CV generation is unavailable"),
        )
    try:
        validated = GeneratedResume.model_validate(generated)
        pdf_bytes = build_resume_pdf(validated)
    except (ValidationError, ValueError, OSError) as exc:
        raise HTTPException(status_code=502, detail="Unable to create the resume PDF") from exc

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="generated_resume.pdf"'},
    )
