from pathlib import Path
import re


# ---------------------------------------------------------
# Topic keywords
# ---------------------------------------------------------

TOPIC_KEYWORDS = {

    # =====================================================
    # DSA
    # =====================================================

    "Arrays": [
        "array",
        "arrays",
        "contiguous memory",
        "index",
        "indexing",
        "unsorted array",
    ],

    "Binary Search": [
        "binary search",
        "sorted data",
        "search space",
        "log n",
        "o(log n)",
    ],

    "Linked Lists": [
        "linked list",
        "linked lists",
        "node",
        "nodes",
        "head pointer",
        "reference to another node",
    ],

    "Stacks": [
        "stack",
        "stacks",
        "lifo",
        "last in, first out",
        "push",
        "pop",
    ],

    "Queues": [
        "queue",
        "queues",
        "fifo",
        "first in, first out",
        "enqueue",
        "dequeue",
    ],

    "Sorting": [
        "sorting",
        "bubble sort",
        "merge sort",
        "quick sort",
        "o(n²)",
        "o(n log n)",
    ],


    # =====================================================
    # Aptitude
    # =====================================================

    "Percentages": [
        "percentage",
        "percentages",
        "percentage increase",
        "percentage decrease",
        "percent of",
    ],

    "Profit and Loss": [
        "profit",
        "loss",
        "cost price",
        "selling price",
        "profit percentage",
        "loss percentage",
    ],

    "Ratio and Proportion": [
        "ratio",
        "ratios",
        "proportion",
        "proportions",
    ],

    "Time and Work": [
        "time and work",
        "one-day work",
        "one day work",
        "combined work",
        "days to complete",
    ],

    "Averages": [
        "average",
        "averages",
        "mean",
    ],

    "Simple Interest": [
        "simple interest",
        "principal",
        "rate of interest",
        "time period",
    ],

    "Compound Interest": [
        "compound interest",
        "compounded",
        "compound amount",
    ],

    "Time Speed Distance": [
        "time speed distance",
        "speed distance time",
        "speed",
        "distance",
        "km/h",
        "kilometers per hour",
        "kilometres per hour",
    ],

    "Number System": [
        "number system",
        "natural number",
        "whole number",
        "integer",
        "prime number",
        "divisibility",
        "remainder",
        "hcf",
        "lcm",
    ],

    "Probability": [
        "probability",
        "event",
        "outcome",
        "sample space",
    ],

    "Permutation and Combination": [
        "permutation",
        "combination",
        "factorial",
        "arrangements",
        "selection",
    ],


    # =====================================================
    # English
    # =====================================================

    "Grammar": [
        "grammar",
        "grammatical",
        "english grammar",
        "parts of speech",
        "noun",
        "pronoun",
        "verb",
        "adjective",
        "adverb",
        "conjunction",
        "interjection",
    ],

    "Tenses": [
        "tense",
        "tenses",
        "present tense",
        "past tense",
        "future tense",
        "present simple",
        "past simple",
        "future simple",
        "present perfect",
        "past perfect",
        "future perfect",
        "present continuous",
        "past continuous",
        "future continuous",
    ],

    "Articles": [
        "articles",
        "use of articles",
        "definite article",
        "indefinite article",
        "a and an",
        "the article",
    ],

    "Subject Verb Agreement": [
        "subject verb agreement",
        "subject-verb agreement",
        "subject and verb",
        "verb agreement",
        "singular subject",
        "plural subject",
    ],

    "Prepositions": [
        "preposition",
        "prepositions",
        "use of prepositions",
        "prepositional phrase",
    ],

    "Active and Passive Voice": [
        "active voice",
        "passive voice",
        "active and passive",
    ],

    "Direct and Indirect Speech": [
        "direct speech",
        "indirect speech",
        "reported speech",
        "direct and indirect",
    ],

    "Synonyms and Antonyms": [
        "synonym",
        "synonyms",
        "antonym",
        "antonyms",
        "opposite meaning",
        "similar meaning",
    ],

    "Vocabulary": [
        "vocabulary",
        "word meaning",
        "meaning of the word",
        "definition",
    ],

    "Reading Comprehension": [
        "reading comprehension",
        "comprehension",
        "passage",
        "read the passage",
    ],

    "Sentence Correction": [
        "sentence correction",
        "correct the sentence",
        "incorrect sentence",
        "grammatically correct",
    ],

    "Sentence Completion": [
        "sentence completion",
        "complete the sentence",
        "fill in the blank",
        "fill the blank",
    ],

    "Error Detection": [
        "error detection",
        "spot the error",
        "identify the error",
        "find the error",
    ],

    "Idioms and Phrases": [
        "idiom",
        "idioms",
        "phrase",
        "phrases",
        "idioms and phrases",
    ],

    "One Word Substitution": [
        "one word substitution",
        "one-word substitution",
        "substitute one word",
    ],
}


