# AquaBot - RAG Chatbot for Aqua / Ocean Questions

A Retrieval-Augmented Generation (RAG) chatbot built with **Flask + pure Python**.
It answers ocean questions *only from its own knowledge base* (12 documents in `data/`)
and shows the source passages for every answer.

## How RAG works here

```
Question -> TF-IDF retriever -> top matching chunks -> generator -> Answer + Sources
                (rag/retriever.py)                    (rag/generator.py)
```

1. **Load**   - `rag/loader.py` reads every `.txt` in `data/` and splits it into ~110-word chunks.
2. **Retrieve** - `rag/retriever.py` turns chunks into TF-IDF vectors and finds the closest ones to your question (cosine similarity).
3. **Generate** - `rag/generator.py`:
   - **Offline mode (default):** picks the best sentences from the retrieved chunks. No internet, no API key.
   - **Claude mode (optional):** if `ANTHROPIC_API_KEY` is set in `.env`, Claude writes the answer using only the retrieved chunks.
4. **Guardrail** - if the best match score is below `MIN_SCORE`, the bot says it does not know instead of guessing.

## Folder structure

```
aqua-ocean-rag/
  app.py               Flask server (routes: /, /api/chat, /api/health)
  rag/                 loader.py, retriever.py, generator.py
  data/                12 ocean knowledge files (.txt)  <- add your own here
  templates/index.html Chat page
  static/              style.css, app.js
  tests/test_rag.py    Retrieval tests
  run.bat              One-click start (Windows)
  setup.ps1            PowerShell start script
  requirements.txt
  .env.example
```

## Run it on Windows (click by click)

**Needs:** Python 3.10 or newer. Check by pressing `Win + R`, typing `cmd`, pressing Enter, then typing `python --version`.
If it is not found, install from python.org and tick **"Add Python to PATH"** on the first screen.

### Option A - easiest (double-click)
1. Right-click the downloaded `aqua-ocean-rag.zip` > **Extract All...** > **Extract**.
2. Open the extracted `aqua-ocean-rag` folder.
3. Double-click **`run.bat`**.
4. Wait for "Starting AquaBot". Your browser opens at `http://127.0.0.1:5000`.
5. Click a suggested question or type your own and press Enter.
6. To stop: click the black window and press `Ctrl + C`.

### Option B - PowerShell
1. Open the extracted folder in File Explorer.
2. Click the address bar, type `powershell`, press Enter.
3. Run these one at a time:
```powershell
python -m pip install --user -r requirements.txt
python app.py
```
4. Open `http://127.0.0.1:5000` in your browser.

### Run the tests (optional)
```powershell
python -m unittest discover tests
```

## Turn on Claude answers (optional)
1. In the project folder, copy `.env.example` and rename the copy to `.env`.
2. Open `.env` in Notepad, paste your key after `ANTHROPIC_API_KEY=`, save.
3. Restart the app. The badge at the top changes from **Offline RAG** to **Claude + RAG**.

## Add your own knowledge
1. Create a new `.txt` file in `data/`, e.g. `13_marine_biology.txt`.
2. **First line = title.** Then write paragraphs separated by a blank line.
3. Restart the app (it re-indexes on start).

## Settings (`.env`)
| Name | Default | Meaning |
|---|---|---|
| TOP_K | 4 | How many chunks to retrieve |
| MIN_SCORE | 0.085 | Below this score the bot says "I don't know". Raise it to be stricter. |

## Known limits
- Offline mode matches **words**, not meaning, so unusual phrasing may miss. Claude mode answers more naturally.
- A very short off-topic question that shares a word with the data (e.g. "weather") can still match; Claude mode handles this better because it is told to answer only from context.

## Ideas to extend
- If you get 'Application Control policy has blocked' errors, always use `python -m pip ...` (not `pip`) and avoid compiled packages.
- Swap TF-IDF for sentence-transformers embeddings + FAISS.
- Add PDF loading (`pypdf`) to `rag/loader.py`.
- Add chat history and streaming replies.
