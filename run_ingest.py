"""Milestone 3 entry point: load documents, chunk them, save chunks.json.

Usage:
    python run_ingest.py

Loads every .txt in documents/, splits each into overlapping character chunks,
writes the chunks (with source/url metadata) to chunks.json, prints a per-document
stats table, and asserts the chunking invariants from planning.md.
"""

import json

from rag.chunk import chunk_document, chunk_documents
from rag.config import CHUNK_OVERLAP, CHUNK_SIZE, CHUNKS_PATH
from rag.ingest import load_documents


def verify(chunks, documents) -> None:
    """Assert the invariants the chunker is supposed to guarantee."""
    # 1. No chunk exceeds the configured size.
    for c in chunks:
        assert len(c.text) <= CHUNK_SIZE, (
            f"{c.chunk_id} is {len(c.text)} chars (> {CHUNK_SIZE})"
        )

    # 2. Consecutive chunks within a document overlap. Because chunk boundaries
    #    are snapped to sentence/paragraph breaks, the overlap is approximate
    #    rather than an exact char slice, so we check that the start of each
    #    chunk reappears in the previous chunk's text.
    for doc in documents:
        doc_chunks = [c for c in chunks if c.doc_id == doc.doc_id]
        for prev, curr in zip(doc_chunks, doc_chunks[1:]):
            probe = curr.text[:30]
            assert probe and probe in prev.text, (
                f"no overlap between {prev.chunk_id} and {curr.chunk_id}"
            )

    # 3. Every chunk carries attribution metadata.
    for c in chunks:
        assert c.source, f"{c.chunk_id} has empty source"
        assert c.url, f"{c.chunk_id} has empty url"

    # 4. chunk_ids are globally unique.
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids)), "duplicate chunk_id detected"

    print("All invariants passed.")


def main() -> None:
    documents = load_documents()
    chunks = chunk_documents(documents)

    # Per-document stats table.
    print(f"\nLoaded {len(documents)} documents -> {len(chunks)} chunks "
          f"(size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})\n")
    print(f"{'doc_id':<52} {'chars':>7} {'chunks':>7}")
    print("-" * 68)
    for doc in documents:
        n = len(chunk_document(doc))
        print(f"{doc.doc_id:<52} {len(doc.text):>7} {n:>7}")
    print("-" * 68)
    lengths = [len(c.text) for c in chunks]
    print(f"chunk length  min={min(lengths)}  max={max(lengths)}  "
          f"avg={sum(lengths) // len(lengths)}\n")

    verify(chunks, documents)

    CHUNKS_PATH.write_text(
        json.dumps([c.to_dict() for c in chunks], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(chunks)} chunks to {CHUNKS_PATH}")


if __name__ == "__main__":
    main()
