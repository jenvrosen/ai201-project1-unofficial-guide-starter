# The Unofficial Guide — Endometriosis Diet

A little retrieval system that answers diet and nutrition questions about endometriosis using a set of real sources I collected, and tells you which source each answer came from.

---

## Domain

My system covers diet and nutrition for endometriosis: what foods to avoid, what foods or supplements might help, and how approaches like an anti-inflammatory or low-FODMAP diet fit into managing symptoms.

I went with this topic because diet advice for endo is genuinely hard to pin down in one place. It's scattered across very different kinds of sources: clinic handouts, one research review, patient advocacy sites, and people on Reddit describing what actually worked for them. A lot of the official medical information focuses on surgery and hormone treatment and mostly skips past food, so the diet stuff ends up fragmented and the quality varies a lot. I wanted something that could pull all of it together and still show where each claim came from, so you can see what clinicians recommend right next to what patients actually report.

---

## Document Sources

I collected 13 sources and saved each one as a plain `.txt` file in `documents/`, with a `Source:` and `URL:` line at the top so I could use them for attribution later. The web articles I pulled directly, the PDFs I had to extract with `pypdf`, and the Reddit threads I got through the PullPush / Arctic-Shift archive APIs because Reddit blocks direct downloads.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | SSM Health (SLUCare) — Anti-Inflammatory & Elimination Diet booklet | Clinical handout (PDF) | https://www.ssmhealth.com/SSMHealth/media/Documents/slucare/services/obstetrics-gynecology-womens-health/endometriosis-diet-booklet.pdf |
| 2 | Cleveland Clinic — How To Follow a Healthy Endometriosis Diet | Consumer health article | https://health.clevelandclinic.org/endometriosis-diet |
| 3 | NCBI PMC — Nutrition in the Prevention and Treatment of Endometriosis: A Review | Peer-reviewed article | https://pmc.ncbi.nlm.nih.gov/articles/PMC9983692/ |
| 4 | Endometriosis Association — Foods to Eat and Avoid | Advocacy / educational | https://endometriosisassn.org/endometriosis-diet-foods-to-eat-and-avoid/ |
| 5 | BC Women's Centre — Pelvic Pain & Endometriosis Diet Handout | Clinical handout (PDF) | https://www.bcwomens.ca/Gynecology-Site/Documents/Pelvic%20Pain-Endo/2015Nov_CPP-diet-handout.pdf |
| 6 | Endometriosis UK — Diet and Complementary Therapies booklet | Advocacy handout (PDF) | https://www.endometriosis-uk.org/sites/default/files/2025-11/Endometriosis-CompTherapy-16pp-v4.pdf |
| 7 | Reddit r/Endo — "Diet that resolved my endometriosis" | Patient forum thread | https://www.reddit.com/r/Endo/comments/tw0ovy/diet_that_resolved_my_endometriosis/ |
| 8 | Reddit r/endometriosis — "Endo diets" | Patient forum thread | https://www.reddit.com/r/endometriosis/comments/1blralx/endo_diets/ |
| 9 | Reddit r/endometriosis — "My diet has reduced my endo pain…" | Patient forum thread | https://www.reddit.com/r/endometriosis/comments/1my1mfe/my_diet_has_reduced_my_endo_pain_more_than/ |
| 10 | Reddit r/endometriosis — "What's everyone's go-to anti-inflammatory…" | Patient forum thread | https://www.reddit.com/r/endometriosis/comments/1qsgi3n/whats_everyones_go_to_anti_inflammatory/ |
| 11 | The Endometriosis Foundation — Diet & Lifestyle | Advocacy / educational | https://www.theendometriosisfoundation.org/diet-and-lifestyle |
| 12 | PCRM — Nutrition Guide for Clinicians: Endometriosis | Clinician reference | https://nutritionguide.pcrm.org/nutritionguide/view/Nutrition_Guide_for_Clinicians/1342065/all/Endometriosis |
| 13 | Healthline — Endometriosis Diet: Foods to Eat and Avoid | Consumer health article | https://www.healthline.com/health/endometriosis/endometriosis-diet |

---

## Chunking Strategy

**Chunk size:** about 1,000 characters

**Overlap:** 200 characters

**Why these choices fit my documents:**

I'm using recursive (boundary-aware) character chunking. My sources are a real mix (long PDFs, article pages, and forum threads), so I wanted chunks that don't cut off in the middle of a sentence. My chunker (`rag/chunk.py`) fills a chunk up to roughly 1,000 characters, then recursively falls back through a hierarchy of separators (paragraph break, then sentence end, then line break) to find the best place to cut, so each chunk ends on a complete thought. It's not semantic chunking, I'm using the text's structure to pick break points, not its meaning.

