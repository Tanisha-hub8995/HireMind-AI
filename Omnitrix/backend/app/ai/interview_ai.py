from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.database.enums import DifficultyLevel
from app.models.question import Question
from app.services.interview_evaluator import InterviewEvaluator
from app.services.question_generator import QuestionGeneratorService
from app.services.speech_service import SpeechService


class InterviewAI:
    """AI orchestration layer for Interview preparation, adaptive question selection,

    follow-up questioning, speech-to-text (STT), text-to-speech (TTS), and response evaluation.
    """

    def __init__(self):
        self.question_generator = QuestionGeneratorService()
        self.evaluator = InterviewEvaluator()
        self.speech_service = SpeechService()

    def prepare_session(
        self,
        db: Session,
        user_id: int,
        role: str = "Software Engineer",
        difficulty: str = "MEDIUM",
        interview_type: str = "TECHNICAL",
        topics: Optional[List[str]] = None,
        resume_id: Optional[int] = None,
        target_company: Optional[str] = None,
        num_questions: int = 5,
    ):
        candidate_context = self.question_generator.get_candidate_context(
            db, user_id=user_id, resume_id=resume_id
        )
        questions = self.question_generator.prepare_interview_questions(
            db=db,
            user_id=user_id,
            role=role,
            difficulty=difficulty,
            interview_type=interview_type,
            topics=topics,
            candidate_context=candidate_context,
            target_company=target_company,
            num_questions=num_questions,
        )
        return {
            "candidate_context": candidate_context,
            "questions": questions,
        }

    def evaluate_response(
        self,
        question_text: str,
        answer_text: str,
        expected_section: str = "PROFESSIONAL_KNOWLEDGE",
        candidate_context: Optional[Dict] = None,
    ) -> Dict:
        return self.evaluator.evaluate_answer(
            question_text=question_text,
            answer_text=answer_text,
            expected_section=expected_section,
            candidate_context=candidate_context,
        )

    def adapt_difficulty(self, current_difficulty: DifficultyLevel, score: float) -> DifficultyLevel:
        return self.question_generator.adjust_difficulty(current_difficulty, score)

    def analyze_upgradation(
        self,
        current_difficulty: DifficultyLevel,
        score: float,
        is_skipped: bool = False,
    ) -> tuple[DifficultyLevel, bool, Optional[str], str]:
        return self.question_generator.analyze_upgradation(current_difficulty, score, is_skipped=is_skipped)

    def get_next_question(
        self,
        db: Session,
        user_id: Optional[int] = None,
        target_difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        role: str = "Software Engineer",
        topics: Optional[List[str]] = None,
        candidate_context: Optional[dict] = None,
    ) -> Question:
        return self.question_generator.get_next_adaptive_question(
            db=db,
            user_id=user_id,
            target_difficulty=target_difficulty,
            role=role,
            topics=topics,
            candidate_context=candidate_context,
        )

    def generate_followup(
        self,
        db: Session,
        previous_question: str,
        candidate_answer: str,
        role: str = "Software Engineer",
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
    ) -> Question:
        return self.question_generator.generate_followup_question(
            db=db,
            previous_question=previous_question,
            candidate_answer=candidate_answer,
            role=role,
            difficulty=difficulty,
        )

    def transcribe_audio(self, audio_bytes: bytes, filename: str = "candidate_audio.wav") -> str:
        return self.speech_service.speech_to_text(audio_bytes, filename=filename)

    def synthesize_speech(self, text: str) -> bytes:
        return self.speech_service.text_to_speech_wav(text)

    def synthesize_speech_with_mime(self, text: str):
        return self.speech_service.synthesize_speech(text)

    def complete_session(self, db: Session, interview_id: int):
        return self.evaluator.finalize_interview(db=db, interview_id=interview_id)
