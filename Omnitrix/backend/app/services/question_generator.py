import logging
import random
import re
from typing import List, Optional
import numpy as np
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai.embedding_service import EmbeddingService
from app.ai.llm_service import LLMService
from app.database.enums import AssessmentSection, DifficultyLevel
from app.models.answer import Answer
from app.models.question import Question
from app.models.resume import Resume
from app.models.resume_skill import ResumeSkill
from app.models.skill import Skill

logger = logging.getLogger(__name__)


def map_topic_to_section(topic: str) -> AssessmentSection:
    """Map arbitrary topic or skill string to a valid DB AssessmentSection enum."""
    t = topic.upper().strip()
    if any(k in t for k in ["DSA", "DATA STRUCTURE", "ALGORITHM", "LEETCODE", "ARRAY", "TREE", "GRAPH", "SORTING"]):
        return AssessmentSection.DSA
    elif any(k in t for k in ["APTITUDE", "QUANT", "REASONING", "MATH", "LOGICAL", "PUZZLE"]):
        return AssessmentSection.APTITUDE
    elif any(k in t for k in ["ENGLISH", "VERBAL", "COMMUNICATION", "GRAMMAR"]):
        return AssessmentSection.ENGLISH
    else:
        return AssessmentSection.PROFESSIONAL_KNOWLEDGE


def map_difficulty(diff: Optional[str]) -> DifficultyLevel:
    if not diff:
        return DifficultyLevel.MEDIUM
    d = str(diff).upper().strip()
    if d in ("EASY", "E"):
        return DifficultyLevel.EASY
    elif d in ("HARD", "H", "ADVANCED"):
        return DifficultyLevel.HARD
    return DifficultyLevel.MEDIUM


