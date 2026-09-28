from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, List, Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.ai.interview_ai import InterviewAI
from app.database.database import SessionLocal
from app.database.enums import AssessmentSection, DifficultyLevel
from app.dependencies.auth import get_current_user
from app.models.answer import Answer
from app.models.interview import Interview
from app.models.job import Job
from app.models.question import Question
from app.models.result import InterviewResult
from app.models.user import User
from app.schemas.interview import (
    AnswerSubmitRequest,
    AnswerSubmitResponse,
    FollowupQuestionRequest,
    InterviewCompleteResponse,
    InterviewDetailResponse,
    InterviewHistoryItem,
    InterviewStartRequest,
    InterviewStartResponse,
    TTSAudioRequest,
)
from app.schemas.question import QuestionCandidateView

router = APIRouter(prefix="/interviews", tags=["Interviews"])
interview_ai = InterviewAI()

AUDIO_DIR = Path(__file__).resolve().parents[2] / "uploads" / "audio"
AUDIO_ANSWERS_DIR = AUDIO_DIR / "answers"
AUDIO_QUESTIONS_DIR = AUDIO_DIR / "questions"
AUDIO_ANSWERS_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)


def _build_question_view(q: Any, interview_id: Optional[int] = None) -> Optional[QuestionCandidateView]:
    """Construct a candidate question view with automatic TTS audio URL populated."""
    if not q:
        return None
    view = QuestionCandidateView.model_validate(q)
    if view.id and view.id > 0:
        view.audio_url = f"/interviews/questions/{view.id}/audio"
    return view



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_or_create_interview(db: Session, interview_id: int, user_id: int) -> Interview:
    """Find interview by ID, or fallback to user's active/latest session, or auto-create one."""
    if interview_id and interview_id > 0:
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if interview:
            return interview

    # Look up latest interview for user
    interview = (
        db.query(Interview)
        .filter(Interview.user_id == user_id)
        .order_by(Interview.created_at.desc())
        .first()
    )
    if interview:
        return interview

    # Auto-initialize an active interview session
    new_interview = Interview(
        user_id=user_id,
        interview_type="TECHNICAL",
        status="IN_PROGRESS",
        scheduled_at=datetime.utcnow(),
    )
    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)
    return new_interview


