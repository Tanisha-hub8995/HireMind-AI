import argparse
import sys
from pathlib import Path


# ============================================================
# BACKEND PATH
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ============================================================
# APPLICATION IMPORTS
# ============================================================

from sqlalchemy import select

from app.database.database import SessionLocal

from app.database.enums import (
    AssessmentSection,
    DifficultyLevel,
)

from app.models.question import Question

from app.ai.rag.rag_service import RAGService

from app.ai.question_generator import (
    generate_question_batch,
)


# ============================================================
# CONFIGURATION
# ============================================================

RAG_TOP_K = 20


SUPPORTED_SECTIONS = {
    "aptitude": AssessmentSection.APTITUDE,
    "english": AssessmentSection.ENGLISH,
    "dsa": AssessmentSection.DSA,
}


# ============================================================
# RAG QUERIES
# ============================================================

RAG_QUERIES = {

    "aptitude": (
        "aptitude quantitative reasoning "
        "percentages profit and loss "
        "ratio and proportion averages "
        "time and work time speed and distance "
        "simple interest compound interest "
        "probability permutations number systems"
    ),

    "english": (
        "English grammar vocabulary "
        "tenses subject verb agreement "
        "articles prepositions "
        "synonyms antonyms sentence correction"
    ),

    "dsa": (
        "data structures algorithms "
        "arrays strings linked lists stacks queues "
        "trees graphs hashing sorting searching "
        "recursion dynamic programming "
        "time complexity space complexity"
    ),
}


# ============================================================
# NORMALIZE SECTION
# ============================================================

def normalize_section(
    section: str,
) -> str:

    section = (
        str(section)
        .strip()
        .lower()
    )

    if section not in SUPPORTED_SECTIONS:

        supported = ", ".join(
            SUPPORTED_SECTIONS.keys()
        )

        raise ValueError(
            f"Unsupported section '{section}'. "
            f"Supported sections: {supported}"
        )

    return section


# ============================================================
# DIFFICULTY DISTRIBUTION
# ============================================================

def build_difficulty_plan(
    count: int,
) -> dict[str, int]:

    if count <= 0:

        raise ValueError(
            "--count must be greater than 0."
        )

    base_count = count // 3

    remainder = count % 3

    easy_count = base_count
    medium_count = base_count
    hard_count = base_count

    if remainder >= 1:
        easy_count += 1

    if remainder >= 2:
        medium_count += 1

    return {
        "easy": easy_count,
        "medium": medium_count,
        "hard": hard_count,
    }


# ============================================================
# QUESTION -> DICTIONARY
# ============================================================

def question_to_dict(
    question: Question,
) -> dict:

    return {

        "id": question.id,

        "section": (
            question.section.value
            if hasattr(
                question.section,
                "value",
            )
            else str(
                question.section
            )
        ),

        "question_text": (
            question.question_text
        ),

        "option_a": question.option_a,

        "option_b": question.option_b,

        "option_c": question.option_c,

        "option_d": question.option_d,

        "correct_option": (
            question.correct_option
        ),

        "difficulty": (
            question.difficulty.value
            if hasattr(
                question.difficulty,
                "value",
            )
            else str(
                question.difficulty
            )
        ),

        "expected_time_seconds": (
            question.expected_time_seconds
        ),

        "positive_mark": (
            question.positive_mark
        ),

        "negative_mark": (
            question.negative_mark
        ),

        "is_active": (
            question.is_active
        ),
    }


# ============================================================
# LOAD EXISTING QUESTIONS
# ============================================================

def load_existing_questions(
    section: str,
) -> list[dict]:

    db_section = SUPPORTED_SECTIONS[
        section
    ]

    with SessionLocal() as db:

        statement = (
            select(Question)
            .where(
                Question.section
                == db_section
            )
            .order_by(
                Question.id
            )
        )

        questions = (
            db.scalars(
                statement
            ).all()
        )

        return [
            question_to_dict(
                question
            )
            for question in questions
        ]