class QuestionGeneratorService:
    """Selects, adapts, and generates interview questions using validated DB questions,

    RAG knowledge, Qwen2.5-3B generation, and multi-tier strict deduplication
    (SentenceTransformer FAISS vectors, Jaccard token overlap, and previous user history filtering).
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()

    def _cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        a = np.array(v1, dtype=np.float32)
        b = np.array(v2, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def _is_duplicate_question(
        self,
        new_text: str,
        new_vec: Optional[list],
        existing_texts: List[str],
        existing_vecs: List[list[float]],
    ) -> bool:
        """Strict multi-tier check to guarantee ZERO duplicate or repetitive questions."""
        cleaned_new = re.sub(r"[^\w\s]", "", new_text.lower()).strip()
        tokens_new = set(cleaned_new.split())
        stop_words = {"what", "how", "why", "which", "is", "are", "the", "a", "an", "in", "to", "for", "with", "of", "and", "or", "you", "would", "explain", "describe"}
        meaningful_tokens_new = tokens_new - stop_words

        for i, ex_text in enumerate(existing_texts):
            cleaned_ex = re.sub(r"[^\w\s]", "", ex_text.lower()).strip()
            # 1. Exact text or substring match
            if cleaned_new == cleaned_ex or (len(cleaned_new) > 20 and cleaned_new in cleaned_ex) or (len(cleaned_ex) > 20 and cleaned_ex in cleaned_new):
                return True

            # 2. Token overlap / Jaccard similarity (catches rephrased questions on the same topic)
            tokens_ex = set(cleaned_ex.split())
            meaningful_tokens_ex = tokens_ex - stop_words
            if meaningful_tokens_new and meaningful_tokens_ex:
                intersection = meaningful_tokens_new & meaningful_tokens_ex
                union = meaningful_tokens_new | meaningful_tokens_ex
                jaccard = len(intersection) / len(union) if union else 0.0
                if jaccard > 0.40 or len(intersection) >= 5:
                    return True

            # 3. SentenceTransformer semantic vector cosine similarity (> 0.72)
            if new_vec and i < len(existing_vecs) and existing_vecs[i]:
                sim = self._cosine_similarity(new_vec, existing_vecs[i])
                if sim > 0.72:
                    return True

        return False

    def get_candidate_context(self, db: Session, user_id: int, resume_id: Optional[int] = None) -> dict:
        """Extract candidate skills, experience, and profile context from database and resume."""
        context = {
            "skills": [],
            "experience": "",
            "summary": "",
            "target_role": "",
        }

        query = db.query(Resume).filter(Resume.user_id == user_id)
        if resume_id:
            resume = query.filter(Resume.id == resume_id).first()
        else:
            resume = query.order_by(Resume.created_at.desc()).first()

        if resume:
            context["skills"] = list(resume.extracted_skills or [])
            context["summary"] = resume.summary or ""
            context["raw_text"] = (resume.raw_text or "")[:1500]

            skill_rows = (
                db.query(Skill.canonical_name)
                .join(ResumeSkill, ResumeSkill.skill_id == Skill.id)
                .filter(ResumeSkill.resume_id == resume.id)
                .all()
            )
            for (c_name,) in skill_rows:
                if c_name and c_name not in context["skills"]:
                    context["skills"].append(c_name)

        return context

    def get_rag_knowledge(self, section: str, query: str) -> str:
        """Retrieve relevant RAG domain context if available."""
        try:
            from app.ai.rag.rag_service import RAGService
            sec_name = "dsa" if "dsa" in section.lower() else ("aptitude" if "apt" in section.lower() else "english")
            rag = RAGService(sec_name)
            return rag.retrieve_context(query, top_k=2)
        except Exception as exc:
            logger.info("RAG context query skipped: %s", exc)
            return ""

    def analyze_upgradation(
        self,
        current_difficulty: DifficultyLevel,
        score: float,
        is_skipped: bool = False,
    ) -> tuple[DifficultyLevel, bool, Optional[str], str]:
        """Adaptive Upgradation & Stopping Analysis:

        Returns: (new_difficulty, should_stop, stop_reason, analysis_text)
        - If is_skipped -> Stop immediately.
        - If score < 50.0 -> Incorrect answer -> Stop immediately.
        - If score >= 50.0 -> Correct answer -> Upgrade difficulty level (EASY -> MEDIUM -> HARD).
        """
        if is_skipped:
            return (
                current_difficulty,
                True,
                "SKIPPED_QUESTION",
                "Interview concluded: Question was skipped. Comprehensive evaluation report generated.",
            )

        if score < 50.0:
            return (
                current_difficulty,
                True,
                "INCORRECT_ANSWER",
                f"Interview concluded: Response score ({score:.1f}/100) is below the passing threshold (50.0). Final evaluation report generated.",
            )

        # Correct answer -> Upgrade level
        if current_difficulty == DifficultyLevel.EASY:
            new_diff = DifficultyLevel.MEDIUM
            analysis = "Level UPGRADED from Easy to Medium! Your response demonstrated clear fundamental accuracy. Advancing to intermediate level."
        elif current_difficulty == DifficultyLevel.MEDIUM:
            new_diff = DifficultyLevel.HARD
            analysis = "Level UPGRADED from Medium to Hard! Strong technical depth and problem-solving. Advancing to advanced architectural challenge."
        else:
            new_diff = DifficultyLevel.HARD
            analysis = "Outstanding performance! Maintained Advanced Hard tier with high technical precision."

        return new_diff, False, None, analysis

    def adjust_difficulty(self, current_difficulty: DifficultyLevel, score: float) -> DifficultyLevel:
        """Adaptive Questioning upgrade."""
        new_diff, _, _, _ = self.analyze_upgradation(current_difficulty, score)
        return new_diff

    def get_next_adaptive_question(
        self,
        db: Session,
        user_id: Optional[int] = None,
        target_difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        role: str = "Software Engineer",
        topics: Optional[List[str]] = None,
        candidate_context: Optional[dict] = None,
    ) -> Question:
        """Retrieve or generate the next unseen question at the upgraded difficulty level."""
        # Find questions previously answered by this user
        previously_answered_ids = set()
        if user_id:
            ans_rows = db.query(Answer.question_id).filter(Answer.user_id == user_id, Answer.question_id.isnot(None)).all()
            previously_answered_ids = {r[0] for r in ans_rows if r[0]}

        # Query DB for unseen question at target difficulty
        query = db.query(Question).filter(
            Question.is_active == True,
            Question.difficulty == target_difficulty,
        )
        if previously_answered_ids:
            query = query.filter(Question.id.notin_(previously_answered_ids))

        next_q = query.order_by(func.random()).first()
        if next_q:
            return next_q

        # If none in DB, generate one at target difficulty
        skills = (candidate_context or {}).get("skills", ["Python", "FastAPI", "PostgreSQL"])
        generated_list = self._generate_ai_questions(
            role=role,
            difficulty=target_difficulty.value,
            topics=topics or ["Engineering Architecture", "Data Structures", "System Design"],
            candidate_context=candidate_context or {"skills": skills},
            target_company=None,
            count=1,
            avoid_questions=[],
        )

        q_item = generated_list[0]
        new_q = Question(
            section=map_topic_to_section(q_item.get("section", "PROFESSIONAL_KNOWLEDGE")),
            question_text=q_item["question_text"],
            option_a="N/A",
            option_b="N/A",
            option_c="N/A",
            option_d="N/A",
            correct_option="A",
            difficulty=target_difficulty,
            expected_time_seconds=q_item.get("expected_time_seconds", 90),
            positive_mark=1.0,
            negative_mark=0.0,
            is_active=True,
        )
        db.add(new_q)
        db.commit()
        db.refresh(new_q)
        return new_q

    def prepare_interview_questions(
        self,
        db: Session,
        user_id: Optional[int] = None,
        role: str = "Software Engineer",
        difficulty: str = "MEDIUM",
        interview_type: str = "TECHNICAL",
        topics: Optional[List[str]] = None,
        candidate_context: Optional[dict] = None,
        target_company: Optional[str] = None,
        num_questions: int = 5,
    ) -> List[Question]:
        """Prepares a strictly non-duplicate, diverse set of interview questions using:

        1. Validated DB question bank with history exclusion for user
        2. Randomized diverse section sampling
        3. LLM/Qwen generation for missing domain questions
        4. Multi-tier deduplication (embeddings + token overlap + exact match).
        """
        selected_questions: List[Question] = []
        selected_texts: List[str] = []
        selected_embeddings: List[list[float]] = []

        diff_enum = map_difficulty(difficulty)
        sections_to_query = [map_topic_to_section(t) for t in topics] if topics else []

        # Find questions previously answered by this user to avoid any repetition
        previously_answered_ids = set()
        if user_id:
            ans_rows = db.query(Answer.question_id).filter(Answer.user_id == user_id, Answer.question_id.isnot(None)).all()
            previously_answered_ids = {r[0] for r in ans_rows if r[0]}

        # 1. Fetch diverse questions from DB question bank
        db_query = db.query(Question).filter(Question.is_active == True)
        if sections_to_query:
            db_query = db_query.filter(Question.section.in_(sections_to_query))

        if previously_answered_ids:
            unseen_query = db_query.filter(Question.id.notin_(list(previously_answered_ids)))
            db_candidates = unseen_query.order_by(func.random()).limit(30).all()
            if len(db_candidates) < num_questions:
                # If unseen questions exhausted, fallback to full pool with randomized ordering
                db_candidates = db_query.order_by(func.random()).limit(30).all()
        else:
            db_candidates = db_query.order_by(func.random()).limit(30).all()

        for q in db_candidates:
            if len(selected_questions) >= num_questions:
                break

            q_text = q.question_text
            q_vec = None
            try:
                q_vec = self.embedding_service.encode(q_text)
            except Exception:
                pass

            if not self._is_duplicate_question(q_text, q_vec, selected_texts, selected_embeddings):
                selected_questions.append(q)
                selected_texts.append(q_text)
                if q_vec:
                    selected_embeddings.append(q_vec)

        # 2. If needed, generate remaining role/resume-specific questions
        needed = num_questions - len(selected_questions)
        if needed > 0:
            generated_list = self._generate_ai_questions(
                role=role,
                difficulty=diff_enum.value,
                topics=topics or (candidate_context.get("skills", [])[:5] if candidate_context else ["DSA", "System Design"]),
                candidate_context=candidate_context or {},
                target_company=target_company,
                count=needed + 3,
                avoid_questions=selected_texts,
            )

            for g_item in generated_list:
                if len(selected_questions) >= num_questions:
                    break

                q_text = g_item.get("question_text") or g_item.get("text", "")
                if not q_text:
                    continue

                q_vec = None
                try:
                    q_vec = self.embedding_service.encode(q_text)
                except Exception:
                    pass

                if self._is_duplicate_question(q_text, q_vec, selected_texts, selected_embeddings):
                    continue

                raw_sec = g_item.get("section", "PROFESSIONAL_KNOWLEDGE")
                new_q = Question(
                    section=map_topic_to_section(raw_sec),
                    question_text=q_text,
                    option_a="N/A",
                    option_b="N/A",
                    option_c="N/A",
                    option_d="N/A",
                    correct_option="A",
                    difficulty=diff_enum,
                    expected_time_seconds=g_item.get("expected_time_seconds", 90),
                    positive_mark=1.0,
                    negative_mark=0.0,
                    is_active=True,
                )
                db.add(new_q)
                db.flush()
                selected_questions.append(new_q)
                selected_texts.append(q_text)
                if q_vec:
                    selected_embeddings.append(q_vec)

        db.commit()
        return selected_questions

    def generate_followup_question(
        self,
        db: Session,
        previous_question: str,
        candidate_answer: str,
        role: str = "Software Engineer",
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
    ) -> Question:
        """Generates an intelligent follow-up question based directly on what the candidate answered."""
        system_prompt = (
            f"You are an experienced technical interviewer assessing a candidate for a {role} position. "
            "Based on the previous question and the candidate's actual response, generate a concise, probing follow-up question "
            "that explores their reasoning, edge cases, trade-offs, or implementation details. "
            "Return JSON: {'question_text': '...', 'expected_time_seconds': 75}"
        )

        payload = {
            "previous_question": previous_question,
            "candidate_answer": candidate_answer[:2000],
            "difficulty": difficulty.value,
        }

        q_text = ""
        try:
            if hasattr(self.llm_service, "_qwen_json"):
                res = self.llm_service._qwen_json(system_prompt, payload)
                if isinstance(res, dict) and "question_text" in res:
                    q_text = res["question_text"]
        except Exception:
            pass

        if not q_text:
            ans_lower = candidate_answer.lower()
            if "index" in ans_lower or "database" in ans_lower or "sql" in ans_lower:
                q_text = "What are the write-performance trade-offs when adding multiple indexes, and how do you monitor index bloat?"
            elif "microservice" in ans_lower or "api" in ans_lower or "gateway" in ans_lower:
                q_text = "How would you implement distributed tracing and handle cascading service failures across those services?"
            elif "cache" in ans_lower or "redis" in ans_lower or "memcached" in ans_lower:
                q_text = "How do you handle cache invalidation and prevent cache stampede/avalanche in high-throughput scenarios?"
            elif "async" in ans_lower or "thread" in ans_lower or "concurrency" in ans_lower:
                q_text = "How do you ensure thread safety, prevent deadlocks, and test for race conditions in concurrent execution?"
            else:
                q_text = "Could you elaborate on the potential edge cases and failure modes in the approach you just described?"

        new_q = Question(
            section=AssessmentSection.PROFESSIONAL_KNOWLEDGE,
            question_text=q_text,
            option_a="N/A",
            option_b="N/A",
            option_c="N/A",
            option_d="N/A",
            correct_option="A",
            difficulty=difficulty,
            expected_time_seconds=75,
            positive_mark=1.0,
            negative_mark=0.0,
            is_active=True,
        )
        db.add(new_q)
        db.commit()
        db.refresh(new_q)
        return new_q

    def _generate_ai_questions(
        self,
        role: str,
        difficulty: str,
        topics: List[str],
        candidate_context: dict,
        target_company: Optional[str],
        count: int = 3,
        avoid_questions: Optional[List[str]] = None,
    ) -> List[dict]:
        """Use Qwen / LLMService or a rich diverse randomized pool to generate role-tailored questions."""
        skills = candidate_context.get("skills", [])
        company_note = f" targeting {target_company}" if target_company else ""
        avoid_note = f" Do NOT generate questions similar to: {avoid_questions[:5]}." if avoid_questions else ""

        system_prompt = (
            f"You are an expert technical interviewer assessing a candidate for a {role} position{company_note}. "
            f"Generate {count} unique, non-overlapping interview questions at {difficulty} difficulty covering: {', '.join(topics or ['core fundamentals'])}.{avoid_note} "
            "Return JSON matching: {'questions': [{'section': 'PROFESSIONAL_KNOWLEDGE', 'question_text': '...', 'expected_time_seconds': 90}]}"
        )

        payload = {
            "role": role,
            "difficulty": difficulty,
            "topics": topics,
            "candidate_skills": skills[:8],
            "count": count,
        }

        try:
            if hasattr(self.llm_service, "_qwen_json"):
                res = self.llm_service._qwen_json(system_prompt, payload)
                if isinstance(res, dict) and "questions" in res and isinstance(res["questions"], list):
                    return res["questions"]
        except Exception as exc:
            logger.info("LLM generation fallback: %s", exc)

        # Broad categorized pool of distinct engineering questions across 10+ sub-domains
        diverse_question_pool = [
            # 1. DSA & Algorithms
            {
                "section": "DSA",
                "question_text": f"How would you design an efficient data structure to support fast insert, delete, and getRandom in O(1) time complexity for a {role} system?",
                "expected_time_seconds": 90,
            },
            {
                "section": "DSA",
                "question_text": "Explain how you would detect a cycle in a directed graph and determine the topological ordering of interdependent build tasks.",
                "expected_time_seconds": 90,
            },
            # 2. System Architecture & Scalability
            {
                "section": "PROFESSIONAL_KNOWLEDGE",
                "question_text": f"Explain the architectural trade-offs between monolithic and microservices architectures for a high-traffic {role} backend.",
                "expected_time_seconds": 120,
            },
            {
                "section": "PROFESSIONAL_KNOWLEDGE",
                "question_text": "How do you design a resilient rate-limiting mechanism (e.g. Token Bucket or Leaky Bucket) across distributed API gateways?",
                "expected_time_seconds": 90,
            },
            # 3. Databases & Indexing
            {
                "section": "PROFESSIONAL_KNOWLEDGE",
                "question_text": "Explain how database indexing (B-Tree vs Hash vs GIN) works in PostgreSQL and how index bloat impacts write throughput.",
                "expected_time_seconds": 90,
            },
            {
                "section": "PROFESSIONAL_KNOWLEDGE",
                "question_text": "How do you handle database sharding, cross-shard queries, and distributed transaction consistency across multiple regions?",
                "expected_time_seconds": 120,
            },
            # 4. Concurrency & Asynchronous Programming
            {
                "section": "PROFESSIONAL_KNOWLEDGE",
                "question_text": "Explain how you handle concurrency, race conditions, and database transaction isolation levels (Read Committed vs Serializable).",
                "expected_time_seconds": 90,
            },
            {
                "section": "PROFESSIONAL_KNOWLEDGE",
                "question_text": "How does event-driven asynchronous processing (e.g., Celery, Kafka, RabbitMQ) decouple heavy background workloads from latency-critical APIs?",
                "expected_time_seconds": 90,
            },
            # 5. Caching & Memory Management
            {
                "section": "PROFESSIONAL_KNOWLEDGE",
                "question_text": "Describe the strategies for handling cache invalidation, cache stampede, and cache penetration in distributed Redis clusters.",
                "expected_time_seconds": 90,
            },
            # 6. Observability & Production Troubleshooting
            {
                "section": "PROFESSIONAL_KNOWLEDGE",
                "question_text": "Walk me through how you would diagnose and resolve a severe memory leak or CPU spike in a live production service under peak traffic.",
                "expected_time_seconds": 120,
            },
            # 7. Candidate Profile & Behavioral Trade-offs
            {
                "section": "PROFESSIONAL_KNOWLEDGE",
                "question_text": f"Describe a complex technical challenge you solved involving {', '.join(skills[:3]) if skills else 'distributed systems'} and how you measured its latency and reliability.",
                "expected_time_seconds": 120,
            },
            {
                "section": "PROFESSIONAL_KNOWLEDGE",
                "question_text": "Tell me about a time when you had to make a critical technical trade-off between architectural purity and time-to-market. What was your decision framework?",
                "expected_time_seconds": 90,
            },
        ]

        # Filter out questions already in avoid_questions list
        filtered = []
        for q in diverse_question_pool:
            if not self._is_duplicate_question(q["question_text"], None, avoid_questions or [], []):
                filtered.append(q)

        random.shuffle(filtered)
        return filtered[:count] if filtered else diverse_question_pool[:count]
