"""Gradio web interface for The Unofficial Guide (endometriosis diet RAG).

Run with:
    python app.py
then open http://localhost:7860
"""

import gradio as gr

from rag.generate import ask


def handle_query(question: str):
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "(no sources used)"
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide — Endometriosis Diet") as demo:
    gr.Markdown(
        "# The Unofficial Guide — Endometriosis Diet\n"
        "Ask about diet and nutrition for endometriosis. Answers are grounded "
        "only in the collected sources (clinical handouts, articles, research, "
        "and patient forums) and the documents used are listed under each answer."
    )
    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. Which foods are recommended to avoid for endometriosis?",
    )
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    gr.Examples(
        examples=[
            "What foods are most often recommended to avoid for endometriosis?",
            "Which foods or nutrients are suggested as beneficial?",
            "Does an anti-inflammatory diet help with endometriosis pain?",
        ],
        inputs=inp,
    )

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
