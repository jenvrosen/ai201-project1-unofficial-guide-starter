"""Project-wide paths and chunking constants for the RAG pipeline."""

from pathlib import Path

# Repo root is the parent of the rag/ package directory.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Where the prepared source .txt files live.
DOCUMENTS_DIR = REPO_ROOT / "documents"

# Milestone 3 output: chunks + metadata consumed by Milestone 4.
CHUNKS_PATH = REPO_ROOT / "chunks.json"

# Chunking parameters.
#
# all-MiniLM-L6-v2 (used for embeddings in Milestone 4) truncates input at
# 256 tokens (~1,000-1,200 characters). A 1,000-character chunk fits inside that
# window, so the whole chunk is embedded rather than silently truncated.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# --- Milestone 4: embedding + retrieval ---

# Sentence-transformers model used to embed chunks and queries.
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

# Persistent ChromaDB location and collection name.
CHROMA_DIR = REPO_ROOT / "chroma_db"
COLLECTION_NAME = "endo_chunks"

# Number of chunks retrieved per query (top-k). Starting at 5 per the milestone
# guidance ("start with k=4 or 5") — will be tuned after evaluation.
TOP_K = 5

# --- Milestone 5: generation ---

# Groq chat model used for grounded answer generation.
GROQ_MODEL = "llama-3.3-70b-versatile"

# Retrieval guard: if the best chunk's cosine distance exceeds this, we treat the
# question as out-of-scope and refuse rather than answer from a weak match.
# (Eval showed on-topic hits at ~0.18-0.26 and failures at ~0.6+.)
MAX_DISTANCE = 0.5

# Exact refusal string the system is required to use when context is insufficient.
INSUFFICIENT_INFO_MSG = "I don't have enough information on that."
