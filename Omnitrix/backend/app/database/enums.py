from enum import Enum


class AssessmentMode(str, Enum):
    FULL = "FULL"
    APTITUDE = "APTITUDE"
    ENGLISH = "ENGLISH"
    DSA = "DSA"


class AssessmentSection(str, Enum):
    APTITUDE = "APTITUDE"
    ENGLISH = "ENGLISH"
    DSA = "DSA"
    PROFESSIONAL_KNOWLEDGE = "PROFESSIONAL_KNOWLEDGE"


class AssessmentStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"


class DifficultyLevel(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class QuestionStatus(str, Enum):
    UNSEEN = "UNSEEN"
    VIEWED = "VIEWED"
    ANSWERED = "ANSWERED"
    SKIPPED = "SKIPPED"
    FINALIZED = "FINALIZED"