@router.post("/start", response_model=InterviewStartResponse)
def start_interview(
    request: InterviewStartRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """1 & 2. Prepare candidate profile, retrieve/generate deduplicated EASY questions by default, and initialize interview session."""
    valid_job_id = request.job_id if (request.job_id and request.job_id > 0) else None
    if valid_job_id:
        if not db.query(Job).filter(Job.id == valid_job_id).first():
            valid_job_id = None

    # Always start interview at EASY level initially
    initial_diff = request.difficulty or "EASY"

    interview = Interview(
        user_id=current_user.id,
        job_id=valid_job_id,
        interview_type=request.interview_type or "TECHNICAL",
        status="IN_PROGRESS",
        scheduled_at=datetime.utcnow(),
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    # 1. Candidate profile preparation & 2. Question preparation with deduplication starting at EASY
    session_data = interview_ai.prepare_session(
        db=db,
        user_id=current_user.id,
        role=request.role or "Software Engineer",
        difficulty=initial_diff,
        interview_type=request.interview_type or "TECHNICAL",
        topics=request.topics,
        resume_id=request.resume_id,
        target_company=request.target_company,
        num_questions=request.num_questions or 5,
    )

    questions = session_data["questions"]
    first_q = questions[0] if questions else None

    return InterviewStartResponse(
        interview_id=interview.id,
        interview_type=interview.interview_type,
        status=interview.status,
        target_role=request.role,
        target_company=request.target_company,
        current_difficulty=initial_diff,
        first_question=_build_question_view(first_q, interview.id),
        questions=[_build_question_view(q, interview.id) for q in questions],
        created_at=interview.created_at,
    )


# ---------------------------------------------------------
# Question TTS & Audio Endpoints
# ---------------------------------------------------------

@router.post("/tts")
def post_text_to_speech(
    request: TTSAudioRequest,
):
    """Text-To-Speech (TTS) binary audio generator from JSON payload."""
    audio_bytes, mime_type = interview_ai.synthesize_speech_with_mime(request.text)
    return Response(
        content=audio_bytes,
        media_type=mime_type,
        headers={"Content-Disposition": "inline; filename=speech.wav"},
    )


@router.get("/tts")
def get_text_to_speech(text: str = "Please introduce yourself and explain your background."):
    """Text-To-Speech (TTS) binary audio generator from query parameter for HTML5 Audio playback."""
    audio_bytes, mime_type = interview_ai.synthesize_speech_with_mime(text)
    ext = "wav" if "wav" in mime_type else "mp3"
    return Response(
        content=audio_bytes,
        media_type=mime_type,
        headers={
            "Content-Disposition": f"inline; filename=speech.{ext}",
            "Content-Type": mime_type,
            "Content-Length": str(len(audio_bytes)),
            "Accept-Ranges": "bytes",
        },
    )


@router.get("/questions/{question_id}/audio")
def get_question_audio_by_id(
    question_id: int,
    text: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get spoken question audio by question ID with caching."""
    cached_path = AUDIO_QUESTIONS_DIR / f"question_{question_id}.wav"
    if cached_path.exists() and cached_path.stat().st_size > 500:
        return FileResponse(path=str(cached_path), media_type="audio/wav")

    q_text = text
    if not q_text and question_id > 0:
        q = db.query(Question).filter(Question.id == question_id).first()
        if q:
            q_text = q.question_text

    if not q_text:
        q_text = "Please explain your technical approach, data structures, and trade-offs."

    audio_bytes, mime_type = interview_ai.synthesize_speech_with_mime(q_text)
    try:
        cached_path.write_bytes(audio_bytes)
    except Exception:
        pass

    return Response(
        content=audio_bytes,
        media_type=mime_type,
        headers={"Content-Disposition": f"inline; filename=question_{question_id}.wav"},
    )


@router.post("/{interview_id}/skip", response_model=AnswerSubmitResponse)

def skip_interview_question(
    interview_id: int,
    question_id: Optional[int] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Session = Depends(get_db),
):
    """Explicitly skip current question: Immediately stops the interview and generates the final performance report."""
    req = AnswerSubmitRequest(
        question_id=question_id,
        answer_text="[SKIPPED]",
        is_skipped=True,
    )
    return submit_interview_answer(
        interview_id=interview_id,
        request=req,
        current_user=current_user,
        db=db,
    )


@router.post("/{interview_id}/answer", response_model=AnswerSubmitResponse)
def submit_interview_answer(
    interview_id: int,
    request: AnswerSubmitRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """4, 6 & 7. Submit answer:

    - If answer is correct (score >= 50.0) -> AI upgrades difficulty (EASY -> MEDIUM -> HARD) and serves next question.
    - If answer is incorrect or question is skipped -> Immediately stops the interview and returns the final comprehensive evaluation.
    """
    interview = _get_or_create_interview(db=db, interview_id=interview_id, user_id=current_user.id)

    question_text = request.question_text
    expected_section = "PROFESSIONAL_KNOWLEDGE"
    curr_diff = DifficultyLevel.EASY
    valid_question_id = None

    if request.question_id and request.question_id > 0:
        q = db.query(Question).filter(Question.id == request.question_id).first()
        if q:
            valid_question_id = q.id
            question_text = q.question_text
            expected_section = q.section.value if hasattr(q.section, "value") else str(q.section)
            curr_diff = q.difficulty or DifficultyLevel.EASY

    if not valid_question_id and question_text:
        q = db.query(Question).filter(Question.question_text == question_text).first()
        if q:
            valid_question_id = q.id
            expected_section = q.section.value if hasattr(q.section, "value") else str(q.section)
            curr_diff = q.difficulty or DifficultyLevel.EASY

    if not valid_question_id:
        q = db.query(Question).first()
        if q:
            valid_question_id = q.id
            if not question_text:
                question_text = q.question_text
                expected_section = q.section.value if hasattr(q.section, "value") else str(q.section)
                curr_diff = q.difficulty or DifficultyLevel.EASY
        else:
            new_q = Question(
                question_text=question_text or "Explain your technical approach, data structures, and trade-offs.",
                section=AssessmentSection.PROFESSIONAL_KNOWLEDGE,
                difficulty=DifficultyLevel.EASY,
                expected_time_seconds=60,
            )
            db.add(new_q)
            db.commit()
            db.refresh(new_q)
            valid_question_id = new_q.id

    if not question_text:
        question_text = "General Technical Question"

    # Detect if question is skipped or empty
    ans_cleaned = (request.answer_text or "").strip()
    is_skipped = (
        bool(request.is_skipped)
        or not ans_cleaned
        or ans_cleaned.lower() in ["skip", "pass", "no idea", "i don't know", "dont know", "skip question", "n/a", "na", "[skipped]"]
    )

    # 6. Answer evaluation
    if is_skipped:
        eval_result = {
            "score": 0.0,
            "correctness": 0.0,
            "technical_accuracy": 0.0,
            "reasoning_depth": 0.0,
            "relevance": 0.0,
            "completeness": 0.0,
            "communication_clarity": 0.0,
            "feedback": "Question was skipped by candidate without providing technical reasoning.",
            "keywords_detected": [],
        }
    else:
        eval_result = interview_ai.evaluate_response(
            question_text=question_text,
            answer_text=ans_cleaned,
            expected_section=expected_section,
        )

    # 7. Adaptive Analysis: Check if answer is correct (upgrade level) or incorrect/skipped (stop immediately)
    new_difficulty, should_stop, stop_reason, upgradation_text = interview_ai.analyze_upgradation(
        current_difficulty=curr_diff,
        score=eval_result["score"],
        is_skipped=is_skipped,
    )

    # Persist answer record
    answer = Answer(
        question_id=valid_question_id,
        user_id=current_user.id,
        answer_text=request.answer_text if not is_skipped else "[SKIPPED]",
        audio_path=request.audio_path,
        score=eval_result["score"],
        feedback=eval_result["feedback"],
        keywords_detected=eval_result["keywords_detected"],
        time_taken_seconds=request.time_taken_seconds or 60,
        created_at=datetime.utcnow(),
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)

    # Handle Next Question or Immediate Termination
    next_question_view = None
    followup_view = None
    final_report = None

    if should_stop:
        # IMMEDIATELY STOP THE INTERVIEW
        interview.status = "COMPLETED"
        interview.score = eval_result["score"]
        db.commit()

        # Generate full report immediately
        final_rep_dict = interview_ai.complete_session(db=db, interview_id=interview.id)
        final_report = InterviewCompleteResponse(
            interview_id=interview.id,
            status=interview.status,
            overall_score=final_rep_dict["overall_score"],
            technical_score=final_rep_dict["technical_score"],
            problem_solving_score=final_rep_dict.get("problem_solving_score", 65.0),
            communication_score=final_rep_dict["communication_score"],
            confidence_score=final_rep_dict.get("confidence_score", 70.0),
            summary=final_rep_dict["summary"],
            overall_performance=final_rep_dict.get("overall_performance"),
            technical_knowledge=final_rep_dict.get("technical_knowledge"),
            problem_solving=final_rep_dict.get("problem_solving"),
            communication=final_rep_dict.get("communication"),
            strong_areas=final_rep_dict.get("strong_areas", []),
            weak_areas=final_rep_dict.get("weak_areas", []),
            topics_needing_improvement=final_rep_dict.get("topics_needing_improvement", []),
            question_wise_performance=final_rep_dict.get("question_wise_performance", []),
            recommended_preparation_topics=final_rep_dict.get("recommended_preparation_topics", []),
            strengths=final_rep_dict.get("strengths", []),
            improvements=final_rep_dict.get("improvements", []),
            completed_at=interview.completed_at or datetime.utcnow(),
        )
    else:
        # CORRECT ANSWER: Fetch next question at UPGRADED difficulty
        next_q = interview_ai.get_next_question(
            db=db,
            user_id=current_user.id,
            target_difficulty=new_difficulty,
        )
        if next_q:
            next_question_view = _build_question_view(next_q, interview.id)

        # Optional follow-up question if requested
        if request.generate_followup and ans_cleaned:
            followup_q = interview_ai.generate_followup(
                db=db,
                previous_question=question_text,
                candidate_answer=ans_cleaned,
                difficulty=new_difficulty,
            )
            if followup_q:
                followup_view = _build_question_view(followup_q, interview.id)

    return AnswerSubmitResponse(
        answer_id=answer.id,
        question_id=valid_question_id or request.question_id or 0,
        score=answer.score,
        correctness=eval_result.get("correctness") or round(answer.score, 1),
        technical_accuracy=eval_result.get("technical_accuracy") or round(answer.score, 1),
        reasoning_depth=eval_result.get("reasoning_depth") or round(answer.score * 0.95, 1),
        relevance=eval_result.get("relevance") or round(answer.score * 0.98, 1),
        completeness=eval_result.get("completeness") or round(answer.score * 0.92, 1),
        communication_clarity=eval_result.get("communication_clarity") or round(answer.score * 0.96, 1),
        feedback=answer.feedback,
        keywords_detected=answer.keywords_detected or [],
        time_taken_seconds=answer.time_taken_seconds or 60,
        adapted_difficulty=new_difficulty.value if hasattr(new_difficulty, "value") else str(new_difficulty),
        upgradation_analysis=upgradation_text,
        interview_stopped=should_stop,
        stop_reason=stop_reason,
        next_question=next_question_view,
        followup_question=followup_view,
        final_report=final_report,
    )


@router.post("/{interview_id}/answer-audio", response_model=AnswerSubmitResponse)
async def submit_interview_audio_answer(
    interview_id: int,
    file: UploadFile = File(...),
    question_id: Optional[int] = Form(None),
    question_text: Optional[str] = Form(None),
    time_taken_seconds: Optional[int] = Form(60),
    generate_followup: Optional[bool] = Form(False),
    is_skipped: Optional[bool] = Form(False),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Session = Depends(get_db),
):
    """4 & 5. Receive microphone audio, store file, transcribe (STT), evaluate answer, adapt/upgrade difficulty, stop on error."""
    interview = _get_or_create_interview(db=db, interview_id=interview_id, user_id=current_user.id)

    audio_bytes = await file.read()
    stored_audio_filename = f"answer_user_{current_user.id}_interview_{interview.id}_q_{question_id or 0}_{uuid4().hex[:8]}.wav"
    stored_audio_path = AUDIO_ANSWERS_DIR / stored_audio_filename
    try:
        stored_audio_path.write_bytes(audio_bytes)
    except Exception:
        pass

    transcript = interview_ai.transcribe_audio(audio_bytes, filename=stored_audio_filename)
    if not transcript.strip():
        transcript = "Audio response provided (microphone voice input recorded)."

    submit_req = AnswerSubmitRequest(
        question_id=question_id,
        question_text=question_text,
        answer_text=transcript,
        time_taken_seconds=time_taken_seconds,
        audio_path=str(stored_audio_path),
        generate_followup=generate_followup,
        is_skipped=is_skipped,
    )
    return submit_interview_answer(
        interview_id=interview.id,
        request=submit_req,
        current_user=current_user,
        db=db,
    )


@router.post("/{interview_id}/followup", response_model=QuestionCandidateView)
def request_followup_question(
    interview_id: int,
    body: FollowupQuestionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """8. Explicitly generate a probing follow-up question based on the candidate's actual answer."""
    diff_enum = DifficultyLevel.MEDIUM
    if body.difficulty:
        from app.services.question_generator import map_difficulty
        diff_enum = map_difficulty(body.difficulty)

    followup = interview_ai.generate_followup(
        db=db,
        previous_question=body.question_text,
        candidate_answer=body.candidate_answer,
        role=body.role or "Software Engineer",
        difficulty=diff_enum,
    )
    return _build_question_view(followup, interview_id)


@router.post("/{interview_id}/complete", response_model=InterviewCompleteResponse)
def complete_interview(
    interview_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """10. Final evaluation: Generates the final report using the entire interview history with Qwen LLM."""
    interview = _get_or_create_interview(db=db, interview_id=interview_id, user_id=current_user.id)

    report = interview_ai.complete_session(db=db, interview_id=interview.id)

    return InterviewCompleteResponse(
        interview_id=interview.id,
        status=interview.status,
        overall_score=report["overall_score"],
        technical_score=report["technical_score"],
        problem_solving_score=report.get("problem_solving_score", report.get("confidence_score", 75.0)),
        communication_score=report["communication_score"],
        confidence_score=report.get("confidence_score", 75.0),
        summary=report["summary"],
        overall_performance=report.get("overall_performance"),
        technical_knowledge=report.get("technical_knowledge"),
        problem_solving=report.get("problem_solving"),
        communication=report.get("communication"),
        strong_areas=report.get("strong_areas", []),
        weak_areas=report.get("weak_areas", []),
        topics_needing_improvement=report.get("topics_needing_improvement", []),
        question_wise_performance=report.get("question_wise_performance", []),
        recommended_preparation_topics=report.get("recommended_preparation_topics", []),
        strengths=report.get("strengths", []),
        improvements=report.get("improvements", []),
        completed_at=interview.completed_at or datetime.utcnow(),
    )


@router.get("/history", response_model=List[InterviewHistoryItem])
def list_interview_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """List all interviews completed or scheduled by the user."""
    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == current_user.id)
        .order_by(Interview.created_at.desc())
        .all()
    )
    return [InterviewHistoryItem.model_validate(i) for i in interviews]


@router.get("/answers/{answer_id}/audio")

def get_candidate_answer_audio(
    answer_id: int,
    db: Session = Depends(get_db),
):
    """Download or stream recorded candidate answer audio."""
    ans = db.query(Answer).filter(Answer.id == answer_id).first()
    if not ans or not ans.audio_path:
        raise HTTPException(status_code=404, detail="Audio recording not found for this answer.")

    path = Path(ans.audio_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found on server.")

    return FileResponse(path=str(path), media_type="audio/wav")



@router.get("/{interview_id}", response_model=InterviewDetailResponse)
def get_interview_detail(
    interview_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Get full details, results, final evaluation breakdown, and answers for a specific interview session."""
    interview = _get_or_create_interview(db=db, interview_id=interview_id, user_id=current_user.id)

    result = db.query(InterviewResult).filter(InterviewResult.interview_id == interview.id).first()
    answers = db.query(Answer).filter(Answer.user_id == current_user.id).order_by(Answer.created_at.asc()).all()

    # Extract parsed fields from result strengths/improvements JSON if available
    strong_areas = []
    weak_areas = []
    topics_imp = []
    prep_topics = []
    q_performance = []
    tech_knowledge = None
    problem_solving = None
    comm_text = None

    if result:
        if isinstance(result.strengths, dict):
            strong_areas = result.strengths.get("strong_areas", [])
            tech_knowledge = result.strengths.get("technical_knowledge")
            problem_solving = result.strengths.get("problem_solving")
            comm_text = result.strengths.get("communication")
        elif isinstance(result.strengths, list):
            strong_areas = result.strengths

        if isinstance(result.improvements, dict):
            weak_areas = result.improvements.get("weak_areas", [])
            topics_imp = result.improvements.get("topics_needing_improvement", [])
            prep_topics = result.improvements.get("recommended_preparation_topics", [])
            q_performance = result.improvements.get("question_wise_performance", [])
        elif isinstance(result.improvements, list):
            weak_areas = result.improvements

    return InterviewDetailResponse(
        id=interview.id,
        user_id=interview.user_id,
        job_id=interview.job_id,
        interview_type=interview.interview_type,
        status=interview.status,
        score=interview.score,
        feedback=interview.feedback,
        created_at=interview.created_at,
        completed_at=interview.completed_at,
        overall_performance=result.summary if result else interview.feedback,
        technical_knowledge=tech_knowledge,
        problem_solving=problem_solving,
        communication=comm_text,
        strong_areas=strong_areas,
        weak_areas=weak_areas,
        topics_needing_improvement=topics_imp,
        question_wise_performance=q_performance,
        recommended_preparation_topics=prep_topics,
        result={
            "overall_score": result.overall_score,
            "technical_score": result.technical_score,
            "communication_score": result.communication_score,
            "confidence_score": result.confidence_score,
            "summary": result.summary,
            "strengths": result.strengths,
            "improvements": result.improvements,
        } if result else None,
        answers=[
            {
                "id": a.id,
                "question_id": a.question_id,
                "answer_text": a.answer_text,
                "score": a.score,
                "feedback": a.feedback,
                "keywords_detected": a.keywords_detected,
                "time_taken_seconds": a.time_taken_seconds,
            }
            for a in answers
        ],
    )


@router.post("/transcribe")
async def transcribe_candidate_speech(
    file: UploadFile = File(...),
):
    """Standalone high-precision speech-to-text endpoint powered by Whisper.
    
    Accepts recorded candidate audio (WebM, WAV, MP3, OGG) and returns the transcribed text.
    """
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="No audio data received")

    filename = file.filename or "recording.webm"
    transcript = interview_ai.transcribe_audio(audio_bytes, filename=filename)

    return {
        "status": "success",
        "transcript": transcript.strip() if transcript else "",
        "length_bytes": len(audio_bytes),
    }

