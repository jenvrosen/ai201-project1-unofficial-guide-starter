# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- This domain covers endometriosis-specific nutrition and dietary strategies for reducing inflammation, pain, and symptom flares. It is hard to find because the evidence is fragmented across clinical handouts, research articles, patient forums, and advocacy sites, while mainstream medical guidance tends to emphasize surgery and pharmaceuticals over diet. -->

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | SSM Health | Endometriosis diet booklet from a clinical women's health provider | https://www.ssmhealth.com/SSMHealth/media/Documents/slucare/services/obstetrics-gynecology-womens-health/endometriosis-diet-booklet.pdf |
| 2 | Cleveland Clinic | Patient-facing overview of diet strategies for endometriosis | https://health.clevelandclinic.org/endometriosis-diet |
| 3 | NCBI PMC | Peer-reviewed article on diet and endometriosis management | https://pmc.ncbi.nlm.nih.gov/articles/PMC9983692/ |
| 4 | Endometriosis Association | Foods to eat and avoid for people with endometriosis | https://endometriosisassn.org/endometriosis-diet-foods-to-eat-and-avoid/ |
| 5 | BC Women's Centre | Pelvic pain and endometriosis diet handout PDF | https://www.bcwomens.ca/Gynecology-Site/Documents/Pelvic%20Pain-Endo/2015Nov_CPP-diet-handout.pdf |
| 6 | Endometriosis UK | Complementary therapy diet booklet for endometriosis | https://www.endometriosis-uk.org/sites/default/files/2025-11/Endometriosis-CompTherapy-16pp-v4.pdf |
| 7 | Reddit r/Endo | Personal report of a diet that resolved endometriosis symptoms | https://www.reddit.com/r/Endo/comments/tw0ovy/diet_that_resolved_my_endometriosis/ |
| 8 | Reddit r/endometriosis | Community discussion of endometriosis diets | https://www.reddit.com/r/endometriosis/comments/1blralx/endo_diets/ |
| 9 | Reddit r/endometriosis | Personal experience of diet reducing endo pain | https://www.reddit.com/r/endometriosis/comments/1my1mfe/my_diet_has_reduced_my_endo_pain_more_than/ |
| 10 | Reddit r/endometriosis | Discussion of anti-inflammatory diet approaches | https://www.reddit.com/r/endometriosis/comments/1qsgi3n/whats_everyones_go_to_anti_inflammatory/ |
| 11 | Endometriosis Foundation | Diet and lifestyle recommendations from an advocacy foundation | https://www.theendometriosisfoundation.org/diet-and-lifestyle |
| 12 | PCRM Nutrition Guide | Clinician-facing nutrition guide for endometriosis | https://nutritionguide.pcrm.org/nutritionguide/view/Nutrition_Guide_for_Clinicians/1342065/all/Endometriosis |
| 13 | Healthline | Consumer article on endometriosis diet and foods to consider | https://www.healthline.com/health/endometriosis/endometriosis-diet |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 1,000 characters

**Overlap:** 200 characters

**Final chunk count:** 259 chunks across 13 documents

**Reasoning:**
The corpus mixes PDFs, clinical handouts, article pages, and forum threads of varied length and structure. I use recursive (boundary-aware) character chunking: it fills chunks up to a target size, then recursively falls back through a hierarchy of separators (paragraph break, then sentence end, then line break) to cut at the nearest natural boundary so each chunk ends on a complete thought instead of mid-word. This is not semantic chunking — break points come from the text's structure, not its meaning. I sized chunks to fit the embedding model: `all-MiniLM-L6-v2` (Retrieval Approach below) truncates input at 256 tokens, roughly 1,000–1,200 characters. A ~1,000-character chunk therefore fits inside that window and is embedded in full — a larger chunk (e.g., 2,500 characters) would be silently truncated, so more than half of each chunk would never reach the vector. The 200-character overlap (a 20% stride, snapped to a boundary) preserves sentence and recommendation continuity across chunk edges, so dietary guidance that spans the end of one chunk and the start of the next is still retrievable. Light preprocessing removes the per-file `Source:`/`URL:` header (kept as metadata for attribution), strips decorative separator rules from the Reddit exports, and collapses the blank-line/whitespace artifacts left over from PDF extraction before chunking.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** 5 (starting value per milestone guidance; to be tuned after evaluation)

**Production tradeoff reflection:**
all-MiniLM-L6-v2 is a fast, cost-effective embedding model with strong semantic relevance for mixed web and PDF text. If cost were not a constraint, I would consider a larger model with better domain accuracy and longer context support to improve retrieval quality for medical and nutrition terminology, while balancing latency and inference cost for user-facing queries.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What are the most consistently recommended foods to avoid for endometriosis across the sources? | Anti-inflammatory sources recommend avoiding red meat, processed foods, refined sugar, and high-fat dairy. |
| 2 | Which foods or nutrients are repeatedly suggested as beneficial for managing endometriosis symptoms? | Sources repeatedly suggest omega-3 rich fish, leafy greens, whole grains, fruits, vegetables, and anti-inflammatory spices such as turmeric. |
| 3 | What role does a low-inflammatory diet play in endometriosis management according to the clinical handouts and research article? | It is recommended as a complementary strategy to reduce pain and symptom flares, not as a cure, by lowering systemic inflammation and stabilizing hormone-related responses. |
| 4 | What type of evidence is represented by the Reddit sources compared to the clinical handouts and research article? | Reddit sources provide personal experiences and anecdotal diet reports, while clinical handouts and the research article provide evidence-based guidelines and peer-reviewed findings. |
| 5 | How should the system answer if a question asks for medical advice beyond the documents? | It should state that it is not a replacement for professional medical advice and encourage consulting a healthcare provider, while summarizing relevant registered document recommendations. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Document noise and format inconsistency: PDFs, web pages, and Reddit posts may extract into text with broken line breaks, headers, and stray markup, which can reduce embedding quality and lead to less accurate retrieval.

