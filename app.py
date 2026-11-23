"""AquaBot - RAG chatbot for ocean / aqua questions (Flask)."""
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from rag.loader import load_chunks
from rag.retriever import Retriever
from rag.generator import generate

load_dotenv()
BASE = os.path.dirname(os.path.abspath(__file__))
TOP_K = int(os.getenv("TOP_K", "4"))
MIN_SCORE = float(os.getenv("MIN_SCORE", "0.085"))

app = Flask(__name__)
chunks = load_chunks(os.path.join(BASE, "data"))
retriever = Retriever(chunks)
print(f"[AquaBot] Loaded {len(chunks)} chunks from {len({c.source for c in chunks})} documents")

GREETINGS = {"hi", "hello", "hey", "hii", "good morning", "good evening", "good afternoon"}
SUGGESTIONS = [
    "Why is seawater salty?",
    "What causes tides?",
    "What is coral bleaching?",
    "How deep is the Mariana Trench?",
    "What is ocean acidification?",
    "How do mangroves protect the coast?",
]
FALLBACK = ("I couldn't find that in my ocean knowledge base. Try asking about oceans, "
            "marine life, currents, tides, coral reefs, pollution, climate or conservation.")


@app.route("/")
def index():
    return render_template("index.html", suggestions=SUGGESTIONS)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    query = (data.get("message") or "").strip()
    if not query:
        return jsonify(error="Please type a question."), 400
    if query.lower().strip("!., ") in GREETINGS:
        return jsonify(answer="Hello! I'm AquaBot. Ask me anything about oceans and aquatic life.",
                       sources=[], mode="greeting", confidence=1.0)

    hits = retriever.search(query, k=TOP_K)
    if not hits or hits[0][1] < MIN_SCORE:
        return jsonify(answer=FALLBACK, sources=[], mode="fallback",
                       confidence=round(hits[0][1], 3) if hits else 0.0)

    answer, mode = generate(retriever, query, hits)
    seen, sources = set(), []
    for c, score in hits:
        if c.source not in seen:
            seen.add(c.source)
            sources.append({"title": c.title, "file": c.source, "score": round(score, 3),
                            "snippet": c.text[:220] + ("..." if len(c.text) > 220 else "")})
    return jsonify(answer=answer, sources=sources, mode=mode, confidence=round(hits[0][1], 3))


@app.route("/api/health")
def health():
    return jsonify(status="ok", chunks=len(chunks), documents=len({c.source for c in chunks}),
                   llm=bool(os.getenv("ANTHROPIC_API_KEY")))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
