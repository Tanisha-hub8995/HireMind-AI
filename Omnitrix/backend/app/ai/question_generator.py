import json
import re
from difflib import SequenceMatcher
from typing import Sequence

from app.ai.llm_service import generate_llm_response


# ============================================================
# CONFIGURATION
# ============================================================

MAX_GENERATION_ATTEMPTS = 3

POSITIVE_MARK = 1.0
NEGATIVE_MARK = 0.25


# ============================================================
# SECTION DESCRIPTIONS
# ============================================================

SECTION_DESCRIPTIONS = {
    "aptitude": (
        "Quantitative aptitude involving arithmetic, percentages, "
        "profit and loss, ratios, averages, time and work, "
        "time and distance, interest, probability, permutations, "
        "mixtures, number systems, and quantitative reasoning."
    ),

    "english": (
        "English language skills including grammar, vocabulary, "
        "tenses, articles, prepositions, subject-verb agreement, "
        "synonyms, antonyms, sentence correction, usage, "
        "and reading/language reasoning."
    ),

    "dsa": (
        "Data structures and algorithms including arrays, strings, "
        "linked lists, stacks, queues, trees, graphs, hashing, "
        "sorting, searching, recursion, dynamic programming, "
        "and time/space complexity."
    ),
}


# ============================================================
# QUESTION TYPE SUGGESTIONS
# ============================================================

QUESTION_TYPE_SUGGESTIONS = {
    "aptitude": [
        "numerical calculation",
        "word problem",
        "comparison",
        "logical quantitative problem",
        "application problem",
        "data interpretation",
    ],

    "english": [
        "grammar identification",
        "fill in the blank",
        "sentence correction",
        "vocabulary",
        "synonym",
        "antonym",
        "usage question",
    ],

    "dsa": [
        "conceptual question",
        "complexity analysis",
        "output-based question",
        "algorithm behavior",
        "data structure property",
        "implementation concept",
    ],
}


# ============================================================
# EXPECTED TIME
# ============================================================

EXPECTED_TIME_RANGES = {
    "easy": (30, 60),
    "medium": (45, 90),
    "hard": (60, 120),
}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def _normalize_text(value: str) -> str:
    value = str(value or "").lower()

    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


# ============================================================
# QUESTION SIGNATURE
# ============================================================

def _question_signature(question: dict) -> str:
    text = _normalize_text(
        question.get(
            "question_text",
            "",
        )
    )

    return re.sub(
        r"\b\d+(?:\.\d+)?\b",
        "<num>",
        text,
    )


# ============================================================
# MEANINGFUL TOKENS
# ============================================================

def _meaningful_tokens(text: str) -> set[str]:

    stop_words = {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "to",
        "of",
        "in",
        "on",
        "for",
        "and",
        "or",
        "if",
        "then",
        "what",
        "which",
        "how",
        "many",
        "much",
        "does",
        "do",
        "did",
        "can",
        "could",
        "will",
        "would",
        "has",
        "have",
        "had",
        "with",
        "from",
        "by",
        "at",
        "as",
        "it",
        "this",
        "that",
        "these",
        "those",
        "than",
        "into",
        "their",
        "they",
        "them",
        "he",
        "she",
        "his",
        "her",
        "you",
        "your",
        "each",
        "per",
        "respectively",
    }

    return {
        token
        for token in _normalize_text(text).split()
        if token not in stop_words
        and len(token) > 2
    }


# ============================================================
# OPTION VALUES
# ============================================================

def _option_values(question: dict) -> list[str]:

    return [
        str(question.get("option_a", "")),
        str(question.get("option_b", "")),
        str(question.get("option_c", "")),
        str(question.get("option_d", "")),
    ]


# ============================================================
# CORRECT OPTION TEXT
# ============================================================

def _correct_option_text(question: dict) -> str:

    mapping = {
        "A": "option_a",
        "B": "option_b",
        "C": "option_c",
        "D": "option_d",
    }

    field = mapping.get(
        str(
            question.get(
                "correct_option",
                "",
            )
        )
        .strip()
        .upper()
    )

    return (
        str(question.get(field, ""))
        if field
        else ""
    )


# ============================================================
# NUMERIC VALUE
# ============================================================

def _numeric_value(
    value: str,
) -> float | None:

    matches = re.findall(
        r"-?\d+(?:\.\d+)?",
        str(value or ""),
    )

    return (
        float(matches[0])
        if matches
        else None
    )


