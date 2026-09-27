from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.enums import (
    AssessmentSection,
    AssessmentStatus,
    QuestionStatus,
    DifficultyLevel,
    AssessmentMode,
)

from app.models.assessment import (
    Assessment,
    AssessmentAnswer,
    AssessmentResult,
    AssessmentSectionResult,
)
from app.models.question import Question

from app.schemas.assessment import (
    AssessmentInstructionsResponse,
    AssessmentInstruction,
    StartAssessmentResponse,
)


router = APIRouter(
    prefix="/assessments",
    tags=["Assessment"],
)


# ============================================================
# CONSTANTS
# ============================================================

QUESTIONS_PER_SECTION = 20
POSITIVE_MARK = 1.0
NEGATIVE_MARK = 0.25
SKIPPED_MARK = 0.0
SECTION_DURATION_MINUTES = 20

SECTION_ORDER = [
    AssessmentSection.APTITUDE,
    AssessmentSection.ENGLISH,
    AssessmentSection.DSA,
]

SECTION_DURATIONS = {
    AssessmentSection.APTITUDE: 20,
    AssessmentSection.ENGLISH: 20,
    AssessmentSection.DSA: 20,
}


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# TIME HELPERS
# ============================================================

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def get_user_assessment(
    db: Session,
    assessment_id: int,
    user_id: int,
) -> Assessment:

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id,
            Assessment.user_id == user_id,
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found.",
        )

    return assessment


def get_section_result(
    db: Session,
    assessment_id: int,
    section: AssessmentSection,
) -> AssessmentSectionResult:

    result = (
        db.query(AssessmentSectionResult)
        .filter(
            AssessmentSectionResult.assessment_id == assessment_id,
            AssessmentSectionResult.section == section,
        )
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment section not found.",
        )

    return result


def get_current_section(
    db: Session,
    assessment_id: int,
) -> AssessmentSection | None:

    section_result = (
        db.query(AssessmentSectionResult)
        .filter(
            AssessmentSectionResult.assessment_id == assessment_id,
            AssessmentSectionResult.started_at.isnot(None),
            AssessmentSectionResult.submitted_at.is_(None),
        )
        .order_by(AssessmentSectionResult.id)
        .first()
    )

    if not section_result:
        return None

    return section_result.section


def get_next_section(
    current_section: AssessmentSection,
) -> AssessmentSection | None:

    try:
        index = SECTION_ORDER.index(current_section)
    except ValueError:
        return None

    next_index = index + 1

    if next_index >= len(SECTION_ORDER):
        return None

    return SECTION_ORDER[next_index]


# ============================================================
# QUESTION HELPERS
# ============================================================

def get_section_question_count(
    db: Session,
    assessment_id: int,
    section_result_id: int,
) -> int:

    return (
        db.query(AssessmentAnswer)
        .filter(
            AssessmentAnswer.assessment_id == assessment_id,
            AssessmentAnswer.section_id == section_result_id,
        )
        .count()
    )


def get_previous_question_texts(
    db: Session,
    assessment_id: int,
    section_result_id: int,
) -> list[str]:
    """
    Return every question already generated in this assessment.

    We intentionally do NOT filter by section here. The assessment must
    not generate the same question again in another section.
    The section_result_id parameter is kept for compatibility with the
    existing callers.
    """

    rows = (
        db.query(AssessmentAnswer, Question)
        .join(
            Question,
            Question.id == AssessmentAnswer.question_id,
        )
        .filter(
            AssessmentAnswer.assessment_id == assessment_id,
        )
        .order_by(AssessmentAnswer.id)
        .all()
    )

    return [
        question.question_text
        for _, question in rows
    ]


def difficulty_to_enum(
    difficulty: str,
) -> DifficultyLevel:

    value = difficulty.lower().strip()

    mapping = {
        "easy": DifficultyLevel.EASY,
        "medium": DifficultyLevel.MEDIUM,
        "hard": DifficultyLevel.HARD,
    }

    if value not in mapping:
        raise ValueError(
            f"Invalid difficulty returned by generator: {difficulty}"
        )

    return mapping[value]


def enum_to_string(value) -> str:
    """
    Safely convert SQLAlchemy enum values to strings.
    """

    if hasattr(value, "value"):
        return value.value

    return str(value).lower()


# ============================================================
# ADAPTIVE DIFFICULTY
# ============================================================



