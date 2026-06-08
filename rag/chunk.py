"""Split documents into boundary-aware, overlapping chunks.

Chunks are sized up to `chunk_size` characters but cut at the nearest natural
boundary (paragraph break > sentence end > line break) so that each chunk starts
and ends on a whole thought rather than mid-word. Consecutive chunks overlap by
roughly `overlap` characters, with the overlap start snapped to a clean boundary
too.
"""

import re

from .config import CHUNK_OVERLAP, CHUNK_SIZE
from .models import Chunk, Document

# A sentence end: . ! or ? optionally followed by a closing quote/bracket, then
# whitespace. The match END is the position just after the trailing whitespace.
_SENTENCE_END = re.compile(r"[.!?][)\]\"'’”]*\s")

# Fraction of chunk_size a chunk must reach before we accept an earlier boundary,
# so we don't produce lots of tiny chunks at every paragraph break.
_MIN_FILL_RATIO = 0.6


def _best_break(text: str, lo: int, hi: int) -> int:
    """Pick an end index in (lo, hi] preferring paragraph > sentence > line break.

    Falls back to `hi` (a hard cut) when the window has no natural boundary.
    """
    window = text[lo:hi]
    p = window.rfind("\n\n")
    if p != -1:
        return lo + p + 2
    ends = [m.end() for m in _SENTENCE_END.finditer(window)]
    if ends:
        return lo + ends[-1]
    nl = window.rfind("\n")
    if nl != -1:
        return lo + nl + 1
    return hi


def _overlap_start(text: str, end: int, overlap: int) -> int:
    """Start position for the next chunk: ~`overlap` chars before `end`, snapped
    forward to the earliest clean boundary so the chunk starts cleanly.

    If the earliest boundary sits so close to `end` that it would leave less than
    half the intended overlap, fall back to a raw `overlap`-char step (accepting a
    mid-sentence start) so consecutive chunks always share meaningful context.
    """
    target = max(0, end - overlap)
    window = text[target:end]

    cand = None
    p = window.find("\n\n")
    if p != -1:
        cand = target + p + 2
    if cand is None:
        m = _SENTENCE_END.search(window)
        if m:
            cand = target + m.end()
    if cand is None:
        nl = window.find("\n")
        if nl != -1:
            cand = target + nl + 1

    if cand is None or end - cand < overlap // 2:
        # No usable sentence/paragraph boundary close to the target. Keep a full
        # overlap but at least start on a word boundary (never mid-word).
        sp = text.find(" ", target, end)
        return sp + 1 if sp != -1 else target
    return cand


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into boundary-aware chunks of up to `chunk_size` chars.

    Returns [] for empty text and a single chunk when text fits in one window.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must satisfy 0 <= overlap < chunk_size")

    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    min_fill = int(chunk_size * _MIN_FILL_RATIO)
    n = len(text)
    chunks: list[str] = []
    start = 0
    while start < n:
        hard_end = start + chunk_size
        if hard_end >= n:
            tail = text[start:].strip()
            if tail:
                chunks.append(tail)
            break

        end = _best_break(text, start + min_fill, hard_end)
        if end <= start:
            end = hard_end
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)

        next_start = _overlap_start(text, end, overlap)
        start = next_start if next_start > start else end  # guarantee progress

    return chunks


def chunk_document(
    doc: Document,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    """Chunk a single Document, attaching its metadata to each chunk."""
    pieces = chunk_text(doc.text, chunk_size, overlap)
    return [
        Chunk(
            chunk_id=f"{doc.doc_id}#{i}",
            doc_id=doc.doc_id,
            source=doc.source,
            url=doc.url,
            chunk_index=i,
            text=piece,
        )
        for i, piece in enumerate(pieces)
    ]


def chunk_documents(
    docs: list[Document],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    """Chunk every document and flatten the result into one list."""
    chunks: list[Chunk] = []
    for doc in docs:
        chunks.extend(chunk_document(doc, chunk_size, overlap))
    return chunks
