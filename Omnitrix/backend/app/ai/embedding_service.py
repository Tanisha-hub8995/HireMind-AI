import os

import numpy as np


class EmbeddingService:
    """SentenceTransformer embedding provider used by both FAISS indexing and queries.

    The same model instance is used for both adding documents to the index and
    querying it, guaranteeing that the embedding dimension is always consistent.

    Model is loaded lazily on first use so that import time stays fast.
    """

    def __init__(self):
        self.model_name = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self._model = None

    def _load(self):
        """Lazily load SentenceTransformer model.  Raises RuntimeError on failure."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise RuntimeError(
                    "sentence-transformers is not installed. "
                    "Run: pip install sentence-transformers"
                ) from exc
            self._model = SentenceTransformer(self.model_name)
        return self._model

    @property
    def dimension(self) -> int:
        """Return the embedding dimension of the loaded model."""
        return self._load().get_sentence_embedding_dimension()

    def encode(self, text: str) -> list[float]:
        """Encode *text* and return a unit-length float32 vector as a Python list."""
        model = self._load()
        vector = model.encode(text, normalize_embeddings=True)
        return np.asarray(vector, dtype="float32").tolist()