# ---------------------------------------------------------
# Heading aliases
# ---------------------------------------------------------

HEADING_ALIASES = {

    # =====================================================
    # Aptitude
    # =====================================================

    "percentages": "Percentages",
    "percentage": "Percentages",

    "profit and loss": "Profit and Loss",
    "profit & loss": "Profit and Loss",

    "ratio and proportion": "Ratio and Proportion",
    "ratio": "Ratio and Proportion",
    "proportion": "Ratio and Proportion",

    "time and work": "Time and Work",

    "averages": "Averages",
    "average": "Averages",

    "simple interest": "Simple Interest",

    "compound interest": "Compound Interest",

    "time speed distance": "Time Speed Distance",
    "time, speed and distance": "Time Speed Distance",

    "number system": "Number System",

    "probability": "Probability",

    "permutation and combination": (
        "Permutation and Combination"
    ),


    # =====================================================
    # English
    # =====================================================

    "english grammar": "Grammar",
    "grammar": "Grammar",

    "subject verb agreement": (
        "Subject Verb Agreement"
    ),
    "subject-verb agreement": (
        "Subject Verb Agreement"
    ),

    "tenses": "Tenses",
    "tense": "Tenses",

    "articles": "Articles",
    "article": "Articles",

    "prepositions": "Prepositions",
    "preposition": "Prepositions",

    "active and passive voice": (
        "Active and Passive Voice"
    ),
    "active voice": "Active and Passive Voice",
    "passive voice": "Active and Passive Voice",

    "direct and indirect speech": (
        "Direct and Indirect Speech"
    ),
    "direct speech": "Direct and Indirect Speech",
    "indirect speech": "Direct and Indirect Speech",
    "reported speech": "Direct and Indirect Speech",

    "synonyms and antonyms": (
        "Synonyms and Antonyms"
    ),
    "synonyms": "Synonyms and Antonyms",
    "antonyms": "Synonyms and Antonyms",

    "vocabulary": "Vocabulary",
    "word meaning": "Vocabulary",

    "reading comprehension": (
        "Reading Comprehension"
    ),
    "comprehension": "Reading Comprehension",

    "sentence correction": "Sentence Correction",

    "sentence completion": "Sentence Completion",

    "error detection": "Error Detection",
    "spot the error": "Error Detection",

    "idioms and phrases": "Idioms and Phrases",
    "idioms": "Idioms and Phrases",
    "phrases": "Idioms and Phrases",

    "one word substitution": (
        "One Word Substitution"
    ),
    "one-word substitution": (
        "One Word Substitution"
    ),


    # =====================================================
    # DSA
    # =====================================================

    "arrays": "Arrays",
    "array": "Arrays",

    "binary search": "Binary Search",

    "linked lists": "Linked Lists",
    "linked list": "Linked Lists",

    "stacks": "Stacks",
    "stack": "Stacks",

    "queues": "Queues",
    "queue": "Queues",

    "sorting": "Sorting",
}


# ---------------------------------------------------------
# Clean text
# ---------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Clean unnecessary whitespace while preserving
    paragraph boundaries.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
    ]

    cleaned_lines = []
    previous_blank = False

    for line in lines:

        if not line:

            if not previous_blank:
                cleaned_lines.append("")

            previous_blank = True

        else:

            cleaned_lines.append(line)
            previous_blank = False

    return "\n".join(cleaned_lines).strip()


# ---------------------------------------------------------
# Split into logical paragraphs
# ---------------------------------------------------------

def split_into_paragraphs(
    text: str,
) -> list[str]:
    """
    Split the document into logical paragraphs.

    Blank lines are treated as paragraph boundaries.
    """

    text = clean_text(text)

    raw_paragraphs = re.split(
        r"\n\s*\n",
        text,
    )

    paragraphs = []

    for paragraph in raw_paragraphs:

        paragraph = paragraph.strip()

        if paragraph:
            paragraphs.append(paragraph)

    return paragraphs


# ---------------------------------------------------------
# Normalize text for matching
# ---------------------------------------------------------

def normalize_for_matching(
    text: str,
) -> str:
    """
    Normalize text so topic keywords can be matched
    reliably.
    """

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ---------------------------------------------------------
# Detect explicit heading
# ---------------------------------------------------------

def get_heading_topic(
    paragraph: str,
) -> str | None:
    """
    Check whether a paragraph is a known topic heading.

    Example:

        Binary Search

    returns:

        Binary Search
    """

    text = normalize_for_matching(
        paragraph
    )

    if text in HEADING_ALIASES:
        return HEADING_ALIASES[text]

    return None


# ---------------------------------------------------------
# Detect topic from keywords
# ---------------------------------------------------------

