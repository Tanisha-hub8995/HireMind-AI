# ============================================================
# ASSESSMENT SCORING SERVICE
# ============================================================


DIFFICULTY_WEIGHTS = {
    "easy": 1.0,
    "medium": 1.25,
    "hard": 1.50,
}


# ============================================================
# QUESTION SCORE
# ============================================================

def calculate_question_score(
    is_correct: bool,
    selected_option,
    positive_mark: float = 1.0,
    negative_mark: float = 0.25
) -> float:

    # No answer = skipped
    if selected_option is None:
        return 0.0

    # Correct answer
    if is_correct:
        return positive_mark

    # Wrong answer
    return -negative_mark


# ============================================================
# ACCURACY
# ============================================================

def calculate_accuracy(
    correct_count: int,
    attempted_count: int
) -> float:

    if attempted_count == 0:
        return 0.0

    return (
        correct_count / attempted_count
    ) * 100


# ============================================================
# TIME EFFICIENCY
# ============================================================

def calculate_time_efficiency(
    expected_time_seconds: int,
    actual_time_seconds: int
) -> float:

    if actual_time_seconds <= 0:
        return 100.0

    efficiency = (
        expected_time_seconds
        / actual_time_seconds
    ) * 100

    return min(100.0, efficiency)


# ============================================================
# DIFFICULTY WEIGHT
# ============================================================

def get_difficulty_weight(difficulty) -> float:

    difficulty = str(difficulty).lower()

    # Handles:
    # DifficultyLevel.EASY
    # DifficultyLevel.MEDIUM
    # DifficultyLevel.HARD

    if "." in difficulty:
        difficulty = difficulty.split(".")[-1]

    return DIFFICULTY_WEIGHTS.get(
        difficulty,
        1.0
    )


# ============================================================
# DIFFICULTY SCORE
# ============================================================

def calculate_difficulty_score(
    question_score_pairs
) -> float:

    weighted_score = 0.0

    weighted_maximum = 0.0

    for question, score in question_score_pairs:

        weight = get_difficulty_weight(
            question.difficulty
        )

        weighted_score += (
            score * weight
        )

        weighted_maximum += (
            question.positive_mark * weight
        )

    if weighted_maximum == 0:
        return 0.0

    return (
        weighted_score
        / weighted_maximum
    ) * 100


# ============================================================
# INDIVIDUAL SECTION EVALUATION
# ============================================================

def evaluate_section(
    answers,
    questions
):
    """
    Evaluate ONE section only.

    Example:

    Aptitude answers
        -> Aptitude result

    English answers
        -> English result

    DSA answers
        -> DSA result

    Professional Knowledge answers
        -> Professional Knowledge result
    """

    correct_count = 0

    wrong_count = 0

    skipped_count = 0

    total_score = 0.0

    maximum_score = 0.0

    expected_time_seconds = 0

    actual_time_seconds = 0

    question_map = {
        question.id: question
        for question in questions
    }

    question_score_pairs = []

    # --------------------------------------------------------
    # Evaluate each answer
    # --------------------------------------------------------

    for answer in answers:

        question = question_map.get(
            answer.question_id
        )

        if question is None:
            continue

        # ----------------------------------------------------
        # Maximum possible marks
        # ----------------------------------------------------

        maximum_score += (
            question.positive_mark
        )

        # ----------------------------------------------------
        # Expected time
        # ----------------------------------------------------

        expected_time_seconds += (
            question.expected_time_seconds
        )

        # ----------------------------------------------------
        # Actual time
        # ----------------------------------------------------

        actual_time_seconds += (
            answer.time_spent_seconds or 0
        )

        # ----------------------------------------------------
        # SKIPPED
        # ----------------------------------------------------

        if answer.selected_option is None:

            skipped_count += 1

            score = 0.0

            answer.is_correct = None

            answer.marks_awarded = 0.0

        # ----------------------------------------------------
        # CORRECT
        # ----------------------------------------------------

        elif (
            answer.selected_option.upper()
            == question.correct_option.upper()
        ):

            correct_count += 1

            score = question.positive_mark

            answer.is_correct = True

            answer.marks_awarded = score

        # ----------------------------------------------------
        # WRONG
        # ----------------------------------------------------

        else:

            wrong_count += 1

            score = -question.negative_mark

            answer.is_correct = False

            answer.marks_awarded = score

        # ----------------------------------------------------
        # Add score
        # ----------------------------------------------------

        total_score += score

        question_score_pairs.append(
            (question, score)
        )

    # --------------------------------------------------------
    # Attempted
    # --------------------------------------------------------

    attempted_count = (
        correct_count
        + wrong_count
    )

    # --------------------------------------------------------
    # Accuracy
    # --------------------------------------------------------

    accuracy = calculate_accuracy(
        correct_count,
        attempted_count
    )

    # --------------------------------------------------------
    # Time efficiency
    # --------------------------------------------------------

    time_efficiency = calculate_time_efficiency(
        expected_time_seconds,
        actual_time_seconds
    )

    # --------------------------------------------------------
    # Difficulty score
    # --------------------------------------------------------

    difficulty_score = calculate_difficulty_score(
        question_score_pairs
    )

    # --------------------------------------------------------
    # Percentage
    # --------------------------------------------------------

    percentage = 0.0

    if maximum_score > 0:

        percentage = (
            total_score
            / maximum_score
        ) * 100

    # --------------------------------------------------------
    # Return section result
    # --------------------------------------------------------

    return {

        "score": round(
            total_score,
            2
        ),

        "maximum_score": round(
            maximum_score,
            2
        ),

        "percentage": round(
            percentage,
            2
        ),

        "correct_count": correct_count,

        "wrong_count": wrong_count,

        "skipped_count": skipped_count,

        "attempted_count": attempted_count,

        "accuracy": round(
            accuracy,
            2
        ),

        "time_efficiency": round(
            time_efficiency,
            2
        ),

        "difficulty_score": round(
            difficulty_score,
            2
        )
    }


# ============================================================
# FINAL EXAM EVALUATION
# ============================================================

def calculate_full_result(
    section_results
):
    """
    Combine the results of the four sections.

    IMPORTANT:

    This function does NOT evaluate questions.

    The four sections are already evaluated
    individually before this function runs.
    """

    total_score = 0.0

    maximum_score = 0.0

    for section_result in section_results:

        total_score += (
            section_result["score"]
        )

        maximum_score += (
            section_result["maximum_score"]
        )

    percentage = 0.0

    if maximum_score > 0:

        percentage = (
            total_score
            / maximum_score
        ) * 100

    return {

        "total_score": round(
            total_score,
            2
        ),

        "maximum_score": round(
            maximum_score,
            2
        ),

        "percentage": round(
            percentage,
            2
        ),

        "sections": section_results
    }