"""Stage 3 — embed chunks with all-MiniLM-L6-v2 and store them in ChromaDB.

We embed the text ourselves with sentence-transformers (rather than letting
Chroma call an embedding model implicitly) so the pipeline is explicit: load
chunks -> encode -> store vectors + metadata. The query side (retrieve.py) reuses
the same `get_embedder()` so chunks and queries always live in the same space.
"""

import json

import chromadb
from sentence_transformers import SentenceTransformer

from .chunk import chunk_documents
from .config import (
    CHROMA_DIR,
    CHUNKS_PATH,
    COLLECTION_NAME,
    EMBED_MODEL_NAME,
)
from .ingest import load_documents

# Module-level caches so the model and DB client are created once per process.
_embedder: SentenceTransformer | None = None
_client: chromadb.ClientAPI | None = None


def get_embedder() -> SentenceTransformer:
    """Return a cached SentenceTransformer for EMBED_MODEL_NAME."""
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL_NAME)
    return _embedder


def get_client() -> chromadb.ClientAPI:
    """Return a cached ChromaDB client that persists to CHROMA_DIR on disk."""
    global _client
    if _client is None:
        # PersistentClient writes the collection to disk so the index survives
        # between runs (Milestone 5 reuses it without re-embedding).
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _client


def load_chunks() -> list[dict]:
    """Load chunk dicts from chunks.json, or rebuild them from the pipeline."""
    if CHUNKS_PATH.exists():
        return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    # Fallback: run ingestion + chunking in-memory if chunks.json is missing.
    return [c.to_dict() for c in chunk_documents(load_documents())]


def build_index(batch_size: int = 64):
    """Embed every chunk and (re)build the Chroma collection. Returns it.

    The collection is dropped and recreated so re-running this is idempotent
    (no duplicate ids, no stale chunks from a previous corpus).
    """
    chunks = load_chunks()
    if not chunks:
        raise RuntimeError("No chunks found. Run `python run_ingest.py` first.")

    client = get_client()
    # Start clean: delete the old collection if it exists.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # collection didn't exist yet
    # hnsw:space="cosine" tells Chroma to rank by cosine distance, which matches
    # how sentence-transformer embeddings are meant to be compared.
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    embedder = get_embedder()
    texts = [c["text"] for c in chunks]
    # normalize_embeddings=True gives unit vectors, which pairs correctly with
    # cosine distance.
    embeddings = embedder.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    ids = [c["chunk_id"] for c in chunks]
    metadatas = [
        {
            "source": c["source"],
            "url": c["url"],
            "doc_id": c["doc_id"],
            "chunk_index": c["chunk_index"],
        }
        for c in chunks
    ]

    # Add in batches (Chroma handles large adds, but batching keeps memory low).
    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        collection.add(
            ids=ids[start:end],
            documents=texts[start:end],
            embeddings=[e.tolist() for e in embeddings[start:end]],
            metadatas=metadatas[start:end],
        )

    return collection
