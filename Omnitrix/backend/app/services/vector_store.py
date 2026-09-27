import json
import re
from pathlib import Path
from threading import RLock

import numpy as np
from app.ai.embedding_service import EmbeddingService
from app.database.database import SessionLocal
from app.models.resume_vector import ResumeVector


class FaissVectorStore:
    """FAISS search index backed by SQLAlchemy metadata and resume section text.

    Design invariants
    -----------------
    * The same ``EmbeddingService`` instance is used for both indexing and
      querying, so the vector dimension is always consistent.
    * The FAISS index is stored at ``data/resume_vectors_st.faiss`` alongside a
      JSON sidecar (``vector_metadata.json``) that maps FAISS integer IDs back
      to database rows.
    * On startup the index dimension is validated against the embedding model;
      a stale index with the wrong dimension is detected early and raises a
      helpful error rather than silently returning wrong results.
    """

    def __init__(self, index_path: str | None = None):
        self.index_path = Path(
            index_path
            or Path(__file__).resolve().parents[2] / "data" / "resume_vectors_st.faiss"
        )
        self.metadata_path = self.index_path.with_name("vector_metadata.json")
        self.index = None
        self.metadata: dict = {}
        self.embedding_service = EmbeddingService()
        self._loaded = False
        self._lock = RLock()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_faiss(self):
        try:
            import faiss
        except ImportError as exc:
            raise RuntimeError(
                "faiss-cpu is not installed. Run: pip install faiss-cpu"
            ) from exc
        return faiss

    def _ensure_index(self):
        if self._loaded:
            return

        faiss = self._load_faiss()
        dim = self.embedding_service.dimension  # SentenceTransformer dimension

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        if self.index_path.exists():
            loaded = faiss.read_index(str(self.index_path))
            if loaded.d != dim:
                raise ValueError(
                    f"FAISS index dimension ({loaded.d}) does not match the "
                    f"embedding model dimension ({dim}). "
                    "Delete data/resume_vectors_st.faiss and restart to rebuild."
                )
            self.index = loaded
        else:
            self.index = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))

        if self.metadata_path.exists():
            self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))

        self._loaded = True

    def _save_index(self):
        faiss = self._load_faiss()
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        self.metadata_path.write_text(
            json.dumps(self.metadata, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _next_vector_id(self) -> int:
        return max((int(k) for k in self.metadata), default=0) + 1

    def _rebuild_index(self, rows):
        faiss = self._load_faiss()
        dim = self.embedding_service.dimension

        vectors = []
        ids = []
        rebuilt_metadata: dict = {}
        next_vector_id = max((int(k) for k in self.metadata), default=0) + 1

        for row in rows:
            vector = self._vectorize(row.text_content)
            previous = next(
                (item for item in self.metadata.values() if item.get("db_vector_id") == row.id),
                None,
            )
            vector_id = int(previous["vector_id"]) if previous else next_vector_id
            if previous is None:
                next_vector_id += 1
            vectors.append(vector)
            ids.append(vector_id)
            rebuilt_metadata[str(vector_id)] = {
                "vector_id": vector_id,
                "db_vector_id": row.id,
                "user_id": row.user_id,
                "resume_id": row.resume_id,
                "section_type": row.section_name,
                "type": (previous or {}).get("type", "resume_section"),
                "skill_id": (previous or {}).get("skill_id"),
                "source_text": row.text_content,
            }

        self.index = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))
        if vectors:
            vector_array = np.asarray(vectors, dtype="float32")
            self.index.add_with_ids(vector_array, np.asarray(ids, dtype="int64"))
        self.metadata = rebuilt_metadata
        self._loaded = True
        self._save_index()

    def _indexed_ids(self) -> set[int]:
        faiss = self._load_faiss()
        return {
            int(v)
            for v in faiss.vector_to_array(self.index.id_map)
            if v >= 0
        }

    def _vectorize(self, text: str) -> list[float]:
        """Embed *text* using the shared SentenceTransformer model."""
        return self.embedding_service.encode(text)

    # ------------------------------------------------------------------
    # Section splitting
    # ------------------------------------------------------------------

    def _split_sections(self, content: str) -> list[tuple[str, str]]:
        cleaned = re.sub(r"\s+", " ", content).strip()
        if not cleaned:
            return []

        section_groups: dict[str, list[str]] = {
            "summary": [],
            "skills": [],
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "full_resume": [cleaned],
        }

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        current = "summary"
        for line in lines:
            lower = line.lower()
            if any(kw in lower for kw in ["skill", "technical skills", "core competencies"]):
                current = "skills"
            elif any(kw in lower for kw in ["experience", "work history", "employment"]):
                current = "experience"
            elif any(kw in lower for kw in ["education", "degree", "university", "school"]):
                current = "education"
            elif any(kw in lower for kw in ["project", "projects"]):
                current = "projects"
            elif any(kw in lower for kw in ["certification", "certifications"]):
                current = "certifications"
            section_groups[current].append(line)

        result = []
        for section_name, chunk_lines in section_groups.items():
            text = " ".join(chunk_lines).strip()
            if text:
                result.append((section_name, text))
        return result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_document(
        self,
        user_id: int,
        content: str,
        metadata: dict | None = None,
        section_name: str = "full_resume",
        resume_id: int | None = None,
    ) -> dict:
        sections = (
            [(section_name, content)]
            if section_name and section_name != "full_resume"
            else self._split_sections(content)
        )

        stored = []
        with self._lock, SessionLocal() as db:
            self._ensure_index()
            for name, text_chunk in sections:
                vector = self._vectorize(text_chunk)
                doc = (
                    db.query(ResumeVector)
                    .filter(
                        ResumeVector.user_id == user_id,
                        ResumeVector.section_name == name,
                        *(
                            [ResumeVector.resume_id == resume_id]
                            if resume_id is not None
                            else []
                        ),
                    )
                    .first()
                )
                if doc is None:
                    doc = ResumeVector(user_id=user_id, resume_id=resume_id, section_name=name)
                    db.add(doc)

                doc.resume_id = resume_id or doc.resume_id
                doc.text_content = text_chunk
                doc.payload = {**(metadata or {}), "section_name": name}
                db.flush()

                existing = next(
                    (item for item in self.metadata.values() if item.get("db_vector_id") == doc.id),
                    None,
                )
                vector_id = int(existing["vector_id"]) if existing else self._next_vector_id()
                if existing:
                    self.index.remove_ids(np.asarray([vector_id], dtype="int64"))
                self.index.add_with_ids(
                    np.asarray([vector], dtype="float32"),
                    np.asarray([vector_id], dtype="int64"),
                )
                self.metadata[str(vector_id)] = {
                    "vector_id": vector_id,
                    "db_vector_id": doc.id,
                    "user_id": user_id,
                    "resume_id": resume_id,
                    "section_type": name,
                    "type": (metadata or {}).get("type", "resume_section"),
                    "skill_id": (metadata or {}).get("skill_id"),
                    "source_text": text_chunk,
                }
                stored.append({"section_name": name, "metadata": doc.payload})

            db.commit()
            self._save_index()
        return {"user_id": user_id, "sections": stored}

    def search(
        self,
        query: str,
        top_k: int = 5,
        section_name: str | None = None,
        user_id: int | None = None,
        resume_id: int | None = None,
    ) -> list[dict]:
        # Embed the query with the *same* model used at index time
        query_vector = self._vectorize(query)
        with self._lock, SessionLocal() as db:
            self._ensure_index()
            rows = db.query(ResumeVector).all()
            indexed_ids = self._indexed_ids()
            if (
                len(indexed_ids) != len(rows)
                or len(self.metadata) != len(rows)
                or {item.get("db_vector_id") for item in self.metadata.values()}
                != {row.id for row in rows}
            ):
                self._rebuild_index(rows)

            search_limit = max(top_k * 3, top_k)
            distances, ids = self.index.search(
                np.asarray([query_vector], dtype="float32"),
                min(search_limit, self.index.ntotal) if self.index.ntotal else 1,
            )
            rows_by_id = {row.id: row for row in rows}
            results = []
            for similarity, vector_id in zip(distances[0], ids[0]):
                meta = self.metadata.get(str(int(vector_id)))
                if meta is None:
                    continue
                row = rows_by_id.get(int(meta["db_vector_id"]))
                if row is None:
                    continue
                if section_name and row.section_name != section_name:
                    continue
                if user_id is not None and row.user_id != user_id:
                    continue
                if resume_id is not None and row.resume_id != resume_id:
                    continue
                results.append({
                    "user_id": row.user_id,
                    "section_name": row.section_name,
                    "text": row.text_content,
                    "metadata": row.payload or {},
                    "vector_id": meta["vector_id"],
                    "similarity": float(similarity),
                })
                if len(results) == top_k:
                    break
        return results


def _build_similarity_result(candidate_skills, job_requirements):
    candidate = {skill.lower().strip() for skill in candidate_skills}
    requirements = {skill.lower().strip() for skill in job_requirements}
    overlap = sorted(candidate.intersection(requirements))
    missing = sorted(requirements - candidate)
    extra = sorted(candidate - requirements)
    if requirements:
        score = round((len(overlap) / len(requirements)) * 100, 2)
    else:
        score = 0.0
    return {
        "match_score": score,
        "matched_skills": overlap,
        "missing_skills": missing,
        "extra_skills": extra,
    }


# Aliases kept for backward compatibility with existing imports
PostgresVectorStore = FaissVectorStore
InMemoryVectorStore = FaissVectorStore