# ============================================================
# ASSIGN EXISTING STORED QUESTIONS
# ============================================================

def assign_existing_questions_to_assessment(
    db: Session,
    assessment: Assessment,
    section_result: AssessmentSectionResult,
) -> None:
    """Assign 20 already-stored questions to an assessment section.

    This function NEVER calls Gemini/Qwen/RAG and NEVER creates a Question.
    It only creates AssessmentAnswer rows pointing at existing questions.
    """

    existing_count = (
        db.query(AssessmentAnswer)
        .filter(
            AssessmentAnswer.assessment_id == assessment.id,
            AssessmentAnswer.section_id == section_result.id,
        )
        .count()
    )

    if existing_count > 0:
        return

    questions = (
        db.query(Question)
        .filter(
            Question.section == section_result.section,
            Question.is_active.is_(True),
        )
        .order_by(func.random())
        .limit(QUESTIONS_PER_SECTION)
        .all()
    )

    if len(questions) < QUESTIONS_PER_SECTION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Not enough stored questions for "
                f"{section_result.section.value}. "
                f"Required: {QUESTIONS_PER_SECTION}, "
                f"available: {len(questions)}."
            ),
        )

    for question in questions:
        db.add(
            AssessmentAnswer(
                assessment_id=assessment.id,
                question_id=question.id,
                section_id=section_result.id,
                selected_option=None,
                status=QuestionStatus.UNSEEN,
                visited_at=None,
                answered_at=None,
                time_spent_seconds=0,
                is_correct=None,
                marks_awarded=0.0,
            )
        )

    db.flush()


def get_next_unanswered_question(
    db: Session,
    assessment_id: int,
    section_result_id: int,
):
    return (
        db.query(AssessmentAnswer)
        .filter(
            AssessmentAnswer.assessment_id == assessment_id,
            AssessmentAnswer.section_id == section_result_id,
            AssessmentAnswer.status.in_(
                [QuestionStatus.UNSEEN, QuestionStatus.VIEWED]
            ),
        )
        .order_by(AssessmentAnswer.id.asc())
        .first()
    )


def get_completed_question_count(
    db: Session,
    assessment_id: int,
    section_result_id: int,
) -> int:
    return (
        db.query(AssessmentAnswer)
        .filter(
            AssessmentAnswer.assessment_id == assessment_id,
            AssessmentAnswer.section_id == section_result_id,
            AssessmentAnswer.status.in_(
                [
                    QuestionStatus.ANSWERED,
                    QuestionStatus.SKIPPED,
                    QuestionStatus.FINALIZED,
                ]
            ),
        )
        .count()
    )

def serialize_question(
    question: Question,
    answer: AssessmentAnswer | None = None,
) -> dict:

    response = {
        "id": question.id,
        "section": enum_to_string(question.section),
        "question_text": question.question_text,
        "option_a": question.option_a,
        "option_b": question.option_b,
        "option_c": question.option_c,
        "option_d": question.option_d,
        "difficulty": enum_to_string(question.difficulty),
        "expected_time_seconds": question.expected_time_seconds,
    }

    if answer:

        response["answer_status"] = enum_to_string(
            answer.status
        )

        response["selected_option"] = (
            answer.selected_option
        )

        response["time_spent_seconds"] = (
            answer.time_spent_seconds
        )

    return response

def check_section_deadline(
    section_result: AssessmentSectionResult,
) -> bool:

    if not section_result.deadline:
        return False

    deadline = ensure_utc(section_result.deadline)

    return utc_now() >= deadline


# ============================================================
# SCORE CALCULATION
# ============================================================


