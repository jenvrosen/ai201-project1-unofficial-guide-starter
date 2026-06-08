"""Milestone 4 retrieval check: query the index from the CLI.

Usage:
    python run_query.py "your question here"     # single query
    python run_query.py                          # runs the 5 eval questions

Prints the top-k retrieved chunks with their source, similarity, and a preview.
"""

import sys

from rag.config import TOP_K
from rag.retrieve import retrieve

# The 5 evaluation questions from planning.md.
EVAL_QUESTIONS = [
    "What are the most consistently recommended foods to avoid for endometriosis?",
    "Which foods or nutrients are repeatedly suggested as beneficial for endometriosis symptoms?",
    "What role does a low-inflammatory diet play in endometriosis management?",
    "What kind of evidence do the Reddit posts provide compared to the clinical sources?",
    "Can you give me medical advice on treating my endometriosis?",
]


def show(query: str, k: int = TOP_K) -> None:
    print("\n" + "#" * 90)
    print(f"QUERY: {query}")
    print("#" * 90)
    for rank, hit in enumerate(retrieve(query, k), start=1):
        preview = " ".join(hit.text.split())[:160]
        print(f"\n[{rank}] distance={hit.distance:.3f}  (cosine sim={hit.similarity:.3f})"
              f"  {hit.source[:52]}")
        print(f"    {hit.chunk_id}")
        print(f"    {preview}...")


def main() -> None:
    if len(sys.argv) > 1:
        show(" ".join(sys.argv[1:]))
    else:
        for q in EVAL_QUESTIONS:
            show(q)


if __name__ == "__main__":
    main()
