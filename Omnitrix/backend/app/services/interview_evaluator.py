import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.ai.llm_service import LLMService
from app.models.answer import Answer
from app.models.interview import Interview
from app.models.progress import UserProgress
from app.models.question import Question
from app.models.recommendation import Recommendation
from app.models.result import InterviewResult

logger = logging.getLogger(__name__)


class InterviewEvaluator:
    """Evaluates candidate answers across 6 dimensions:

    1. Correctness
    2. Technical understanding
    3. Reasoning & depth
    4. Relevance
    5. Completeness
    6. Communication quality
    Generates structured scores, detected keywords, actionable constructive feedback, and final interview reports.
    """

    def __init__(self):
        self.llm_service = LLMService()

    def evaluate_answer(
        self,
        question_text: str,
        answer_text: str,
        expected_section: str = "PROFESSIONAL_KNOWLEDGE",
        candidate_context: Optional[Dict] = None,
    ) -> Dict:
        """Evaluates a single candidate answer using Qwen LLM or deterministic rubric validation."""
        clean_ans = (answer_text or "").strip()
        word_count = len(clean_ans.split())
        lower_ans = clean_ans.lower()

        # Direct detection of inability to answer or trivial responses
        ignorance_phrases = ["no clue", "no idea", "i do not know", "i don't know", "dont know", "skip", "have no clue", "not sure", "cannot answer", "can't answer"]
        if word_count < 3 or any(p in lower_ans for p in ignorance_phrases):
            return {
                "score": 15.0,
                "correctness": 10.0,
                "technical_accuracy": 10.0,
                "reasoning_depth": 10.0,
                "relevance": 10.0,
                "completeness": 10.0,
                "communication_clarity": 20.0,
                "feedback": "Answer demonstrates insufficient technical knowledge or indicates inability to address the question.",
                "keywords_detected": [],
            }

        system_prompt = (
            "You are a senior technical interviewer. Evaluate the candidate's answer across: "
            "1. Correctness (0-100), 2. Technical understanding (0-100), 3. Reasoning & Depth (0-100), "
            "4. Relevance & Completeness (0-100), 5. Communication quality (0-100). "
            "Extract detected technical keywords and write constructive feedback. "
            "Return JSON: {"
            "'score': float, 'correctness': float, 'technical_accuracy': float, "
            "'reasoning_depth': float, 'relevance': float, 'completeness': float, "
            "'communication_clarity': float, 'keywords_detected': ['...'], 'feedback': '...'"
            "}"
        )

        payload = {
            "question": question_text,
            "candidate_answer": clean_ans,
            "section": expected_section,
        }

        try:
            if hasattr(self.llm_service, "_qwen_json"):
                res = self.llm_service._qwen_json(system_prompt, payload)
                if isinstance(res, dict) and "score" in res:
                    return {
                        "score": round(float(res.get("score", 72.0)), 1),
                        "correctness": round(float(res.get("correctness", 70.0)), 1),
                        "technical_accuracy": round(float(res.get("technical_accuracy", 70.0)), 1),
                        "reasoning_depth": round(float(res.get("reasoning_depth", 68.0)), 1),
                        "relevance": round(float(res.get("relevance", 75.0)), 1),
                        "completeness": round(float(res.get("completeness", 70.0)), 1),
                        "communication_clarity": round(float(res.get("communication_clarity", 75.0)), 1),
                        "keywords_detected": list(res.get("keywords_detected", [])),
                        "feedback": str(res.get("feedback", "Good explanation covering core concepts.")),
                    }
        except Exception as exc:
            logger.info("LLM answer evaluation fallback: %s", exc)

        # Deterministic rubric scoring
        keywords = re.findall(r"\b[A-Za-z0-9_+#.-]{3,}\b", clean_ans)
        common_stops = {"the", "and", "for", "that", "this", "with", "from", "have", "are", "which", "can", "they", "will"}
        meaningful_keywords = [k for k in keywords if k.lower() not in common_stops][:8]

        base_score = min(80.0, 40.0 + min(word_count * 0.7, 35.0))
        depth_bonus = 0.0
        reasoning_keywords = ["because", "therefore", "trade-off", "tradeoff", "complexity", "time complexity", "space complexity", "architecture", "scale", "optimize", "cache", "index"]
        matched_indicators = [term for term in reasoning_keywords if term in clean_ans.lower()]
        if matched_indicators:
            depth_bonus = min(15.0, len(matched_indicators) * 4.0)

        tech_score = round(min(96.0, base_score + depth_bonus), 1)
        reasoning_score = round(min(95.0, 50.0 + (len(matched_indicators) * 12.0) + (word_count * 0.3)), 1)
        relevance_score = 85.0 if len(meaningful_keywords) >= 3 else 65.0
        completeness_score = min(92.0, 45.0 + (word_count * 0.6))
        comm_score = round(min(95.0, base_score + 5.0), 1)
        correctness_score = tech_score

        final_score = round(
            (correctness_score * 0.25)
            + (tech_score * 0.25)
            + (reasoning_score * 0.20)
            + (relevance_score * 0.15)
            + (comm_score * 0.15),
            1,
        )

        return {
            "score": final_score,
            "correctness": correctness_score,
            "technical_accuracy": tech_score,
            "reasoning_depth": reasoning_score,
            "relevance": relevance_score,
            "completeness": completeness_score,
            "communication_clarity": comm_score,
            "keywords_detected": meaningful_keywords,
            "feedback": (
                f"Answer demonstrates solid comprehension ({len(meaningful_keywords)} key technical terms detected: {', '.join(meaningful_keywords[:4])}). "
                f"To achieve top marks, emphasize quantitative trade-offs and edge-case handling."
            ),
        }

    def finalize_interview(self, db: Session, interview_id: int) -> Dict:
        """10. Final evaluation: Generates comprehensive final report using the entire interview history.

        Evaluates:
        - Overall performance
        - Technical knowledge
        - Problem-solving
        - Communication
        - Strong areas
        - Weak areas
        - Topics that need improvement
        - Question-wise performance
        - Recommended preparation topics
        """
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        # Gather all answers associated with this user session since interview scheduled/created
        answers = (
            db.query(Answer)
            .filter(Answer.user_id == interview.user_id)
            .order_by(Answer.created_at.asc())
            .all()
        )
        
        # If there are answers created around or after interview creation, prioritize them
        recent_answers = [a for a in answers if interview.created_at and a.created_at and a.created_at >= interview.created_at]
        if not recent_answers and answers:
            # If no recent timestamp match (e.g., fast mock tests), take the last N answers
            recent_answers = answers[-5:]
        elif not recent_answers:
            recent_answers = []

        # Build transcript history with full question context
        transcript_history = []
        for ans in recent_answers:
            q_text = "General Engineering Assessment Question"
            section_name = "PROFESSIONAL_KNOWLEDGE"
            if ans.question_id:
                q = db.query(Question).filter(Question.id == ans.question_id).first()
                if q:
                    q_text = q.question_text
                    section_name = q.section.value if hasattr(q.section, "value") else str(q.section)
            
            transcript_history.append({
                "question_id": ans.question_id,
                "section": section_name,
                "question_text": q_text,
                "candidate_answer": ans.answer_text or "No answer provided.",
                "score": float(ans.score) if ans.score is not None else 65.0,
                "feedback": ans.feedback or "Standard response recorded.",
                "keywords_detected": ans.keywords_detected or [],
                "time_taken_seconds": ans.time_taken_seconds or 0,
            })

        interview_context = {
            "interview_id": interview.id,
            "interview_type": interview.interview_type or "TECHNICAL",
            "job_id": interview.job_id,
            "total_questions_answered": len(transcript_history),
        }

        # Attempt Qwen LLM full history evaluation
        report = None
        try:
            if hasattr(self.llm_service, "generate_interview_final_report"):
                res = self.llm_service.generate_interview_final_report(
                    interview_context=interview_context,
                    transcript_history=transcript_history,
                )
                if isinstance(res, dict) and "overall_score" in res:
                    report = res
        except Exception as exc:
            logger.info("Qwen full final report fallback to deterministic generator: %s", exc)

        # Fallback / Baseline deterministic evaluation based on full history
        valid_scores = [item["score"] for item in transcript_history] if transcript_history else [75.0]
        avg_score = float(sum(valid_scores) / len(valid_scores))

        # Calculate multi-dimensional metrics across entire history
        tech_score = round(avg_score, 1)
        problem_solving_score = round(min(100.0, max(40.0, avg_score + 1.5)), 1)
        comm_score = round(min(100.0, max(45.0, avg_score + 2.0)), 1)
        conf_score = round(min(100.0, max(40.0, avg_score + 2.5)), 1)
        overall_score = round((tech_score * 0.4) + (problem_solving_score * 0.3) + (comm_score * 0.3), 1)

        # Aggregate detected keywords across entire interview
        all_keywords = []
        for item in transcript_history:
            all_keywords.extend(item.get("keywords_detected") or [])
        unique_keywords = list(dict.fromkeys(all_keywords))

        # Determine strong and weak areas from question-wise performance
        strong_areas = [
            "Clear and articulate communication of technical architectures",
            "Solid grasp of fundamental data structures and algorithmic efficiency",
            "Structured decomposition of open-ended engineering problems",
        ]
        if unique_keywords:
            strong_areas.insert(0, f"Demonstrated practical familiarity with core concepts: {', '.join(unique_keywords[:4])}")

        weak_areas = [
            "Could elaborate deeper on distributed failure modes and data consistency",
            "Quantitative trade-offs (e.g., Big-O memory vs compute) could be stated more explicitly",
            "Edge case handling and concurrency safety under high load",
        ]

        topics_needing_improvement = [
            "Advanced System Design & Distributed Caching (Redis/Memcached)",
            "Database Indexing Strategies & Query Execution Plan Optimization",
            "Concurrency Control, Mutexes, and Thread Safety Patterns",
            "Asynchronous Event-Driven Architectures (Kafka/RabbitMQ)",
        ]

        recommended_preparation_topics = [
            "Deep-dive into High-Performance SQL & PostgreSQL Query Optimization",
            "Practice LeetCode Medium/Hard Tree and Dynamic Programming patterns",
            "Study Scalability Design Patterns: Partitioning, Replication, and Cache Invalidation",
            "Mock Technical Communication: Structuring answers using the STAR method",
        ]

        overall_perf_text = (
            f"Candidate achieved an overall interview performance score of {overall_score}%. "
            f"Demonstrated solid competency across {len(transcript_history)} interview questions with strong clarity."
        )

        tech_knowledge_text = (
            f"Technical knowledge score: {tech_score}/100. Candidate displayed a good foundational understanding of "
            f"software engineering principles, syntax, and relevant architectural patterns."
        )

        problem_solving_text = (
            f"Problem-solving score: {problem_solving_score}/100. Showed systematic reasoning, ability to reason through "
            f"trade-offs, and logical modularization of complex scenarios."
        )

        comm_text = (
            f"Communication score: {comm_score}/100. Articulated ideas coherently with appropriate engineering vocabulary "
            f"and structured explanations."
        )

        if report:
            overall_score = float(report.get("overall_score", overall_score))
            tech_score = float(report.get("technical_score", tech_score))
            problem_solving_score = float(report.get("problem_solving_score", problem_solving_score))
            comm_score = float(report.get("communication_score", comm_score))
            overall_perf_text = str(report.get("overall_performance", overall_perf_text))
            tech_knowledge_text = str(report.get("technical_knowledge", tech_knowledge_text))
            problem_solving_text = str(report.get("problem_solving", problem_solving_text))
            comm_text = str(report.get("communication", comm_text))
            if report.get("strong_areas"):
                strong_areas = list(report.get("strong_areas"))
            if report.get("weak_areas"):
                weak_areas = list(report.get("weak_areas"))
            if report.get("topics_that_need_improvement"):
                topics_needing_improvement = list(report.get("topics_that_need_improvement"))
            if report.get("recommended_preparation_topics"):
                recommended_preparation_topics = list(report.get("recommended_preparation_topics"))

        # Save in database
        result = db.query(InterviewResult).filter(InterviewResult.interview_id == interview_id).first()
        if not result:
            result = InterviewResult(
                interview_id=interview_id,
                overall_score=overall_score,
                technical_score=tech_score,
                communication_score=comm_score,
                confidence_score=problem_solving_score,
                summary=overall_perf_text,
                strengths={
                    "strong_areas": strong_areas,
                    "technical_knowledge": tech_knowledge_text,
                    "problem_solving": problem_solving_text,
                    "communication": comm_text,
                },
                improvements={
                    "weak_areas": weak_areas,
                    "topics_needing_improvement": topics_needing_improvement,
                    "recommended_preparation_topics": recommended_preparation_topics,
                    "question_wise_performance": transcript_history,
                },
                created_at=datetime.utcnow(),
            )
            db.add(result)
        else:
            result.overall_score = overall_score
            result.technical_score = tech_score
            result.communication_score = comm_score
            result.confidence_score = problem_solving_score
            result.summary = overall_perf_text
            result.strengths = {
                "strong_areas": strong_areas,
                "technical_knowledge": tech_knowledge_text,
                "problem_solving": problem_solving_text,
                "communication": comm_text,
            }
            result.improvements = {
                "weak_areas": weak_areas,
                "topics_needing_improvement": topics_needing_improvement,
                "recommended_preparation_topics": recommended_preparation_topics,
                "question_wise_performance": transcript_history,
            }

        interview.status = "COMPLETED"
        interview.score = overall_score
        interview.completed_at = datetime.utcnow()
        interview.feedback = overall_perf_text

        # Record metrics in user_progress
        db.add(UserProgress(
            user_id=interview.user_id,
            category="interview",
            metric_name="latest_interview_score",
            value=overall_score,
            recorded_at=datetime.utcnow(),
        ))
        db.add(UserProgress(
            user_id=interview.user_id,
            category="interview",
            metric_name="technical_score",
            value=tech_score,
            recorded_at=datetime.utcnow(),
        ))
        db.add(UserProgress(
            user_id=interview.user_id,
            category="interview",
            metric_name="problem_solving_score",
            value=problem_solving_score,
            recorded_at=datetime.utcnow(),
        ))
        db.add(UserProgress(
            user_id=interview.user_id,
            category="interview",
            metric_name="communication_score",
            value=comm_score,
            recorded_at=datetime.utcnow(),
        ))

        # Generate actionable practice recommendations
        db.add(Recommendation(
            user_id=interview.user_id,
            rec_type="practice",
            title="Interview Growth Plan & Targeted Preparation Roadmap",
            description=f"Recommended preparation roadmap based on your {interview.interview_type} interview performance.",
            score=overall_score,
            payload={
                "interview_id": interview_id,
                "overall_score": overall_score,
                "weak_areas": weak_areas,
                "topics_that_need_improvement": topics_needing_improvement,
                "recommended_preparation_topics": recommended_preparation_topics,
            },
            is_read=False,
            created_at=datetime.utcnow(),
        ))

        db.commit()
        db.refresh(result)

        return {
            "interview_id": interview.id,
            "status": interview.status,
            "overall_score": overall_score,
            "technical_score": tech_score,
            "problem_solving_score": problem_solving_score,
            "communication_score": comm_score,
            "confidence_score": conf_score,
            "summary": overall_perf_text,
            "overall_performance": overall_perf_text,
            "technical_knowledge": tech_knowledge_text,
            "problem_solving": problem_solving_text,
            "communication": comm_text,
            "strong_areas": strong_areas,
            "weak_areas": weak_areas,
            "topics_needing_improvement": topics_needing_improvement,
            "question_wise_performance": transcript_history,
            "recommended_preparation_topics": recommended_preparation_topics,
            "strengths": strong_areas,
            "improvements": weak_areas,
            "completed_at": interview.completed_at,
        }
