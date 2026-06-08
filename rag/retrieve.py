"""Stage 4 — retrieve the most relevant chunks for a query.

Embeds the query with the same model used for the chunks, then asks ChromaDB for
the nearest stored chunks by cosine distance.
"""

from dataclasses import dataclass

from .config import COLLECTION_NAME, TOP_K
from .embed import get_client, get_embedder


@dataclass
class RetrievedChunk:
    """A single retrieval hit, with its text, attribution, and similarity."""

    chunk_id: str
    text: str
    source: str
    url: str
    distance: float          # cosine distance (0 = identical, 2 = opposite)

    @property
    def similarity(self) -> float:
        """Cosine similarity (1 = identical), derived from the distance."""
        return 1.0 - self.distance


def get_collection():
    """Open the persisted Chroma collection built by embed.build_index()."""
    return get_client().get_collection(COLLECTION_NAME)


def retrieve(query: str, k: int = TOP_K) -> list[RetrievedChunk]:
    """Return the top-k chunks most similar to `query`, best match first."""
    query_embedding = get_embedder().encode(
        query, normalize_embeddings=True
    ).tolist()

    collection = get_collection()
    # include= asks Chroma to return the stored text + metadata + distances
    # alongside the matching ids.
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    # Chroma returns parallel lists nested one level per query; we sent one query,
    # so everything is in index [0].
    ids = result["ids"][0]
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    return [
        RetrievedChunk(
            chunk_id=cid,
            text=doc,
            source=meta.get("source", ""),
            url=meta.get("url", ""),
            distance=dist,
        )
        for cid, doc, meta, dist in zip(ids, documents, metadatas, distances)
    ]
