"""Milestone 4 entry point: embed all chunks and build the ChromaDB index.

Usage:
    python run_embed.py

Requires chunks.json (run `python run_ingest.py` first).
"""

from rag.embed import build_index


def main() -> None:
    print("Embedding chunks with all-MiniLM-L6-v2 and building ChromaDB index...")
    collection = build_index()
    print(f"\nDone. Collection '{collection.name}' now holds "
          f"{collection.count()} chunks.")


if __name__ == "__main__":
    main()
