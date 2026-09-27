from dataclasses import dataclass


DIFFICULTY_ORDER = ["easy", "medium", "hard"]

WINDOW_SIZE = 5

# Accuracy thresholds
HIGH_ACCURACY = 0.80
LOW_ACCURACY = 0.40

# Time thresholds
FAST_TIME_RATIO = 0.80
SLOW_TIME_RATIO = 1.20


@dataclass
class DifficultyDecision:
    current_difficulty: str
    next_difficulty: str
    attempted: int
    correct: int
    wrong: int
    skipped: int
    accuracy: float
    average_time_ratio: float
    reason: str


def normalize_difficulty(difficulty: str) -> str:
    difficulty = str(difficulty).strip().lower()

    if difficulty not in DIFFICULTY_ORDER:
        raise ValueError(
            f"Invalid difficulty: {difficulty}"
        )

    return difficulty


def increase_difficulty(difficulty: str) -> str:
    difficulty = normalize_difficulty(difficulty)

    current_index = DIFFICULTY_ORDER.index(difficulty)

    if current_index == len(DIFFICULTY_ORDER) - 1:
        return difficulty

    return DIFFICULTY_ORDER[current_index + 1]


def decrease_difficulty(difficulty: str) -> str:
    difficulty = normalize_difficulty(difficulty)

    current_index = DIFFICULTY_ORDER.index(difficulty)

    if current_index == 0:
        return difficulty

    return DIFFICULTY_ORDER[current_index - 1]


def calculate_window_statistics(
    answers: list[dict],
) -> dict:
    """
    Calculate performance statistics for one
    5-question adaptation window.

    Each answer dictionary should contain:

        is_correct
        is_skipped
        response_time_seconds
        expected_time_seconds
    """

    attempted = 0
    correct = 0
    wrong = 0
    skipped = 0

    time_ratios = []

    for answer in answers:

        is_skipped = bool(
            answer.get("is_skipped", False)
        )

        if is_skipped:
            skipped += 1
            continue

        attempted += 1

        if bool(answer.get("is_correct", False)):
            correct += 1
        else:
            wrong += 1

        actual_time = float(
            answer.get(
                "response_time_seconds",
                0,
            )
        )

        expected_time = float(
            answer.get(
                "expected_time_seconds",
                60,
            )
        )

        if expected_time > 0 and actual_time > 0:
            time_ratio = (
                actual_time / expected_time
            )

            time_ratios.append(time_ratio)

    if attempted > 0:
        accuracy = correct / attempted
    else:
        accuracy = 0.0

    if time_ratios:
        average_time_ratio = (
            sum(time_ratios)
            / len(time_ratios)
        )
    else:
        average_time_ratio = 1.0

    return {
        "attempted": attempted,
        "correct": correct,
        "wrong": wrong,
        "skipped": skipped,
        "accuracy": accuracy,
        "average_time_ratio": average_time_ratio,
    }


def decide_next_difficulty(
    current_difficulty: str,
    answers: list[dict],
) -> DifficultyDecision:
    """
    Decide difficulty ONLY after a complete
    5-question window.

    The function does NOT change difficulty
    before 5 questions have been completed.
    """

    current_difficulty = normalize_difficulty(
        current_difficulty
    )

    if len(answers) < WINDOW_SIZE:
        raise ValueError(
            "Difficulty can only be evaluated "
            "after 5 questions."
        )

    # Only use the most recent 5 answers.
    window = answers[-WINDOW_SIZE:]

    stats = calculate_window_statistics(
        window
    )

    attempted = stats["attempted"]
    correct = stats["correct"]
    wrong = stats["wrong"]
    skipped = stats["skipped"]
    accuracy = stats["accuracy"]
    average_time_ratio = (
        stats["average_time_ratio"]
    )

    # --------------------------------------------------
    # CASE 1: User has not attempted anything
    # --------------------------------------------------

    if attempted == 0:

        return DifficultyDecision(
            current_difficulty=current_difficulty,
            next_difficulty=current_difficulty,
            attempted=attempted,
            correct=correct,
            wrong=wrong,
            skipped=skipped,
            accuracy=accuracy,
            average_time_ratio=average_time_ratio,
            reason=(
                "No questions were attempted, "
                "so difficulty remains unchanged."
            ),
        )

    # --------------------------------------------------
    # FAST / SLOW
    # --------------------------------------------------

    is_fast = (
        average_time_ratio <= FAST_TIME_RATIO
    )

    is_slow = (
        average_time_ratio >= SLOW_TIME_RATIO
    )

    # --------------------------------------------------
    # HIGH PERFORMANCE
    #
    # 4 or 5 correct out of attempted questions
    # AND reasonably fast.
    # --------------------------------------------------

    if (
        accuracy >= HIGH_ACCURACY
        and is_fast
    ):

        next_difficulty = increase_difficulty(
            current_difficulty
        )

        reason = (
            f"High consistency: "
            f"{correct}/{attempted} correct "
            f"with fast response time. "
            f"Difficulty increased."
        )

    # --------------------------------------------------
    # LOW PERFORMANCE
    #
    # 0–2 correct approximately
    # AND generally slow.
    # --------------------------------------------------

    elif (
        accuracy <= LOW_ACCURACY
        and is_slow
    ):

        next_difficulty = decrease_difficulty(
            current_difficulty
        )

        reason = (
            f"Low consistency: "
            f"{correct}/{attempted} correct "
            f"with slow response time. "
            f"Difficulty decreased."
        )

    # --------------------------------------------------
    # EVERYTHING ELSE
    #
    # Mixed performance:
    # keep the same difficulty.
    # --------------------------------------------------

    else:

        next_difficulty = current_difficulty

        if is_fast:
            speed_description = "fast"
        elif is_slow:
            speed_description = "slow"
        else:
            speed_description = "moderate"

        reason = (
            f"Mixed consistency: "
            f"{correct}/{attempted} correct "
            f"with {speed_description} response time. "
            f"Difficulty remains unchanged."
        )

    return DifficultyDecision(
        current_difficulty=current_difficulty,
        next_difficulty=next_difficulty,
        attempted=attempted,
        correct=correct,
        wrong=wrong,
        skipped=skipped,
        accuracy=accuracy,
        average_time_ratio=average_time_ratio,
        reason=reason,
    )


def should_adapt(
    completed_questions: int,
) -> bool:
    """
    Returns True only when another complete
    5-question window has been completed.
    """

    return (
        completed_questions > 0
        and completed_questions % WINDOW_SIZE == 0
    )