# ============================================================
# SAVE QUESTION
# ============================================================

def save_question(
    section: str,
    question_data: dict,
) -> int:

    db_section = SUPPORTED_SECTIONS[
        section
    ]

    difficulty_text = (
        str(
            question_data.get(
                "difficulty",
                "",
            )
        )
        .strip()
        .lower()
    )

    difficulty_map = {

        "easy":
            DifficultyLevel.EASY,

        "medium":
            DifficultyLevel.MEDIUM,

        "hard":
            DifficultyLevel.HARD,
    }

    if difficulty_text not in difficulty_map:

        raise ValueError(
            "Invalid difficulty returned "
            f"by generator: {difficulty_text}"
        )

    new_question = Question(

        section=db_section,

        question_text=str(
            question_data[
                "question_text"
            ]
        ).strip(),

        option_a=str(
            question_data[
                "option_a"
            ]
        ).strip(),

        option_b=str(
            question_data[
                "option_b"
            ]
        ).strip(),

        option_c=str(
            question_data[
                "option_c"
            ]
        ).strip(),

        option_d=str(
            question_data[
                "option_d"
            ]
        ).strip(),

        correct_option=str(
            question_data[
                "correct_option"
            ]
        ).strip().upper(),

        difficulty=difficulty_map[
            difficulty_text
        ],

        expected_time_seconds=int(
            question_data[
                "expected_time_seconds"
            ]
        ),

        positive_mark=float(
            question_data.get(
                "positive_mark",
                1.0,
            )
        ),

        negative_mark=float(
            question_data.get(
                "negative_mark",
                0.25,
            )
        ),

        is_active=True,
    )

    with SessionLocal() as db:

        try:

            db.add(
                new_question
            )

            db.commit()

            db.refresh(
                new_question
            )

            return new_question.id

        except Exception:

            db.rollback()

            raise


# ============================================================
# BUILD RAG CONTEXT
# ============================================================

def build_rag_context(
    section: str,
) -> str:

    rag_service = RAGService(
        section
    )

    query = RAG_QUERIES[
        section
    ]

    print()
    print(
        "============================================================"
    )

    print(
        "BUILDING RAG CONTEXT"
    )

    print(
        "============================================================"
    )

    print(
        f"Section : {section}"
    )

    print(
        f"Query   : {query}"
    )

    print(
        f"Top K   : {RAG_TOP_K}"
    )

    print()

    context = (
        rag_service.retrieve_context(
            query=query,
            top_k=RAG_TOP_K,
        )
    )

    if (
        not context
        or not context.strip()
    ):

        raise RuntimeError(
            "RAG returned no context for "
            f"section '{section}'."
        )

    print(
        "✓ RAG context loaded successfully."
    )

    return context


# ============================================================
# PRINT QUESTION
# ============================================================

def print_question(
    question: dict,
    question_number: int,
    total_questions: int,
    database_id: int,
) -> None:

    print()
    print(
        "------------------------------------------------------------"
    )

    print(
        f"QUESTION {question_number}/{total_questions}"
    )

    print(
        "------------------------------------------------------------"
    )

    print(
        f"Database ID : {database_id}"
    )

    print(
        f"Difficulty  : "
        f"{question.get('difficulty', '')}"
    )

    print()

    print(
        "Question:"
    )

    print(
        question.get(
            "question_text",
            "",
        )
    )

    print()

    print(
        f"A. {question.get('option_a', '')}"
    )

    print(
        f"B. {question.get('option_b', '')}"
    )

    print(
        f"C. {question.get('option_c', '')}"
    )

    print(
        f"D. {question.get('option_d', '')}"
    )

    print()

    print(
        "Correct answer: "
        f"{question.get('correct_option', '')}"
    )

    print(
        "Expected time: "
        f"{question.get('expected_time_seconds', '')} "
        "seconds"
    )

    print(
        "Positive mark: "
        f"{question.get('positive_mark', 1.0)}"
    )

    print(
        "Negative mark: "
        f"{question.get('negative_mark', 0.25)}"
    )