def detect_topic_from_keywords(
    paragraph: str,
) -> str | None:
    """
    Detect the most likely topic using topic-specific
    keywords.

    The topic with the highest number of matching
    keywords is selected.
    """

    text = normalize_for_matching(
        paragraph
    )

    topic_scores = {}

    for topic, keywords in TOPIC_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            keyword = keyword.lower()

            if keyword in text:
                score += 1

        if score > 0:
            topic_scores[topic] = score

    if not topic_scores:
        return None

    # Select topic with highest keyword score.
    best_topic = max(
        topic_scores,
        key=topic_scores.get,
    )

    return best_topic


# ---------------------------------------------------------
# Split large topic text safely
# ---------------------------------------------------------

def split_large_text(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """
    Split unusually large topic text without cutting
    words in half.
    """

    words = text.split()

    if not words:
        return []

    chunks = []
    current_words = []

    for word in words:

        candidate = (
            current_words + [word]
        )

        candidate_text = " ".join(
            candidate
        )

        if len(candidate_text) <= chunk_size:

            current_words.append(word)
            continue

        if current_words:

            chunks.append(
                " ".join(current_words)
            )

        # Create word-based overlap.
        overlap_words = []

        if chunk_overlap > 0:

            current_length = 0

            for previous_word in reversed(
                current_words
            ):

                word_length = len(
                    previous_word
                )

                if (
                    current_length
                    + word_length
                    + 1
                    > chunk_overlap
                ):
                    break

                overlap_words.insert(
                    0,
                    previous_word,
                )

                current_length += (
                    word_length + 1
                )

        current_words = (
            overlap_words + [word]
        )

    if current_words:

        chunks.append(
            " ".join(current_words)
        )

    return chunks


# ---------------------------------------------------------
# Main topic-aware chunker
# ---------------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> list[str]:
    """
    Create topic-aware RAG chunks.

    The chunker uses:

    1. Explicit topic headings.
    2. Topic-specific keywords.
    3. Safe word-based splitting for very large topics.

    Explicit headings take priority over keyword detection.
    """

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0."
        )

    if chunk_overlap < 0:
        raise ValueError(
            "chunk_overlap cannot be negative."
        )

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )

    paragraphs = split_into_paragraphs(
        text
    )

    if not paragraphs:
        return []

    # Dictionary containing topic → paragraphs.
    topic_paragraphs = {}

    # Keep track of the current topic.
    current_topic = None

    for paragraph in paragraphs:

        # ---------------------------------------------
        # 1. Check for an explicit heading
        # ---------------------------------------------

        heading_topic = get_heading_topic(
            paragraph
        )

        if heading_topic:

            current_topic = heading_topic

            if (
                current_topic
                not in topic_paragraphs
            ):
                topic_paragraphs[
                    current_topic
                ] = []

            continue

        # ---------------------------------------------
        # 2. Try to detect topic from keywords
        # ---------------------------------------------

        detected_topic = (
            detect_topic_from_keywords(
                paragraph
            )
        )

        # ---------------------------------------------
        # 3. Use keyword topic only when found
        # ---------------------------------------------

        if detected_topic:

            current_topic = detected_topic

        # ---------------------------------------------
        # 4. If no topic detected, keep current topic
        # ---------------------------------------------

        if current_topic is None:

            current_topic = "General"

            if (
                current_topic
                not in topic_paragraphs
            ):
                topic_paragraphs[
                    current_topic
                ] = []

        # ---------------------------------------------
        # 5. Store paragraph under current topic
        # ---------------------------------------------

        if (
            current_topic
            not in topic_paragraphs
        ):
            topic_paragraphs[
                current_topic
            ] = []

        topic_paragraphs[
            current_topic
        ].append(paragraph)

    # -------------------------------------------------
    # Build final chunks
    # -------------------------------------------------

    chunks = []

    for (
        topic,
        paragraphs_for_topic,
    ) in topic_paragraphs.items():

        if not paragraphs_for_topic:
            continue

        topic_text = "\n\n".join(
            paragraphs_for_topic
        )

        # Add topic name to the chunk.
        topic_text = (
            f"Topic: {topic}\n\n"
            f"{topic_text}"
        )

        if len(topic_text) <= chunk_size:

            chunks.append(
                topic_text.strip()
            )

        else:

            large_chunks = split_large_text(
                text=topic_text,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

            chunks.extend(
                large_chunks
            )

    return chunks


# ---------------------------------------------------------
# Read file and chunk
# ---------------------------------------------------------

def read_and_chunk_file(
    file_path: str | Path,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> list[str]:
    """
    Read a knowledge file and create topic-aware
    chunks.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Knowledge file not found: {path}"
        )

    text = path.read_text(
        encoding="utf-8"
    )

    return chunk_text(
        text=text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )