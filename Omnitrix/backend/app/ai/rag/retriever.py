from pathlib import Path
import json

import faiss
import numpy as np

from app.ai.rag.embeddings import embedding_service


VECTOR_STORE_DIR = Path("vector_store")


class RAGRetriever:
    """
    Retrieve relevant knowledge chunks from FAISS.

    Topic diversity is encouraged using a soft penalty.
    Recently used topics are not forbidden.
    """

    def __init__(self, section: str):
        self.section = section

        self.index_path = (
            VECTOR_STORE_DIR / f"{section}.index"
        )

        self.metadata_path = (
            VECTOR_STORE_DIR
            / f"{section}_metadata.json"
        )

        if not self.index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {self.index_path}"
            )

        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata file not found: "
                f"{self.metadata_path}"
            )

        self.index = faiss.read_index(
            str(self.index_path)
        )

        self.metadata = json.loads(
            self.metadata_path.read_text(
                encoding="utf-8"
            )
        )
        print("DEBUG metadata type:", type(self.metadata))
        print("DEBUG metadata length:", len(self.metadata))
        print("DEBUG FAISS vectors:", self.index.ntotal)
        print("DEBUG embedding service:", embedding_service)

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        used_topics: set[str] | None = None,
    ) -> list[dict]:
        """
        Retrieve relevant knowledge chunks from FAISS.

        Recently used topics receive a soft penalty.

        They are NOT excluded completely.

        Example:

            Time & Work used 3 times
                -> larger penalty

            Ratio & Proportion used 0 times
                -> no penalty

        This encourages topic diversity while still allowing
        the same topic to appear again when it is highly relevant.
        """

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0."
            )

        if used_topics is None:
            used_topics = set()

        # Normalize topic names so that comparisons
        # are case-insensitive.
        used_topics = {
            topic.strip().lower()
            for topic in used_topics
            if topic and topic.strip()
        }

        # --------------------------------------------------
        # Create query embedding
        # --------------------------------------------------

        print("DEBUG: About to create query embedding")
        print("DEBUG query:", query)

        query_embedding = embedding_service.embed_text(query)

        print("DEBUG: Query embedding created")
        print("DEBUG embedding type:", type(query_embedding))
        print("DEBUG embedding shape:", query_embedding.shape)
        print("DEBUG embedding length:", len(query_embedding))

        query_embedding = np.asarray(
            [query_embedding],
            dtype="float32",
        )

        # --------------------------------------------------
        # Retrieve a larger candidate pool
        # --------------------------------------------------
        # We retrieve more candidates than requested so
        # that topic-aware reranking has enough choices.
        # --------------------------------------------------

        candidate_k = min(
            max(top_k * 6, 12),
            self.index.ntotal,
        )

        scores, indices = self.index.search(
            query_embedding,
            candidate_k,
        )

        candidates = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index < 0:
                continue

            if index >= len(self.metadata):
                continue

            metadata = self.metadata[index]

            text = metadata["text"]

            topic = self._extract_topic(text)

            raw_score = float(score)

            # --------------------------------------------------
            # Soft topic penalty
            # --------------------------------------------------
            #
            # FAISS score tells us how relevant the chunk is.
            #
            # We do NOT remove previously used topics.
            #
            # Instead, we slightly reduce their score so that
            # another relevant topic can win when possible.
            # --------------------------------------------------

            topic_penalty = 0.0

            if topic in used_topics:
                topic_penalty = 0.06

            adjusted_score = (
                raw_score - topic_penalty
            )

            candidates.append(
                {
                    "score": raw_score,
                    "adjusted_score": adjusted_score,
                    "section": metadata["section"],
                    "source_file": metadata[
                        "source_file"
                    ],
                    "chunk_index": metadata[
                        "chunk_index"
                    ],
                    "topic": topic,
                    "text": text,
                }
            )

        # --------------------------------------------------
        # Sort using adjusted score
        # --------------------------------------------------

        candidates.sort(
            key=lambda item: item["adjusted_score"],
            reverse=True,
        )

        # --------------------------------------------------
        # Select results
        # --------------------------------------------------
        #
        # We still prefer different topics among the
        # selected chunks.
        #
        # This prevents:
        #
        #   Time & Work
        #   Time & Work
        #   Time & Work
        #
        # from occupying all three RAG results.
        #
        # But this does NOT prevent Time & Work from being
        # selected again in a later question.
        # --------------------------------------------------

        selected = []
        selected_topics = set()

        for candidate in candidates:

            topic = candidate["topic"]

            if topic in selected_topics:
                continue

            selected.append(candidate)
            selected_topics.add(topic)

            if len(selected) >= top_k:
                break

        # --------------------------------------------------
        # Fallback
        # --------------------------------------------------
        #
        # If there are not enough different topics,
        # allow repeated topics.
        # --------------------------------------------------

        if len(selected) < top_k:

            selected_chunk_indices = {
                candidate["chunk_index"]
                for candidate in selected
            }

            for candidate in candidates:

                if (
                    candidate["chunk_index"]
                    in selected_chunk_indices
                ):
                    continue

                selected.append(candidate)

                if len(selected) >= top_k:
                    break

        return selected

    def _extract_topic(
        self,
        text: str,
    ) -> str:
        """
        Extract the topic from the first line
        of a RAG chunk.
        """

        if not text:
            return "unknown"

        first_line = (
            text.splitlines()[0].strip()
        )

        if first_line.lower().startswith(
            "topic:"
        ):
            return first_line[
                len("topic:"):
            ].strip().lower()

        return "unknown"