# ============================================================
# FIND UNIQUE NUMERIC OPTION
# ============================================================

def _find_unique_numeric_option(
    question: dict,
    expected: float,
    tolerance: float = 0.01,
) -> str | None:

    matches = []

    for letter, field in zip(
        "ABCD",
        (
            "option_a",
            "option_b",
            "option_c",
            "option_d",
        ),
    ):

        value = _numeric_value(
            question.get(field, "")
        )

        if (
            value is not None
            and abs(value - expected) <= tolerance
        ):
            matches.append(letter)

    return (
        matches[0]
        if len(matches) == 1
        else None
    )


# ============================================================
# DUPLICATE QUESTION CHECK
# ============================================================

def _is_duplicate_question(
    question: dict,
    previous_questions: Sequence[dict],
) -> bool:

    current = _normalize_text(
        question.get(
            "question_text",
            "",
        )
    )

    if not current:
        return True

    signature = _question_signature(
        question
    )

    current_tokens = _meaningful_tokens(
        current
    )

    for previous in previous_questions:

        old = _normalize_text(
            previous.get(
                "question_text",
                "",
            )
        )

        if not old:
            continue

        if current == old:
            return True

        old_signature = _question_signature(
            previous
        )

        if signature and old_signature:

            if (
                SequenceMatcher(
                    None,
                    signature,
                    old_signature,
                ).ratio()
                >= 0.985
            ):
                return True

        old_tokens = _meaningful_tokens(
            old
        )

        if current_tokens and old_tokens:

            union = len(
                current_tokens | old_tokens
            )

            overlap = (
                len(
                    current_tokens
                    & old_tokens
                )
                / union
                if union
                else 0.0
            )

            text_similarity = (
                SequenceMatcher(
                    None,
                    current,
                    old,
                ).ratio()
            )

            if (
                overlap >= 0.90
                and text_similarity >= 0.90
            ):
                return True

    return False


# ============================================================
# TEMPLATE CHECK
# ============================================================

def _has_repeated_template(
    question: dict,
    previous_questions: Sequence[dict],
) -> bool:

    signature = _question_signature(
        question
    )

    if not signature:
        return True

    for previous in previous_questions:

        old_signature = _question_signature(
            previous
        )

        if (
            old_signature
            and SequenceMatcher(
                None,
                signature,
                old_signature,
            ).ratio()
            >= 0.985
        ):
            return True

    return False


# ============================================================
# STRUCTURE VALIDATION
# ============================================================

def _validate_structure(
    question: dict,
) -> tuple[bool, str]:

    required = [
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_option",
        "difficulty",
        "expected_time_seconds",
    ]

    for field in required:

        value = question.get(field)

        if value is None:

            return (
                False,
                f"Missing required field: {field}",
            )

        if (
            isinstance(value, str)
            and not value.strip()
        ):

            return (
                False,
                f"Missing or empty required field: {field}",
            )

    options = [
        _normalize_text(x)
        for x in _option_values(question)
    ]

    if len(set(options)) != 4:

        return (
            False,
            "All four answer options must be different.",
        )

    correct_option = (
        str(
            question.get(
                "correct_option",
                "",
            )
        )
        .strip()
        .upper()
    )

    if correct_option not in {
        "A",
        "B",
        "C",
        "D",
    }:

        return (
            False,
            "correct_option must be A, B, C, or D.",
        )

    if not _correct_option_text(
        question
    ).strip():

        return (
            False,
            "The marked correct option is empty.",
        )

    difficulty = (
        str(
            question.get(
                "difficulty",
                "",
            )
        )
        .strip()
        .lower()
    )

    if difficulty not in EXPECTED_TIME_RANGES:

        return (
            False,
            "difficulty must be easy, medium, or hard.",
        )

    try:

        expected_time = int(
            question[
                "expected_time_seconds"
            ]
        )

    except (
        TypeError,
        ValueError,
    ):

        return (
            False,
            "expected_time_seconds must be an integer.",
        )

    low, high = EXPECTED_TIME_RANGES[
        difficulty
    ]

    if not (
        low
        <= expected_time
        <= high
    ):

        return (
            False,
            (
                "expected_time_seconds must be "
                f"between {low} and {high} "
                f"for {difficulty}."
            ),
        )

    question["correct_option"] = (
        correct_option
    )

    question["difficulty"] = (
        difficulty
    )

    question["expected_time_seconds"] = (
        expected_time
    )

    return True, ""


# ============================================================
# PERCENTAGE VALIDATION
# ============================================================

def _validate_percentage_math(
    question: dict,
) -> tuple[bool, str]:

    text = str(
        question.get(
            "question_text",
            "",
        )
    )

    normalized = _normalize_text(
        text
    )

    numbers = [
        float(x)
        for x in re.findall(
            r"\d+(?:\.\d+)?",
            text,
        )
    ]

    if not any(
        x in normalized
        for x in (
            "percent",
            "percentage",
            "discount",
        )
    ):

        return True, ""

    correct = _numeric_value(
        _correct_option_text(question)
    )

    if correct is None:
        return True, ""

    if (
        "discount" in normalized
        and len(numbers) >= 2
    ):

        percentage = next(
            (
                x
                for x in numbers
                if 0 < x <= 100
            ),
            None,
        )

        price = next(
            (
                x
                for x in numbers
                if x != percentage
            ),
            None,
        )

        if (
            percentage is not None
            and price is not None
        ):

            expected = (
                price
                * (
                    1
                    - percentage / 100
                )
            )

            if abs(
                correct - expected
            ) > 0.01:

                fixed = (
                    _find_unique_numeric_option(
                        question,
                        expected,
                    )
                )

                if fixed:

                    question[
                        "correct_option"
                    ] = fixed

                    return True, ""

                return (
                    False,
                    "Incorrect percentage/discount answer.",
                )

    return True, ""


# ============================================================
# RATIO VALIDATION
# ============================================================

def _validate_ratio_math(
    question: dict,
) -> tuple[bool, str]:

    text = str(
        question.get(
            "question_text",
            "",
        )
    )

    normalized = _normalize_text(
        text
    )

    if not any(
        x in normalized
        for x in (
            "ratio",
            "proportion",
            "proportional",
        )
    ):

        return True, ""

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)",
        text,
    )

    if not match:
        return True, ""

    a = float(
        match.group(1)
    )

    b = float(
        match.group(2)
    )

    if b == 0:

        return (
            False,
            "Ratio denominator cannot be zero.",
        )

    given = re.search(
        r"if there (?:are|is)\s+"
        r"(\d+(?:\.\d+)?)\s+([a-z]+)",
        text,
        flags=re.IGNORECASE,
    )

    correct = _numeric_value(
        _correct_option_text(question)
    )

    if (
        given
        and correct is not None
        and a > 0
    ):

        expected = (
            float(given.group(1))
            * b
            / a
        )

        if abs(
            correct - expected
        ) > 0.01:

            fixed = (
                _find_unique_numeric_option(
                    question,
                    expected,
                )
            )

            if fixed:

                question[
                    "correct_option"
                ] = fixed

                return True, ""

            return (
                False,
                "Incorrect ratio answer.",
            )

    return True, ""


# ============================================================
# TIME AND WORK VALIDATION
# ============================================================

def _validate_time_work_math(
    question: dict,
) -> tuple[bool, str]:

    text = str(
        question.get(
            "question_text",
            "",
        )
    )

    normalized = _normalize_text(
        text
    )

    signals = (
        "worker",
        "workers",
        "work together",
        "working together",
        "complete a job",
        "alone",
    )

    if not any(
        signal in normalized
        for signal in signals
    ):

        return True, ""

    times = [
        float(x)
        for x in re.findall(
            r"(\d+(?:\.\d+)?)\s*"
            r"(?:days?|hours?)",
            normalized,
        )
    ]

    if len(times) < 2:
        return True, ""

    correct = _numeric_value(
        _correct_option_text(question)
    )

    if correct is None:
        return True, ""

    if any(
        x in normalized
        for x in (
            "work together",
            "working together",
            "together how long",
            "combined time",
        )
    ):

        a = times[0]
        b = times[1]

        if a <= 0 or b <= 0:

            return (
                False,
                "Work times must be greater than zero.",
            )

        expected = (
            1
            / (
                1 / a
                + 1 / b
            )
        )

        if abs(
            correct - expected
        ) > 0.05:

            fixed = (
                _find_unique_numeric_option(
                    question,
                    expected,
                    tolerance=0.05,
                )
            )

            if fixed:

                question[
                    "correct_option"
                ] = fixed

                return True, ""

            return (
                False,
                "Incorrect time-and-work answer.",
            )

    return True, ""