def calculate_section_result(
    db: Session,
    assessment: Assessment,
    section_result: AssessmentSectionResult,
) -> AssessmentSectionResult:

    answers = (
        db.query(AssessmentAnswer, Question)
        .join(
            Question,
            Question.id == AssessmentAnswer.question_id,
        )
        .filter(
            AssessmentAnswer.assessment_id == assessment.id,
            AssessmentAnswer.section_id == section_result.id,
        )
        .all()
    )

    correct_count = 0
    wrong_count = 0
    skipped_count = 0
    attempted_count = 0

    score = 0.0
    maximum_score = 0.0

    expected_time_total = 0
    actual_time_total = 0

    difficulty_points = 0.0

    difficulty_weights = {
        DifficultyLevel.EASY: 1.0,
        DifficultyLevel.MEDIUM: 1.25,
        DifficultyLevel.HARD: 1.50,
    }

    for answer, question in answers:

        maximum_score += POSITIVE_MARK

        expected_time_total += (
            question.expected_time_seconds
        )

        actual_time_total += max(
            answer.time_spent_seconds or 0,
            0,
        )

        if answer.status == QuestionStatus.SKIPPED:

            skipped_count += 1
            answer.is_correct = None
            answer.marks_awarded = SKIPPED_MARK

        elif answer.selected_option:

            attempted_count += 1

            selected = (
                answer.selected_option
                .strip()
                .upper()
            )

            correct = (
                question.correct_option
                .strip()
                .upper()
            )

            if selected == correct:

                correct_count += 1

                answer.is_correct = True
                answer.marks_awarded = POSITIVE_MARK

                score += POSITIVE_MARK

            else:

                wrong_count += 1

                answer.is_correct = False
                answer.marks_awarded = -NEGATIVE_MARK

                score -= NEGATIVE_MARK

            difficulty_points += (
                difficulty_weights.get(
                    question.difficulty,
                    1.0,
                )
            )

        else:

            skipped_count += 1

            answer.is_correct = None
            answer.marks_awarded = SKIPPED_MARK

    percentage = 0.0

    if maximum_score > 0:

        percentage = max(
            0.0,
            (score / maximum_score) * 100,
        )

    accuracy = 0.0

    if attempted_count > 0:

        accuracy = (
            correct_count / attempted_count
        ) * 100

    time_efficiency = 0.0

    if actual_time_total > 0:

        time_efficiency = min(
            100.0,
            (
                expected_time_total
                / actual_time_total
            ) * 100,
        )

    section_result.score = score
    section_result.maximum_score = maximum_score
    section_result.percentage = percentage

    section_result.correct_count = correct_count
    section_result.wrong_count = wrong_count
    section_result.skipped_count = skipped_count
    section_result.attempted_count = attempted_count

    section_result.accuracy = accuracy
    section_result.time_efficiency = time_efficiency
    section_result.difficulty_score = difficulty_points

    return section_result


# ============================================================
# COMPLETE FINAL ASSESSMENT
# ============================================================


def complete_assessment(
    db: Session,
    assessment: Assessment,
) -> AssessmentResult:

    sections = (
        db.query(AssessmentSectionResult)
        .filter(
            AssessmentSectionResult.assessment_id
            == assessment.id
        )
        .all()
    )

    total_score = sum(
        section.score or 0.0
        for section in sections
    )

    maximum_score = sum(
        section.maximum_score or 0.0
        for section in sections
    )

    percentage = 0.0

    if maximum_score > 0:

        percentage = max(
            0.0,
            (total_score / maximum_score) * 100,
        )

    assessment.total_score = total_score
    assessment.maximum_score = maximum_score
    assessment.percentage = percentage

    assessment.status = AssessmentStatus.COMPLETED
    assessment.completed_at = utc_now()

    result = (
        db.query(AssessmentResult)
        .filter(
            AssessmentResult.assessment_id
            == assessment.id
        )
        .first()
    )

    if result:

        result.total_score = total_score
        result.maximum_score = maximum_score
        result.percentage = percentage

    else:

        result = AssessmentResult(
            assessment_id=assessment.id,
            user_id=assessment.user_id,
            total_score=total_score,
            maximum_score=maximum_score,
            percentage=percentage,
        )

        db.add(result)

    db.commit()
    db.refresh(result)

    return result


# ============================================================
# SUBMIT CURRENT SECTION
# ============================================================



# ============================================================
# SUBMIT CURRENT SECTION
# ============================================================

