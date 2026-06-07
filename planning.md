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

**Chunk size:** 2,500 characters

**Overlap:** 500 characters

**Reasoning:**
Guides including PDFs, clinical handouts, article pages, and forum posts with varied length and structure. A fixed-size chunk of 2,500 characters keeps segments large enough to capture complete paragraphs and dietary recommendations while still producing enough chunks for retrieval. The 500-character overlap preserves sentence continuity across chunk boundaries, which is important for capturing recommendations and nuanced diet guidance that can span multiple sentences. This fixed character-based approach also simplifies implementation across mixed formats, especially when the text is extracted from PDFs and web pages.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** 6

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

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