# ============================================================
# CONTENT VALIDATION
# ============================================================

def _validate_content(
    question: dict,
    section: str,
) -> tuple[bool, str]:

    if section == "aptitude":

        validators = (
            _validate_percentage_math,
            _validate_ratio_math,
            _validate_time_work_math,
        )

        for validator in validators:

            valid, reason = validator(
                question
            )

            if not valid:

                return (
                    False,
                    reason,
                )

    return True, ""


# ============================================================
# BUILD BATCH PROMPT
# ============================================================

def _build_batch_prompt(
    section: str,
    difficulty_counts: dict[str, int],
    previous_questions: Sequence[dict],
    rag_context: str,
) -> tuple[str, str]:

    section_description = (
        SECTION_DESCRIPTIONS[section]
    )

    styles = (
        QUESTION_TYPE_SUGGESTIONS[section]
    )

    total_requested = sum(
        difficulty_counts.values()
    )

    previous_block = "\n".join(
        f"{i}. {str(q.get('question_text', '')).strip()}"
        for i, q in enumerate(
            previous_questions[-20:],
            1,
        )
        if str(
            q.get(
                "question_text",
                "",
            )
        ).strip()
    )

    if not previous_block:
        previous_block = (
            "No previous questions."
        )

    difficulty_instructions = "\n".join(
        f"- {difficulty}: {count}"
        for difficulty, count
        in difficulty_counts.items()
        if count > 0
    )

    system_prompt = """
You are a high-quality question-generation engine
for an AI assessment platform.

Generate multiple completely NEW multiple-choice questions.

Return ONLY valid JSON.

Do not use markdown.
Do not use code fences.

Each question must contain exactly:

{
    "question_text": "...",
    "option_a": "...",
    "option_b": "...",
    "option_c": "...",
    "option_d": "...",
    "correct_option": "A",
    "difficulty": "easy",
    "expected_time_seconds": 45
}

Rules:

1. Generate exactly the requested number of questions.
2. Follow the requested difficulty distribution exactly.
3. Every question must have four distinct options.
4. Exactly one option must be correct.
5. The correct_option must be A, B, C, or D.
6. The correct answer must actually be correct.
7. Do not include topic.
8. Do not include question_type.
9. Do not include positive_mark.
10. Do not include negative_mark.
11. Avoid duplicates.
12. Avoid trivial paraphrases.
13. Avoid reusing the same question template.
14. Change the reasoning approach between questions.
15. Use RAG context when relevant.
16. For aptitude questions, calculate the answer before
    selecting the correct option.
17. For English questions, avoid ambiguous wording.
18. For DSA questions, ensure technical correctness.
19. Do not put explanations outside the JSON.
20. Return a JSON array of question objects.
""".strip()

    user_prompt = f"""
Assessment section:
{section}

Section description:
{section_description}

Required total questions:
{total_requested}

Required difficulty distribution:
{difficulty_instructions}

Suggested question styles:
{", ".join(styles)}

RAG / knowledge context:
{rag_context or "No additional knowledge context supplied."}

Previous questions:
{previous_block}

IMPORTANT:

Generate exactly {total_requested} NEW questions.

The returned array must contain exactly
{total_requested} objects.

Difficulty counts must be:

{difficulty_instructions}

For aptitude:
- Verify every numerical answer.
- Avoid inconsistent numerical data.
- Make distractors plausible but incorrect.
- Ensure exactly one option is correct.

For English:
- Ensure only one answer is clearly correct.

For DSA:
- Ensure algorithms and complexity claims are correct.

Return ONLY JSON.

Expected format:

[
    {{
        "question_text": "...",
        "option_a": "...",
        "option_b": "...",
        "option_c": "...",
        "option_d": "...",
        "correct_option": "A",
        "difficulty": "easy",
        "expected_time_seconds": 45
    }}
]
""".strip()

    return (
        system_prompt,
        user_prompt,
    )


# ============================================================
# GEMINI QUOTA ERROR
# ============================================================

def _is_gemini_quota_error(
    exc: Exception,
) -> bool:

    error_text = str(exc).lower()

    return (
        "429" in error_text
        or "resource_exhausted" in error_text
        or "quota exceeded" in error_text
        or "quota exhausted" in error_text
    )