def submit_current_section(
    db: Session,
    assessment: Assessment,
    section_result: AssessmentSectionResult,
) -> dict:
    """Evaluate and close the current section.

    FULL assessment:
        APTITUDE -> ENGLISH -> DSA -> COMPLETED

    Individual assessment:
        APTITUDE/ENGLISH/DSA -> COMPLETED
    """

    # --------------------------------------------------------
    # Already submitted
    # --------------------------------------------------------

    if section_result.submitted_at:

        # Individual assessment has no next section.
        if assessment.assessment_mode != AssessmentMode.FULL:

            result = (
                db.query(AssessmentResult)
                .filter(
                    AssessmentResult.assessment_id
                    == assessment.id
                )
                .first()
            )

            return {
                "section": section_result.section.value,
                "score": section_result.score,
                "maximum_score": section_result.maximum_score,
                "percentage": section_result.percentage,
                "correct_count": section_result.correct_count,
                "wrong_count": section_result.wrong_count,
                "skipped_count": section_result.skipped_count,
                "attempted_count": section_result.attempted_count,
                "started_at": section_result.started_at,
                "submitted_at": section_result.submitted_at,
                "next_section": None,
                "assessment_completed": True,
                "assessment_started_at": assessment.started_at,
                "assessment_completed_at": assessment.completed_at,
                "total_score": (
                    result.total_score if result else None
                ),
                "total_maximum_score": (
                    result.maximum_score if result else None
                ),
                "total_percentage": (
                    result.percentage if result else None
                ),
            }

        # FULL assessment
        next_section = get_next_section(
            section_result.section
        )

        return {
            "section": section_result.section.value,
            "score": section_result.score,
            "maximum_score": section_result.maximum_score,
            "percentage": section_result.percentage,
            "correct_count": section_result.correct_count,
            "wrong_count": section_result.wrong_count,
            "skipped_count": section_result.skipped_count,
            "attempted_count": section_result.attempted_count,
            "started_at": section_result.started_at,
            "submitted_at": section_result.submitted_at,
            "next_section": (
                next_section.value
                if next_section
                else None
            ),
            "assessment_completed": (
                next_section is None
            ),
        }

    # --------------------------------------------------------
    # Mark unanswered questions as skipped
    # --------------------------------------------------------

    unanswered = (
        db.query(AssessmentAnswer)
        .filter(
            AssessmentAnswer.assessment_id
            == assessment.id,

            AssessmentAnswer.section_id
            == section_result.id,

            AssessmentAnswer.status.in_(
                [
                    QuestionStatus.UNSEEN,
                    QuestionStatus.VIEWED,
                ]
            ),
        )
        .all()
    )

    now = utc_now()

    for answer in unanswered:

        answer.status = QuestionStatus.SKIPPED
        answer.is_correct = None
        answer.marks_awarded = SKIPPED_MARK

        if answer.visited_at:

            visited = ensure_utc(
                answer.visited_at
            )

            answer.time_spent_seconds = max(
                0,
                int(
                    (
                        now - visited
                    ).total_seconds()
                ),
            )

    # --------------------------------------------------------
    # Close current section
    # --------------------------------------------------------

    section_result.submitted_at = now

    calculate_section_result(
        db=db,
        assessment=assessment,
        section_result=section_result,
    )

    db.flush()

    # ========================================================
    # INDIVIDUAL ASSESSMENT
    # ========================================================

    if assessment.assessment_mode != AssessmentMode.FULL:

        result = complete_assessment(
            db=db,
            assessment=assessment,
        )

        return {
            "section": section_result.section.value,
            "score": section_result.score,
            "maximum_score": section_result.maximum_score,
            "percentage": section_result.percentage,
            "correct_count": section_result.correct_count,
            "wrong_count": section_result.wrong_count,
            "skipped_count": section_result.skipped_count,
            "attempted_count": section_result.attempted_count,
            "started_at": section_result.started_at,
            "submitted_at": section_result.submitted_at,

            "next_section": None,

            "assessment_completed": True,

            "assessment_started_at":
                assessment.started_at,

            "assessment_completed_at":
                assessment.completed_at,

            "total_score":
                result.total_score,

            "total_maximum_score":
                result.maximum_score,

            "total_percentage":
                result.percentage,
        }

    # ========================================================
    # FULL ASSESSMENT
    # ========================================================

    next_section = get_next_section(
        section_result.section
    )

    # --------------------------------------------------------
    # Last FULL section: DSA
    # --------------------------------------------------------

    if next_section is None:

        result = complete_assessment(
            db=db,
            assessment=assessment,
        )

        return {
            "section": section_result.section.value,
            "score": section_result.score,
            "maximum_score": section_result.maximum_score,
            "percentage": section_result.percentage,
            "correct_count": section_result.correct_count,
            "wrong_count": section_result.wrong_count,
            "skipped_count": section_result.skipped_count,
            "attempted_count": section_result.attempted_count,
            "started_at": section_result.started_at,
            "submitted_at": section_result.submitted_at,

            "next_section": None,

            "assessment_completed": True,

            "assessment_started_at":
                assessment.started_at,

            "assessment_completed_at":
                assessment.completed_at,

            "total_score":
                result.total_score,

            "total_maximum_score":
                result.maximum_score,

            "total_percentage":
                result.percentage,
        }

    # --------------------------------------------------------
    # Move FULL assessment to next section
    # --------------------------------------------------------

    next_result = get_section_result(
        db=db,
        assessment_id=assessment.id,
        section=next_section,
    )

    next_now = utc_now()

    next_result.started_at = next_now

    next_result.deadline = (
        next_now
        + timedelta(
            minutes=SECTION_DURATIONS[next_section]
        )
    )

    next_result.submitted_at = None

    assessment.status = (
        AssessmentStatus.IN_PROGRESS
    )

    db.commit()

    # --------------------------------------------------------
    # Get first question of next section
    # --------------------------------------------------------

    next_answer = get_next_unanswered_question(
        db=db,
        assessment_id=assessment.id,
        section_result_id=next_result.id,
    )

    next_question = None

    if next_answer:

        next_question = (
            db.query(Question)
            .filter(
                Question.id
                == next_answer.question_id
            )
            .first()
        )

    return {
        "section": section_result.section.value,
        "score": section_result.score,
        "maximum_score": section_result.maximum_score,
        "percentage": section_result.percentage,
        "correct_count": section_result.correct_count,
        "wrong_count": section_result.wrong_count,
        "skipped_count": section_result.skipped_count,
        "attempted_count": section_result.attempted_count,
        "started_at": section_result.started_at,
        "submitted_at": section_result.submitted_at,

        "next_section": next_section.value,

        "next_section_started_at":
            next_result.started_at,

        "next_deadline":
            next_result.deadline,

        "assessment_completed": False,

        "next_question": (
            serialize_question(
                next_question,
                next_answer,
            )
            if next_question and next_answer
            else None
        ),
    }

