"""RAG pipeline package for The Unofficial Guide.

Stage 1-2 (ingestion + chunking) are imported eagerly because they only need the
standard library. Stages 3-5 (embedding, retrieval, generation) pull in heavy or
optional dependencies (chromadb, sentence-transformers, groq), so they are loaded
lazily on first access — this lets `python run_ingest.py` run without those
packages installed.
"""

import importlib

from .chunk import chunk_document, chunk_documents, chunk_text
from .ingest import clean_text, load_document, load_documents, parse_header
from .models import Chunk, Document

# name -> submodule that defines it (loaded on demand via __getattr__)
_LAZY = {
    "build_index": "embed",
    "get_client": "embed",
    "get_embedder": "embed",
    "load_chunks": "embed",
    "retrieve": "retrieve",
    "get_collection": "retrieve",
    "RetrievedChunk": "retrieve",
    "ask": "generate",
}


def __getattr__(name):
    """PEP 562 lazy attribute access for the dependency-heavy submodules."""
    module = _LAZY.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(importlib.import_module(f".{module}", __name__), name)


__all__ = [
    "Document",
    "Chunk",
    "load_documents",
    "load_document",
    "parse_header",
    "clean_text",
    "chunk_text",
    "chunk_document",
    "chunk_documents",
    "build_index",
    "get_client",
    "get_embedder",
    "load_chunks",
    "retrieve",
    "get_collection",
    "RetrievedChunk",
    "ask",
]
