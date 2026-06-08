"""Load source documents and parse their Source:/URL: headers.

Each file in documents/ is expected to start with header lines::

    Source: <human-readable name>
    URL: <original url>

    <body text...>

Parsing is tolerant: the header lines may be missing or accompanied by an extra
note line (e.g. "Retrieved via Reddit archive API ..."). Anything that isn't a
recognized header line is treated as body text.
"""

import re
from pathlib import Path

from .config import DOCUMENTS_DIR
from .models import Document

_SOURCE_RE = re.compile(r"^\s*Source:\s*(.+?)\s*$")
_URL_RE = re.compile(r"^\s*URL:\s*(\S.*?)\s*$")

# Leading lines that belong to the header block, not the body.
_HEADER_PREFIXES = ("Source:", "URL:", "Retrieved via")


def parse_header(raw: str) -> tuple[str, str, str]:
    """Return (source, url, body) for a raw file's contents.

    source/url fall back to "" when their header line is absent.
    """
    source = ""
    url = ""

    # Find the first Source:/URL: lines anywhere near the top.
    for line in raw.splitlines():
        if not source:
            m = _SOURCE_RE.match(line)
            if m:
                source = m.group(1)
        if not url:
            m = _URL_RE.match(line)
            if m:
                url = m.group(1)
        if source and url:
            break

    # Build the body by dropping the leading header block (header lines and any
    # blank lines among them). Stop at the first real content line.
    lines = raw.splitlines()
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "" or stripped.startswith(_HEADER_PREFIXES):
            start = i + 1
            continue
        break
    body = "\n".join(lines[start:])

    return source, url, body


def clean_text(text: str) -> str:
    """Light cleanup: drop separator rules, collapse blank runs, trim whitespace.

    Preserves words, paragraph breaks, and Reddit-style leading indentation.
    """
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        # Drop pure separator rules (e.g. "====...", "----...") used as visual
        # dividers in the Reddit exports — they carry no meaning for retrieval.
        if len(stripped) >= 3 and set(stripped) <= {"=", "-"}:
            continue
        lines.append(line.rstrip())  # keep leading indentation, trim trailing
    text = "\n".join(lines)
    # Collapse 3+ consecutive newlines down to a single blank line.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_document(path: Path) -> Document:
    """Read one .txt file into a Document with parsed metadata."""
    raw = path.read_text(encoding="utf-8")
    source, url, body = parse_header(raw)
    doc_id = path.stem
    return Document(
        doc_id=doc_id,
        source=source or doc_id,  # fall back to filename stem
        url=url,
        text=clean_text(body),
        path=str(path),
    )


def load_documents(documents_dir: Path = DOCUMENTS_DIR) -> list[Document]:
    """Load every .txt file in documents_dir, sorted by filename."""
    paths = sorted(p for p in documents_dir.glob("*.txt"))
    return [load_document(p) for p in paths]