@router.get(
    "/instructions",
    response_model=AssessmentInstructionsResponse,
)
def get_assessment_instructions():

    sections = []

    for section in SECTION_ORDER:

        sections.append(
            AssessmentInstruction(
                section=section.value,
                duration_minutes=SECTION_DURATIONS[section],
                number_of_questions=QUESTIONS_PER_SECTION,
                positive_mark=POSITIVE_MARK,
                negative_mark=NEGATIVE_MARK,
                skipped_mark=SKIPPED_MARK,
            )
        )

    return AssessmentInstructionsResponse(
        total_duration_minutes=(
            SECTION_DURATION_MINUTES
            * len(SECTION_ORDER)
        ),
        sections=sections,
    )


# ============================================================
# START ASSESSMENT
# ============================================================



# ============================================================
# START ASSESSMENT
# ============================================================

@router.post("/start", response_model=StartAssessmentResponse)
def start_assessment(
    user_id: int,
    assessment_mode: AssessmentMode = AssessmentMode.FULL,
    db: Session = Depends(get_db),
):
    """Start/resume an assessment using only stored questions."""

    existing = (
        db.query(Assessment)
        .filter(
            Assessment.user_id == user_id,
            Assessment.status == AssessmentStatus.IN_PROGRESS,
        )
        .order_by(Assessment.id.desc())
        .first()
    )

    if existing:
        current_section = get_current_section(
            db=db,
            assessment_id=existing.id,
        )

        if current_section:
            section_result = get_section_result(
                db=db,
                assessment_id=existing.id,
                section=current_section,
            )

            if check_section_deadline(section_result):
                submit_current_section(
                    db=db,
                    assessment=existing,
                    section_result=section_result,
                )
                db.refresh(existing)

        return StartAssessmentResponse(
            assessment_id=existing.id,
            status=existing.status,
            started_at=existing.started_at,
        )

    if assessment_mode == AssessmentMode.FULL:
        sections = list(SECTION_ORDER)
    elif assessment_mode in {
        AssessmentMode.APTITUDE,
        AssessmentMode.ENGLISH,
        AssessmentMode.DSA,
    }:
        sections = [AssessmentSection(assessment_mode.value)]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assessment mode.",
        )

    now = utc_now()

    assessment = Assessment(
        user_id=user_id,
        status=AssessmentStatus.IN_PROGRESS,
        started_at=now,
        total_score=0.0,
        maximum_score=0.0,
        percentage=0.0,
        assessment_mode=assessment_mode,
    )

    db.add(assessment)
    db.flush()

    section_results = {}

    # Create the section records and assign all questions NOW.
    # No question is generated during the actual attempt.
    for section in sections:
        section_result = AssessmentSectionResult(
            assessment_id=assessment.id,
            section=section,
            started_at=None,
            deadline=None,
            submitted_at=None,
            score=0.0,
            maximum_score=0.0,
            percentage=0.0,
            correct_count=0,
            wrong_count=0,
            skipped_count=0,
            attempted_count=0,
            accuracy=0.0,
            time_efficiency=0.0,
            difficulty_score=0.0,
        )
        db.add(section_result)
        db.flush()
        section_results[section] = section_result

    first_section = sections[0]
    first_result = section_results[first_section]

    first_result.started_at = now
    first_result.deadline = now + timedelta(
        minutes=SECTION_DURATIONS[first_section]
    )

    for section in sections:
        assign_existing_questions_to_assessment(
            db=db,
            assessment=assessment,
            section_result=section_results[section],
        )

    db.commit()

    return StartAssessmentResponse(
        assessment_id=assessment.id,
        status=assessment.status,
        started_at=assessment.started_at,
    )


