"""Stage 5 — grounded answer generation with Groq.

Grounding is enforced in two ways that do NOT rely on the model behaving:
1. A retrieval distance guard: if no retrieved chunk is close enough to the
   query, we refuse *before* ever calling the LLM.
2. Source attribution is built programmatically from the retrieved chunks'
   metadata, not parsed out of the model's text — so the "Retrieved from" list is
   always accurate even if the model forgets to cite.

The system prompt additionally instructs the model to use only the supplied
context and to emit the exact refusal string when the context is insufficient.
"""

import os

from dotenv import load_dotenv
from groq import Groq

from .config import (
    GROQ_MODEL,
    INSUFFICIENT_INFO_MSG,
    MAX_DISTANCE,
    TOP_K,
)
from .retrieve import RetrievedChunk, retrieve

load_dotenv()  # read GROQ_API_KEY from .env

_client: Groq | None = None

SYSTEM_PROMPT = f"""You answer questions about endometriosis diet and nutrition \
using ONLY the numbered source excerpts provided in the user message.

Strict rules:
- Use ONLY the information in the provided CONTEXT. Do not use any prior or \
outside knowledge, and do not guess.
- If the CONTEXT does not contain enough information to answer the question, \
reply with exactly this sentence and nothing else: "{INSUFFICIENT_INFO_MSG}"
- Do not invent facts, numbers, foods, or studies that are not in the CONTEXT.
- Cite the source name(s) you used inline, e.g. "(source: Healthline)".
- When a source is a personal/anecdotal account (Reddit), label it as a personal \
experience rather than clinical evidence.
- If the user asks for personal medical advice, add one sentence reminding them \
you are not a substitute for a healthcare professional and that they should \
consult one — then summarize only what the CONTEXT says.
"""


def get_client() -> Groq:
    """Return a cached Groq client built from the GROQ_API_KEY env var."""
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        _client = Groq(api_key=api_key)
    return _client


def _format_context(hits: list[RetrievedChunk]) -> str:
    """Render retrieved chunks as a numbered, source-labeled context block."""
    blocks = []
    for i, h in enumerate(hits, start=1):
        blocks.append(f"[{i}] Source: {h.source}\n{h.text}")
    return "\n\n".join(blocks)


def _format_sources(hits: list[RetrievedChunk]) -> list[str]:
    """Programmatic source list: unique source names (with URL), order preserved."""
    seen: dict[str, str] = {}
    for h in hits:
        if h.source not in seen:
            seen[h.source] = h.url
    return [f"{name} — {url}" if url else name for name, url in seen.items()]


def ask(
    question: str,
    k: int = TOP_K,
    max_distance: float = MAX_DISTANCE,
) -> dict:
    """Answer `question` grounded in retrieved chunks.

    Returns {"answer": str, "sources": list[str]}.
    """
    hits = retrieve(question, k)

    # Guard 1: drop weak matches; if nothing is close enough, refuse up front.
    relevant = [h for h in hits if h.distance <= max_distance]
    if not relevant:
        return {"answer": INSUFFICIENT_INFO_MSG, "sources": []}

    user_message = (
        f"CONTEXT:\n{_format_context(relevant)}\n\n"
        f"QUESTION: {question}"
    )

    response = get_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,  # deterministic, less prone to embellishment
    )
    answer = response.choices[0].message.content.strip()

    # If the model refused, don't attach sources (nothing was actually used).
    if answer == INSUFFICIENT_INFO_MSG:
        return {"answer": answer, "sources": []}

    return {"answer": answer, "sources": _format_sources(relevant)}