I landed on ~1,000 characters because of the embedding model. `all-MiniLM-L6-v2` only reads the first 256 tokens of whatever you give it, which is around 1,000–1,200 characters. I originally planned on 2,500-character chunks, but if I'd done that the model would have quietly thrown away more than half of every chunk before embedding it, so I dropped the size to fit. The 200-character overlap is there so a recommendation that lands right on a chunk boundary still shows up in one of the chunks.

Before chunking I do a little cleanup: pull the `Source:`/`URL:` header off into metadata, strip the decorative `====` divider lines out of the Reddit files, and squash the extra blank lines the PDFs leave behind.

**Final chunk count:** 259 chunks across all 13 documents (you can see this when you run `python run_ingest.py`).

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` from sentence-transformers. I store the vectors in a persistent ChromaDB collection using cosine distance, and retrieval pulls back the top 5 chunks per query.

**Production tradeoff reflection:**

I picked MiniLM because it's free, runs locally with no API key or rate limits, and is fast, which is great for a project this size. The downside is the small 256-token window, which is the whole reason my chunks have to be so short. If I were actually shipping this and money wasn't an issue, I'd look at a bigger model like `bge-large-en-v1.5` or a hosted one like OpenAI's `text-embedding-3-large`. Those have much larger context windows, so I could use longer, more natural chunks and not worry about truncation, and they'd probably do better with the medical and nutrition wording. The catch is they cost more and are slower, and the hosted ones mean sending the text off to someone else's server, which feels iffier for health-related content. I didn't need multilingual support here since everything's in English, but that would change if I ever added non-English forums.

---

## Grounded Generation

**System prompt grounding instruction:**

The system prompt in `rag/generate.py` tells the model to use *only* the context I give it, not its own knowledge, and not to guess. If the context doesn't actually answer the question, it has to reply with exactly "I don't have enough information on that." and nothing else. I also tell it not to make up foods, numbers, or studies that aren't in the context, and I run generation at temperature 0 so it stays close to the source.

But I didn't want to rely on the prompt alone, because models don't always listen. So there's also a check before the model even runs: I look at the cosine distance of the best retrieved chunk, and if nothing comes back closer than 0.5, I return the "not enough information" answer without calling the LLM at all. My on-topic questions came back around 0.18–0.26 and the off-topic ones around 0.6+, so 0.5 was a clean cutoff.

**How source attribution is surfaced in the response:**

I do it in code, not by trusting the model. I ask the model to cite source names inline, but the official "Retrieved from" list is built straight from the metadata of the chunks I retrieved (`_format_sources` in `rag/generate.py`), so it's always right even if the model forgets. In the Gradio app that list shows up in its own box under the answer. If the system refuses because nothing was relevant, it doesn't list any sources.

---

## Evaluation Report

I ran all 5 questions end to end through `ask()` (Groq `llama-3.3-70b-versatile`, top-5 retrieval). "Top-hit distance" is the cosine distance of the closest chunk, where lower means closer.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Foods most consistently recommended to **avoid**? | Red meat, processed food, refined sugar, high-fat dairy, alcohol, caffeine, gluten | Listed alcohol, red meat, saturated/trans fat, caffeine, gluten, processed foods, sweets. Cited Healthline, SSM Health, BC Women's, Endometriosis Foundation (dist 0.21) | Relevant | Accurate |
| 2 | Foods/nutrients repeatedly suggested as **beneficial**? | Omega-3 fish, leafy greens, whole grains, fruit/veg, anti-inflammatory spices like turmeric | Listed fiber, leafy greens, omega-3 fish, antioxidant fruit/veg, magnesium, iron, plant protein. Cited Healthline, BC Women's, SSM (dist 0.20) | Relevant | Accurate (it just didn't mention turmeric, since that chunk wasn't in the top 5) |
| 3 | Role of a **low-inflammatory diet** per the clinical/research sources? | A supportive way to lower pain and flares by reducing inflammation, not a cure | Explained the diet reduces inflammation and is supportive rather than curative. Cited Cleveland Clinic, Endometriosis Association, SSM (dist 0.22) | Relevant | Accurate (it leaned on the clinical/consumer sources and didn't directly quote the PMC review) |
| 4 | What **type of evidence** is Reddit vs. the clinical/research sources? | Reddit is personal/anecdotal; the clinical and research sources are evidence-based / peer-reviewed | Refused: "I don't have enough information on that." (top hit only 0.62, past the 0.5 cutoff) | Off-target | Inaccurate — couldn't answer (see Failure Case below) |
| 5 | What should it do if asked for **medical advice** beyond the docs? | Say it isn't a substitute for a professional, tell them to see a provider, and summarize what the docs do say | Gave the disclaimer and said to see a healthcare professional, noted there's no cure and that NSAIDs have limited effect. Cited Endometriosis UK, NCBI PMC (dist 0.34) | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

Overall, 4 of the 5 worked. The three straightforward lookups (1–3) and the medical-advice safety case (5) all came out fine. Question 4 was the one that didn't, and it's the failure I dig into next.

---

## Failure Case Analysis

**Question that failed:** Question 4, "What type of evidence is represented by the Reddit sources compared to the clinical handouts and research article?"

**What the system returned:** It refused with "I don't have enough information on that." The closest chunk it could find was at distance 0.62, way past my 0.5 cutoff and much worse than the 0.18–0.26 I got on the questions that worked. The top match was actually the conflict-of-interest/funding paragraph from the PMC paper, which has nothing to do with the question.

**Root cause (tied to a specific pipeline stage):** This breaks at the retrieval/embedding stage, and it's not really a bug, it's a mismatch between the question and what's in the corpus. Question 4 is asking *about* my documents (compare anecdotal Reddit posts to peer-reviewed research) rather than asking about diet. None of my chunks actually talk about "what kind of evidence Reddit is," so there's nothing for the embedding to match on. The query just ended up near random text that happens to share words like "sources," "evidence," and "research," which is how that funding-disclosure paragraph won. The 0.5 distance check then caught the weak match and made the system refuse instead of inventing a comparison, so at least it failed safely.

**What I would change to fix it:** A different chunk size wouldn't help, because the information it needs isn't in the chunk text, it's in the metadata (which source each chunk came from). I'd tag every chunk with a `source_type` (forum vs. clinical vs. peer-reviewed) during ingestion, and for a "compare the sources" type question I'd grab a balanced set across those types and let the model contrast them, or just answer that kind of question straight from the list of sources instead of using semantic search at all. Plain vector search is the wrong tool for a question about the corpus itself.

---

## Spec Reflection

**One way the spec helped me during implementation:**

Filling out `planning.md` before I wrote code is what saved me from a real mistake. Because I had to write down my chunk size (2,500 characters at the time) and my embedding model on the same page, I noticed they didn't go together: `all-MiniLM-L6-v2` only reads 256 tokens, which is about 1,000 characters, so my 2,500-character chunks would have been chopped off before they were ever embedded. Since I'd committed to both numbers up front, I caught it and shrank the chunks before building anything, instead of finding out after I'd already embedded everything and having to redo it.

**One way my implementation diverged from the spec, and why:**

My plan said fixed 2,500-character chunks with 500 overlap, and I ended up with boundary-aware ~1,000-character chunks with 200 overlap. The size change was because of the token limit above. The bigger change was the approach: once I printed out some sample chunks, the fixed-size version was slicing sentences (and even words) in half, which looked bad and isn't great for retrieval. So I rewrote the chunker to stop at the nearest paragraph or sentence break instead of a hard character count. I went back and updated `planning.md` to match so the two wouldn't disagree.

---

## AI Usage

**Instance 1 — collecting the source documents**

- *What I gave the AI:* my list of 13 source URLs (PDFs, articles, Reddit threads) and asked it to fetch each one and save clean text into `documents/` with a source/URL header.
- *What it produced:* it got the regular web articles fine, but the PDFs came back as unreadable binary and every Reddit link returned a 403 because Reddit blocks bots.
- *What I changed or overrode:* instead of letting it give up, I had it switch methods: extract the PDFs locally with `pypdf`, and pull the Reddit posts and comments from the PullPush / Arctic-Shift archive APIs. I also had it add the missing source/URL headers to two of the PDF files so every chunk would still have attribution.

**Instance 2 — writing `chunk_text()`**

- *What I gave the AI:* my chunking plan (2,500 characters / 500 overlap) and asked it to write `chunk_text()`.
- *What it produced:* a working fixed-size splitter at 2,500/500.
- *What I changed or overrode:* I dropped the size to ~1,000 once I realized the embedding model couldn't handle 2,500, and after looking at the output I had it rewrite the function to break on sentence/paragraph boundaries instead of a hard cut. I updated my planning doc to match.

---

## How to run it

```bash
python run_ingest.py     # build chunks.json (259 chunks)
python run_embed.py      # embed chunks into ChromaDB
python run_query.py      # retrieval check on the eval questions
python app.py            # launch the Gradio app at http://localhost:7860
```

You'll need a `GROQ_API_KEY` in a `.env` file (see `.env.example`).