# ============================================================
# GET CURRENT QUESTION
# ============================================================

@router.get("/{assessment_id}/questions")
def get_current_question(
    assessment_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    assessment = get_user_assessment(
        db=db,
        assessment_id=assessment_id,
        user_id=user_id,
    )

    if assessment.status != AssessmentStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Assessment is not in progress.",
        )

    current_section = get_current_section(
        db=db,
        assessment_id=assessment.id,
    )

    if current_section is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is no active assessment section.",
        )

    section_result = get_section_result(
        db=db,
        assessment_id=assessment.id,
        section=current_section,
    )

    if check_section_deadline(section_result):
        result = submit_current_section(
            db=db,
            assessment=assessment,
            section_result=section_result,
        )
        return {"timer_expired": True, **result}

    answer = get_next_unanswered_question(
        db=db,
        assessment_id=assessment.id,
        section_result_id=section_result.id,
    )

    completed_count = get_completed_question_count(
        db=db,
        assessment_id=assessment.id,
        section_result_id=section_result.id,
    )

    if not answer:
        return {
            "assessment_id": assessment.id,
            "section": current_section.value,
            "deadline": section_result.deadline,
            "section_started_at": section_result.started_at,
            "questions_completed": completed_count,
            "max_questions": QUESTIONS_PER_SECTION,
            "question": None,
            "waiting_for_timer": completed_count >= QUESTIONS_PER_SECTION,
        }

    question = (
        db.query(Question)
        .filter(Question.id == answer.question_id)
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question assigned to this assessment was not found.",
        )

    if answer.status == QuestionStatus.UNSEEN:
        answer.status = QuestionStatus.VIEWED
        answer.visited_at = utc_now()
        db.commit()

    return {
        "assessment_id": assessment.id,
        "section": current_section.value,
        "deadline": section_result.deadline,
        "section_started_at": section_result.started_at,
        "questions_completed": completed_count,
        "max_questions": QUESTIONS_PER_SECTION,
        "question": serialize_question(question, answer),
    }


# ============================================================
# ANSWER CURRENT QUESTION
# ============================================================