2. Mixed evidence quality and source attribution: Clinical handouts and peer-reviewed research are higher-quality than anecdotal Reddit posts, so the system may over-emphasize personal experiences unless retrieval and prompt design explicitly preserve source context and caveats.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │ STAGE 1 — Document Ingestion                                  rag/ingest.py    │
 │   documents/*.txt (13 sources: PDFs, articles, Reddit threads)                 │
 │   load_documents() → parse_header() (Source:/URL: → metadata) → clean_text()   │
 │   ↓ list[Document]                                                             │
 ├──────────────────────────────────────────────────────────────────────────────┤
 │ STAGE 2 — Chunking                                            rag/chunk.py     │
 │   chunk_documents(): boundary-aware split, ~1000 chars / 200 overlap           │
 │   ↓ list[Chunk]  (chunk_id, text, source, url, doc_id, chunk_index)            │
 │   → persisted to chunks.json  (run_ingest.py)                                  │
 ├──────────────────────────────────────────────────────────────────────────────┤
 │ STAGE 3 — Embedding + Vector Store          rag/embed.py  (run_embed.py)       │
 │   SentenceTransformer("all-MiniLM-L6-v2")  embeds each chunk's text            │
 │   → ChromaDB persistent collection "endo_chunks" (cosine)                      │
 │      stores: id=chunk_id, document=text, embedding, metadata={source,url,…}    │
 │   ↓ chroma_db/ on disk                                                         │
 ├──────────────────────────────────────────────────────────────────────────────┤
 │ STAGE 4 — Retrieval                                          rag/retrieve.py   │
 │   retrieve(query, k=6): embed query (same model) → collection.query()          │
 │   ↓ top-6 chunks with text + source/url metadata + distance                    │
 ├──────────────────────────────────────────────────────────────────────────────┤
 │ STAGE 5 — Generation                        rag/generate.py  (Milestone 5)     │
 │   build grounded prompt(query + retrieved chunks) → Groq LLM → cited answer    │
 │   exposed via a CLI / Streamlit interface                                       │
 └──────────────────────────────────────────────────────────────────────────────┘
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

- **Tool:** Claude (Claude Code in the terminal).
- **Input I'll give it:** This planning.md's Documents table and Chunking Strategy section, plus a description of the `/documents` folder (13 pre-extracted `.txt` files, each beginning with a `Source:` line and `URL:` line as a header). I'll tell it the files are already plain text — PDFs were extracted with pypdf, Reddit threads pulled via the PullPush/Arctic-Shift archive APIs — so ingestion only needs to read `.txt`, not parse PDFs or fetch the web.
- **What I expect it to produce:** A `load_documents()` that reads every `.txt` in `/documents` and captures the `Source:`/`URL:` header lines as metadata, and a `chunk_text()` that splits each document into **2,500-character** chunks with **500-character overlap**, returning a list of `{text, source, url, chunk_index}` records.
- **How I'll verify:** Run it on the corpus and confirm: every file is loaded (13 docs), no chunk exceeds 2,500 chars, consecutive chunks share ~500 chars of overlap, and metadata is attached to every chunk. Spot-check that a long source (e.g. the 28-page SSM booklet) produces many chunks and a short one (Cleveland Clinic) produces few.

**Milestone 4 — Embedding and retrieval:**

- **Tool:** Claude.
- **Input I'll give it:** This planning.md's Retrieval Approach section (embedding model `all-MiniLM-L6-v2` via sentence-transformers, **top-k = 6**) and the chunk record shape from Milestone 3.
- **What I expect it to produce:** An `embed_chunks()` that encodes all chunk texts with `all-MiniLM-L6-v2` and stores vectors + metadata in a vector store (e.g. a simple FAISS/NumPy index or Chroma), plus a `retrieve(query, k=6)` that embeds the query and returns the 6 most similar chunks **with their source/url metadata** so answers can be attributed.
- **How I'll verify:** Run each of my 5 evaluation questions through `retrieve()` and confirm the returned chunks are on-topic and come from the sources I'd expect (e.g. Q4 about evidence type should surface both Reddit and clinical/PMC chunks). Confirm exactly 6 chunks come back and each carries its source attribution.

**Milestone 5 — Generation and interface:**

- **Tool:** Claude to write the code; **Groq `llama-3.3-70b-versatile`** (free-tier, OpenAI-compatible, key from `.env`) as the answer-generation model.
- **Input I'll give it:** This planning.md's Evaluation Plan (the 5 test questions + expected answers) and Anticipated Challenges (mixed evidence quality, source attribution). I'll have it write a prompt template that injects the retrieved chunks as context, instructs the model to answer **only** from the provided context, cite sources, distinguish anecdotal (Reddit) from clinical/peer-reviewed evidence, and include the medical-disclaimer behavior described in evaluation Q5.
- **What I expect it to produce:** An `ask(query)` (`rag/generate.py`) that ties retrieval → grounded prompt → Groq response and returns `{answer, sources}`, where the source list is built programmatically from chunk metadata; plus a Gradio interface (`app.py`) where a user types a question and sees the answer with its cited sources.
- **How I'll verify:** Run the evaluation questions end-to-end and compare each response against its expected answer; confirm answers cite sources, that a medical-advice question triggers the disclaimer and a "consult a healthcare provider" message, that an out-of-scope question returns "I don't have enough information on that.", and that the system doesn't fabricate claims absent from the retrieved chunks.
