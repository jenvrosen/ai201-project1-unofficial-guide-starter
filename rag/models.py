"""Data structures passed between pipeline stages."""

from dataclasses import dataclass


@dataclass
class Document:
    """A single source document loaded from the documents/ folder."""

    doc_id: str   # filename stem, e.g. "02_cleveland_clinic_endometriosis_diet"
    source: str   # human-readable source name from the "Source:" header line
    url: str      # original URL from the "URL:" header line
    text: str     # cleaned body text (header lines removed)
    path: str     # absolute path to the file on disk


@dataclass
class Chunk:
    """A fixed-size slice of a document's text, with carried-over metadata."""

    chunk_id: str      # f"{doc_id}#{chunk_index}", globally unique
    doc_id: str
    source: str
    url: str
    chunk_index: int   # 0-based position of this chunk within its document
    text: str

    def to_dict(self) -> dict:
        """Plain dict for JSON serialization (chunks.json)."""
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "source": self.source,
            "url": self.url,
            "chunk_index": self.chunk_index,
            "text": self.text,
        }