@router.put("/{assessment_id}/questions/{question_id}/answer")
def answer_question(
    assessment_id: int,
    question_id: int,
    user_id: int,
    selected_option: str | None = None,
    time_spent_seconds: int = 0,
    db: Session = Depends(get_db),
):
    assessment = get_user_assessment(
        db=db,
        assessment_id=assessment_id,
        user_id=user_id,
    )

    if assessment.status != AssessmentStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Assessment is not in progress.",
        )

    current_section = get_current_section(
        db=db,
        assessment_id=assessment.id,
    )

    if current_section is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No active section.",
        )

    section_result = get_section_result(
        db=db,
        assessment_id=assessment.id,
        section=current_section,
    )

    if check_section_deadline(section_result):
        result = submit_current_section(
            db=db,
            assessment=assessment,
            section_result=section_result,
        )
        return {"timer_expired": True, **result}

    question = (
        db.query(Question)
        .filter(
            Question.id == question_id,
            Question.section == current_section,
        )
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found.",
        )

    answer = (
        db.query(AssessmentAnswer)
        .filter(
            AssessmentAnswer.assessment_id == assessment.id,
            AssessmentAnswer.question_id == question.id,
            AssessmentAnswer.section_id == section_result.id,
            AssessmentAnswer.status.in_(
                [QuestionStatus.UNSEEN, QuestionStatus.VIEWED]
            ),
        )
        .first()
    )

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Question is not active or has already been completed.",
        )

    if selected_option is not None:
        selected_option = selected_option.strip().upper()
        if selected_option not in {"A", "B", "C", "D"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="selected_option must be A, B, C, D, or null.",
            )

    time_spent_seconds = max(0, int(time_spent_seconds or 0))
    answer.time_spent_seconds = time_spent_seconds
    answer.answered_at = utc_now()

    if selected_option is None:
        answer.selected_option = None
        answer.status = QuestionStatus.SKIPPED
        answer.is_correct = None
        answer.marks_awarded = SKIPPED_MARK
    else:
        answer.selected_option = selected_option
        answer.status = QuestionStatus.ANSWERED

        correct_option = question.correct_option.strip().upper()

        if selected_option == correct_option:
            answer.is_correct = True
            answer.marks_awarded = POSITIVE_MARK
        else:
            answer.is_correct = False
            answer.marks_awarded = -NEGATIVE_MARK

    db.commit()

    completed_count = get_completed_question_count(
        db=db,
        assessment_id=assessment.id,
        section_result_id=section_result.id,
    )

    if completed_count >= QUESTIONS_PER_SECTION:
        return {
            "question_completed": True,
            "section_completed": False,
            "waiting_for_timer": True,
            "completed_questions": completed_count,
            "current_section": current_section.value,
            "deadline": section_result.deadline,
            "message": (
                "All 20 questions have been completed. "
                "The section will end when the 20-minute timer expires."
            ),
        }

    next_answer = (
        db.query(AssessmentAnswer)
        .filter(
            AssessmentAnswer.assessment_id == assessment.id,
            AssessmentAnswer.section_id == section_result.id,
            AssessmentAnswer.status == QuestionStatus.UNSEEN,
        )
        .order_by(AssessmentAnswer.id.asc())
        .first()
    )

    if not next_answer:
        return {
            "question_completed": True,
            "section_completed": False,
            "completed_questions": completed_count,
            "current_section": current_section.value,
            "next_question": None,
            "deadline": section_result.deadline,
        }

    next_question = (
        db.query(Question)
        .filter(Question.id == next_answer.question_id)
        .first()
    )

    if not next_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Next stored question was not found.",
        )

    return {
        "question_completed": True,
        "section_completed": False,
        "completed_questions": completed_count,
        "current_section": current_section.value,
        "next_question": serialize_question(next_question, next_answer),
        "deadline": section_result.deadline,
    }


# ============================================================
# SUBMIT SECTION
# ============================================================

@router.post("/{assessment_id}/submit-section")
def submit_section(
    assessment_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    assessment = get_user_assessment(
        db=db,
        assessment_id=assessment_id,
        user_id=user_id,
    )

    if assessment.status != AssessmentStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Assessment is not in progress.",
        )

    current_section = get_current_section(
        db=db,
        assessment_id=assessment.id,
    )

    if current_section is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No active section.",
        )

    section_result = get_section_result(
        db=db,
        assessment_id=assessment.id,
        section=current_section,
    )

    # Individual assessment: early submission is allowed.
    if assessment.assessment_mode != AssessmentMode.FULL:
        return submit_current_section(
            db=db,
            assessment=assessment,
            section_result=section_result,
        )

    # FULL assessment: section submission is allowed only after
    # the 20-minute timer expires.
    if not check_section_deadline(section_result):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "For the full assessment, the section cannot be "
                "submitted before the 20-minute timer expires."
            ),
        )

    return submit_current_section(
        db=db,
        assessment=assessment,
        section_result=section_result,
    )

