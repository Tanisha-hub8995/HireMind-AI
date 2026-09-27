from pathlib import Path
import json

import faiss
import numpy as np

from app.ai.rag.chunkings import read_and_chunk_file
from app.ai.rag.embeddings import embedding_service


BASE_DATA_DIR = Path("data/rag")
VECTOR_STORE_DIR = Path("vector_store")


SECTIONS = [
    "aptitude",
    "english",
    "dsa",
]


def build_section_index(section: str):
    """
    Build a FAISS index for one assessment section.
    """

    if section not in SECTIONS:
        raise ValueError(
            f"Invalid section: {section}"
        )

    section_dir = BASE_DATA_DIR / section

    if not section_dir.exists():
        raise FileNotFoundError(
            f"RAG data directory not found: {section_dir}"
        )

    all_chunks = []
    metadata = []

    # Read every .txt file in the section
    for file_path in sorted(section_dir.glob("*.txt")):

        chunks = read_and_chunk_file(
            file_path=file_path,
            chunk_size=800,
            chunk_overlap=100,
        )

        for chunk_index, chunk in enumerate(chunks):

            all_chunks.append(chunk)

            metadata.append(
                {
                    "section": section,
                    "source_file": file_path.name,
                    "chunk_index": chunk_index,
                    "text": chunk,
                }
            )

    if not all_chunks:
        raise ValueError(
            f"No chunks found for section: {section}"
        )

    # Convert chunks into embeddings
    embeddings = embedding_service.embed_texts(
        all_chunks
    )

    # FAISS expects float32 vectors
    embeddings = np.asarray(
        embeddings,
        dtype="float32",
    )

    # Number of dimensions
    dimension = embeddings.shape[1]

    # Because embeddings are normalized,
    # inner product works as cosine similarity.
    index = faiss.IndexFlatIP(dimension)

    # Add embeddings to FAISS
    index.add(embeddings)

    # Create vector_store directory
    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Save FAISS index
    index_path = (
        VECTOR_STORE_DIR
        / f"{section}.index"
    )

    faiss.write_index(
        index,
        str(index_path),
    )

    # Save metadata
    metadata_path = (
        VECTOR_STORE_DIR
        / f"{section}_metadata.json"
    )

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Built FAISS index for {section}"
    )
    print(
        f"Chunks indexed: {len(all_chunks)}"
    )
    print(
        f"Index saved to: {index_path}"
    )
    print(
        f"Metadata saved to: {metadata_path}"
    )

    return index, metadata