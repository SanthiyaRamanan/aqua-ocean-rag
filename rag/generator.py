"""Turns retrieved chunks into an answer.
Mode 1 (default, offline): extractive answer built from the best sentences.
Mode 2 (optional): if ANTHROPIC_API_KEY is set, Claude writes the answer from the context.
"""
import os

SYSTEM_PROMPT = (
    "You are AquaBot, a friendly assistant that answers questions about oceans, seas, "
    "marine life, water and aquatic science. Answer ONLY using the provided context. "
    "If the context does not contain the answer, say you don't have that in your knowledge base. "
    "Keep answers clear and concise (under 150 words)."
)


def extractive_answer(retriever, query, hits):
    return " ".join(retriever.best_sentences(query, hits))


def llm_answer(query, hits):
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    context = "\n\n".join(f"[{i+1}] ({c.title}) {c.text}" for i, (c, _) in enumerate(hits))
    msg = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5"),
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "text", None)).strip()


def generate(retriever, query, hits):
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            return llm_answer(query, hits), "llm"
        except Exception as e:  # fall back gracefully
            print("LLM error, falling back to extractive:", e)
    return extractive_answer(retriever, query, hits), "extractive"