@router.get(
    "/{assessment_id}/sections/{section}/result",
)
def get_section_result_endpoint(
    assessment_id: int,
    section: AssessmentSection,
    user_id: int,
    db: Session = Depends(get_db),
):

    assessment = get_user_assessment(
        db=db,
        assessment_id=assessment_id,
        user_id=user_id,
    )

    result = get_section_result(
        db=db,
        assessment_id=assessment.id,
        section=section,
    )

    if not result.submitted_at:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This section has not been completed yet.",
        )

    return {
        "assessment_id": assessment.id,
        "section": result.section.value,
        "started_at": result.started_at,
        "deadline": result.deadline,
        "submitted_at": result.submitted_at,
        "score": result.score,
        "maximum_score": result.maximum_score,
        "percentage": result.percentage,
        "correct_count": result.correct_count,
        "wrong_count": result.wrong_count,
        "skipped_count": result.skipped_count,
        "attempted_count": result.attempted_count,
        "accuracy": result.accuracy,
        "time_efficiency": result.time_efficiency,
        "difficulty_score": result.difficulty_score,
    }


# ============================================================
# FINALIZE ASSESSMENT
# ============================================================


@router.post(
    "/{assessment_id}/finalize",
)
def finalize_assessment(
    assessment_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):

    assessment = get_user_assessment(
        db=db,
        assessment_id=assessment_id,
        user_id=user_id,
    )

    if assessment.status == AssessmentStatus.COMPLETED:

        result = (
            db.query(AssessmentResult)
            .filter(
                AssessmentResult.assessment_id
                == assessment.id
            )
            .first()
        )

        if result:

            return {
                "assessment_id": assessment.id,
                "status": assessment.status.value,
                "total_score": result.total_score,
                "maximum_score": result.maximum_score,
                "percentage": result.percentage,
            }

    current_section = get_current_section(
        db=db,
        assessment_id=assessment.id,
    )

    if current_section:

        section_result = get_section_result(
            db=db,
            assessment_id=assessment.id,
            section=current_section,
        )

        if not check_section_deadline(section_result):

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "The assessment cannot be finalized "
                    "before the current section ends."
                ),
            )

        submit_current_section(
            db=db,
            assessment=assessment,
            section_result=section_result,
        )

        db.refresh(assessment)

    if assessment.status != AssessmentStatus.COMPLETED:

        sections = (
            db.query(AssessmentSectionResult)
            .filter(
                AssessmentSectionResult.assessment_id
                == assessment.id
            )
            .all()
        )

        all_completed = all(
            section.submitted_at is not None
            for section in sections
        )

        if all_completed:

            complete_assessment(
                db=db,
                assessment=assessment,
            )

    result = (
        db.query(AssessmentResult)
        .filter(
            AssessmentResult.assessment_id
            == assessment.id
        )
        .first()
    )

    if not result:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Final assessment result could not "
                "be generated."
            ),
        )

    return {
        "assessment_id": assessment.id,
        "status": assessment.status.value,
        "total_score": result.total_score,
        "maximum_score": result.maximum_score,
        "percentage": result.percentage,
    }


# ============================================================
# FINAL RESULT
# ============================================================


@router.get(
    "/{assessment_id}/result",
)
def get_final_result(
    assessment_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):

    assessment = get_user_assessment(
        db=db,
        assessment_id=assessment_id,
        user_id=user_id,
    )

    if assessment.status != AssessmentStatus.COMPLETED:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Assessment has not been completed yet.",
        )

    result = (
        db.query(AssessmentResult)
        .filter(
            AssessmentResult.assessment_id
            == assessment.id
        )
        .first()
    )

    if not result:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Final result not found.",
        )

    sections = (
        db.query(AssessmentSectionResult)
        .filter(
            AssessmentSectionResult.assessment_id
            == assessment.id
        )
        .order_by(AssessmentSectionResult.id)
        .all()
    )

    return {
        "assessment_id": assessment.id,
        "user_id": assessment.user_id,
        "status": assessment.status.value,
        "started_at": assessment.started_at,
        "completed_at": assessment.completed_at,
        "total_score": result.total_score,
        "maximum_score": result.maximum_score,
        "percentage": result.percentage,
        "sections": [
            {
                "section": section.section.value,
                "score": section.score,
                "maximum_score": section.maximum_score,
                "percentage": section.percentage,
                "correct_count": section.correct_count,
                "wrong_count": section.wrong_count,
                "skipped_count": section.skipped_count,
                "attempted_count": section.attempted_count,
                "accuracy": section.accuracy,
                "time_efficiency": section.time_efficiency,
                "difficulty_score": section.difficulty_score,
            }
            for section in sections
        ],
    }