# ============================================================
# GENERATE BATCH OF QUESTIONS
# ============================================================

def generate_question_batch(
    section: str,
    difficulty_counts: dict[str, int],
    previous_questions: Sequence[dict] | None = None,
    rag_context: str = "",
) -> list[dict]:

    previous_questions = list(
        previous_questions or []
    )

    section = (
        str(section)
        .strip()
        .lower()
    )

    if section not in SECTION_DESCRIPTIONS:

        raise ValueError(
            f"Unsupported section: {section}"
        )

    cleaned_counts = {}

    for difficulty, count in (
        difficulty_counts.items()
    ):

        difficulty = (
            str(difficulty)
            .strip()
            .lower()
        )

        count = int(count)

        if count <= 0:
            continue

        if difficulty not in EXPECTED_TIME_RANGES:

            raise ValueError(
                f"Unsupported difficulty: {difficulty}"
            )

        cleaned_counts[
            difficulty
        ] = count

    total_requested = sum(
        cleaned_counts.values()
    )

    if total_requested <= 0:

        raise ValueError(
            "At least one question must be requested."
        )

    last_failure = ""

    for attempt in range(
        1,
        MAX_GENERATION_ATTEMPTS + 1,
    ):

        print()
        print(
            f"Batch generation attempt "
            f"{attempt}/{MAX_GENERATION_ATTEMPTS}"
        )

        print(
            f"Section: {section}"
        )

        print(
            f"Requested batch size: "
            f"{total_requested}"
        )

        print(
            "Difficulty distribution:"
        )

        for difficulty, count in (
            cleaned_counts.items()
        ):

            print(
                f"  {difficulty}: {count}"
            )

        system_prompt, user_prompt = (
            _build_batch_prompt(
                section=section,
                difficulty_counts=cleaned_counts,
                previous_questions=previous_questions,
                rag_context=rag_context,
            )
        )

        # ----------------------------------------------------
        # GEMINI CALL
        # ----------------------------------------------------

        try:

            raw = generate_llm_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

        except Exception as exc:

            last_failure = (
                f"Gemini generation failed: {exc}"
            )

            print(last_failure)

            if _is_gemini_quota_error(
                exc
            ):

                print()
                print(
                    "Gemini quota exhausted."
                )

                print(
                    "Stopping Gemini requests immediately."
                )

                raise RuntimeError(
                    "Gemini API quota exhausted. "
                    "Please wait for the quota reset "
                    "or check your Gemini API plan/billing."
                ) from exc

            # Other temporary errors can retry.
            continue

        # ----------------------------------------------------
        # PARSE JSON
        # ----------------------------------------------------

        try:

            data = json.loads(raw)

        except json.JSONDecodeError as exc:

            last_failure = (
                f"Invalid JSON from Gemini: {exc}"
            )

            print(last_failure)

            continue

        # ----------------------------------------------------
        # HANDLE POSSIBLE WRAPPER OBJECT
        # ----------------------------------------------------

        if isinstance(data, dict):

            if isinstance(
                data.get("questions"),
                list,
            ):

                data = data[
                    "questions"
                ]

            else:

                data = [data]

        if not isinstance(
            data,
            list,
        ):

            last_failure = (
                "Gemini response is not a JSON array."
            )

            print(last_failure)

            continue

        # ----------------------------------------------------
        # CHECK BATCH SIZE
        # ----------------------------------------------------

        if len(data) != total_requested:

            last_failure = (
                "Gemini returned "
                f"{len(data)} questions, "
                f"but {total_requested} were requested."
            )

            print(
                f"Rejected: {last_failure}"
            )

            continue

        validated_questions = []

        batch_failed = False

        # ----------------------------------------------------
        # VALIDATE EVERY QUESTION
        # ----------------------------------------------------

        for index, question in enumerate(
            data,
            start=1,
        ):

            if not isinstance(
                question,
                dict,
            ):

                last_failure = (
                    f"Question {index} is not a JSON object."
                )

                print(
                    f"Rejected: {last_failure}"
                )

                batch_failed = True

                break

            # Remove fields Gemini may accidentally add.
            question.pop(
                "topic",
                None,
            )

            question.pop(
                "question_type",
                None,
            )

            question.pop(
                "positive_mark",
                None,
            )

            question.pop(
                "negative_mark",
                None,
            )

            # Structure
            valid, reason = (
                _validate_structure(
                    question
                )
            )

            if not valid:

                last_failure = (
                    f"Question {index}: "
                    f"{reason}"
                )

                print(
                    f"Rejected: {last_failure}"
                )

                batch_failed = True

                break

            # Difficulty
            generated_difficulty = (
                question[
                    "difficulty"
                ]
            )

            expected_count = (
                cleaned_counts.get(
                    generated_difficulty,
                    0,
                )
            )

            current_count = sum(
                1
                for q in validated_questions
                if q.get(
                    "difficulty"
                )
                == generated_difficulty
            )

            if (
                generated_difficulty
                not in cleaned_counts
            ):

                last_failure = (
                    f"Question {index}: "
                    f"Unexpected difficulty "
                    f"'{generated_difficulty}'."
                )

                print(
                    f"Rejected: {last_failure}"
                )

                batch_failed = True

                break

            if current_count >= expected_count:

                last_failure = (
                    f"Question {index}: "
                    f"Too many "
                    f"{generated_difficulty} questions."
                )

                print(
                    f"Rejected: {last_failure}"
                )

                batch_failed = True

                break

            # Duplicate check against database
            if _is_duplicate_question(
                question,
                previous_questions,
            ):

                last_failure = (
                    f"Question {index}: "
                    "Question is too similar "
                    "to an existing question."
                )

                print(
                    f"Rejected: {last_failure}"
                )

                batch_failed = True

                break

            # Duplicate check inside this batch
            if _is_duplicate_question(
                question,
                validated_questions,
            ):

                last_failure = (
                    f"Question {index}: "
                    "Question duplicates another "
                    "question in the same batch."
                )

                print(
                    f"Rejected: {last_failure}"
                )

                batch_failed = True

                break

            # Template check
            if _has_repeated_template(
                question,
                previous_questions,
            ):

                last_failure = (
                    f"Question {index}: "
                    "Question uses a repeated template."
                )

                print(
                    f"Rejected: {last_failure}"
                )

                batch_failed = True

                break

            # Content validation
            valid, reason = (
                _validate_content(
                    question,
                    section,
                )
            )

            if not valid:

                last_failure = (
                    f"Question {index}: "
                    f"{reason}"
                )

                print(
                    f"Rejected: {last_failure}"
                )

                batch_failed = True

                break

            # Backend controlled marks
            question[
                "positive_mark"
            ] = POSITIVE_MARK

            question[
                "negative_mark"
            ] = NEGATIVE_MARK

            validated_questions.append(
                question
            )

        # ----------------------------------------------------
        # BATCH VALIDATION FAILED
        # ----------------------------------------------------

        if batch_failed:

            print(
                "Batch rejected."
            )

            continue

        # ----------------------------------------------------
        # VERIFY DIFFICULTY COUNTS
        # ----------------------------------------------------

        actual_counts = {
            difficulty: sum(
                1
                for question
                in validated_questions
                if question.get(
                    "difficulty"
                )
                == difficulty
            )
            for difficulty
            in cleaned_counts
        }

        if actual_counts != cleaned_counts:

            last_failure = (
                "Gemini returned an incorrect "
                "difficulty distribution."
            )

            print(
                f"Rejected: {last_failure}"
            )

            print(
                f"Expected: {cleaned_counts}"
            )

            print(
                f"Received: {actual_counts}"
            )

            continue

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        print()
        print(
            f"✓ Gemini generated "
            f"{len(validated_questions)} valid questions."
        )

        return validated_questions

    # --------------------------------------------------------
    # ALL ATTEMPTS FAILED
    # --------------------------------------------------------

    raise RuntimeError(
        "Failed to generate a valid question batch "
        f"after {MAX_GENERATION_ATTEMPTS} attempts. "
        f"Last failure: {last_failure}"
    )


# ============================================================
# BACKWARD-COMPATIBLE SINGLE QUESTION FUNCTION
# ============================================================

def generate_one_question(
    section: str,
    difficulty: str,
    previous_questions: Sequence[dict] | None = None,
    rag_context: str = "",
    primary_topic: str | None = None,
) -> dict:

    del primary_topic

    questions = generate_question_batch(
        section=section,
        difficulty_counts={
            difficulty: 1,
        },
        previous_questions=previous_questions,
        rag_context=rag_context,
    )

    if not questions:

        raise RuntimeError(
            "Gemini returned no question."
        )

    return questions[0]