# ============================================================
# ADD QUESTION TO HISTORY
# ============================================================

def add_question_to_history(
    existing_questions: list[dict],
    question: dict,
    database_id: int,
    section: str,
) -> None:

    existing_questions.append({

        "id": database_id,

        "section": section,

        "question_text": question[
            "question_text"
        ],

        "option_a": question[
            "option_a"
        ],

        "option_b": question[
            "option_b"
        ],

        "option_c": question[
            "option_c"
        ],

        "option_d": question[
            "option_d"
        ],

        "correct_option": question[
            "correct_option"
        ],

        "difficulty": question[
            "difficulty"
        ],

        "expected_time_seconds":
            question[
                "expected_time_seconds"
            ],

        "positive_mark":
            question.get(
                "positive_mark",
                1.0,
            ),

        "negative_mark":
            question.get(
                "negative_mark",
                0.25,
            ),
    })


# ============================================================
# GENERATE QUESTION BANK
# ============================================================

def generate_question_bank(
    section: str,
    count: int,
) -> None:

    section = normalize_section(
        section
    )

    if count <= 0:

        raise ValueError(
            "--count must be greater than 0."
        )

    difficulty_plan = (
        build_difficulty_plan(
            count
        )
    )

    # ========================================================
    # HEADER
    # ========================================================

    print()

    print(
        "============================================================"
    )

    print(
        "AI INTERVIEWER QUESTION BANK GENERATOR"
    )

    print(
        "============================================================"
    )

    print(
        f"Section          : {section}"
    )

    print(
        f"Requested        : {count}"
    )

    print()

    print(
        "Difficulty plan:"
    )

    print(
        f"  Easy   : "
        f"{difficulty_plan['easy']}"
    )

    print(
        f"  Medium : "
        f"{difficulty_plan['medium']}"
    )

    print(
        f"  Hard   : "
        f"{difficulty_plan['hard']}"
    )

    print(
        "============================================================"
    )

    # ========================================================
    # LOAD EXISTING QUESTIONS
    # ========================================================

    print()

    print(
        "Loading existing questions from Neon..."
    )

    existing_questions = (
        load_existing_questions(
            section
        )
    )

    print(
        f"✓ Existing {section} questions: "
        f"{len(existing_questions)}"
    )

    # ========================================================
    # RAG
    # ========================================================

    rag_context = (
        build_rag_context(
            section
        )
    )

    # ========================================================
    # BATCH GENERATION
    # ========================================================

    print()
    print(
        "============================================================"
    )

    print(
        "GENERATING QUESTION BATCH"
    )

    print(
        "============================================================"
    )

    print(
        f"Batch size : {count}"
    )

    print()

    try:

        questions = (
            generate_question_batch(

                section=section,

                difficulty_counts=(
                    difficulty_plan
                ),

                previous_questions=(
                    existing_questions
                ),

                rag_context=(
                    rag_context
                ),
            )
        )

    except Exception as exc:

        print()
        print(
            "✗ GENERATION FAILED"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        # ----------------------------------------------------
        # IMPORTANT
        # ----------------------------------------------------
        #
        # Do NOT retry here.
        #
        # generate_question_batch()
        # already handles normal retries.
        #
        # If Gemini returns 429 quota exhaustion,
        # generate_question_batch() raises immediately.
        #

        print()

        print(
            "Stopping question-bank generation."
        )

        print(
            "No more Gemini requests will be attempted."
        )

        print()

        return

    # ========================================================
    # VERIFY NUMBER OF QUESTIONS
    # ========================================================

    if len(questions) != count:

        raise RuntimeError(
            f"Expected {count} questions, "
            f"but received {len(questions)}."
        )

    # ========================================================
    # SAVE ALL QUESTIONS
    # ========================================================

    saved_count = 0
    failed_questions = 0

    print()
    print(
        "============================================================"
    )

    print(
        "SAVING QUESTIONS TO NEON"
    )

    print(
        "============================================================"
    )

    for index, question in enumerate(
        questions,
        start=1,
    ):

        try:

            database_id = save_question(
                section=section,
                question_data=question,
            )

            add_question_to_history(
                existing_questions=(
                    existing_questions
                ),
                question=question,
                database_id=database_id,
                section=section,
            )

            saved_count += 1

            print()
            print(
                f"✓ Question {index}/{count} "
                f"saved with database ID "
                f"{database_id}"
            )

            print(
                f"  Difficulty: "
                f"{question.get('difficulty')}"
            )

        except Exception as exc:

            failed_questions += 1

            print()
            print(
                f"✗ Question {index}/{count} "
                "failed to save."
            )

            print(
                f"{type(exc).__name__}: {exc}"
            )

    # ========================================================
    # FINAL DATABASE CHECK
    # ========================================================

    final_questions = (
        load_existing_questions(
            section
        )
    )

    # ========================================================
    # FINAL DIFFICULTY COUNTS
    # ========================================================

    easy_total = sum(

        1

        for question
        in final_questions

        if str(
            question.get(
                "difficulty",
                "",
            )
        ).lower()
        == "easy"
    )

    medium_total = sum(

        1

        for question
        in final_questions

        if str(
            question.get(
                "difficulty",
                "",
            )
        ).lower()
        == "medium"
    )

    hard_total = sum(

        1

        for question
        in final_questions

        if str(
            question.get(
                "difficulty",
                "",
            )
        ).lower()
        == "hard"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print()

    print(
        "============================================================"
    )

    print(
        "QUESTION BANK GENERATION COMPLETE"
    )

    print(
        "============================================================"
    )

    print(
        f"Section             : {section}"
    )

    print(
        f"Requested           : {count}"
    )

    print(
        f"Successfully saved  : {saved_count}"
    )

    print(
        f"Generation failures : "
        f"{failed_questions}"
    )

    print(
        f"Total in database   : "
        f"{len(final_questions)}"
    )

    print(
        "============================================================"
    )

    print()

    print(
        "DATABASE DIFFICULTY DISTRIBUTION"
    )

    print(
        f"Easy   : {easy_total}"
    )

    print(
        f"Medium : {medium_total}"
    )

    print(
        f"Hard   : {hard_total}"
    )

    print()

    if saved_count == count:

        print(
            "✓ SUCCESS"
        )

        print(
            f"Successfully generated and saved "
            f"{count} new {section} questions."
        )

    else:

        print(
            "⚠ GENERATION INCOMPLETE"
        )

        print(
            f"Only {saved_count} of {count} "
            "requested questions were saved."
        )

    print()

    print(
        "NOTE:"
    )

    print(
        "The question bank generator does NOT "
        "perform adaptive difficulty."
    )

    print(
        "During the live assessment, the adaptive "
        "engine evaluates every 5 attempted questions "
        "and selects the difficulty for the next block."
    )

    print()


# ============================================================
# ARGUMENT PARSER
# ============================================================

def parse_arguments():

    parser = argparse.ArgumentParser(

        description=(
            "Generate and save AI Interviewer "
            "questions into the Neon question bank."
        )
    )

    parser.add_argument(

        "--section",

        required=True,

        choices=[
            "aptitude",
            "english",
            "dsa",
        ],

        help="Assessment section.",
    )

    parser.add_argument(

        "--count",

        required=True,

        type=int,

        help=(
            "Number of NEW questions to generate."
        ),
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    args = parse_arguments()

    try:

        generate_question_bank(

            section=args.section,

            count=args.count,
        )

    except KeyboardInterrupt:

        print()
        print()

        print(
            "Generation cancelled by user."
        )

        sys.exit(1)

    except Exception as exc:

        print()
        print()

        print(
            "============================================================"
        )

        print(
            "QUESTION BANK GENERATION ERROR"
        )

        print(
            "============================================================"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        print(
            "============================================================"
        )

        sys.exit(1)