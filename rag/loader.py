"""Loads .txt files from /data and splits them into overlapping chunks."""
import os
import re
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    source: str   # file name, e.g. "coral_reefs.txt"
    title: str    # human readable title from the first line
    idx: int      # chunk number within the file


def _split_paragraph_groups(text, max_words=110, overlap_words=25):
    """Group paragraphs into chunks of ~max_words with a small overlap."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, current = [], []
    count = 0
    for p in paragraphs:
        words = p.split()
        if current and count + len(words) > max_words:
            chunk_text = " ".join(current)
            chunks.append(chunk_text)
            tail = chunk_text.split()[-overlap_words:]
            current = [" ".join(tail)]
            count = len(tail)
        current.append(p)
        count += len(words)
    if current:
        chunks.append(" ".join(current))
    return chunks


def load_chunks(data_dir):
    chunks = []
    for name in sorted(os.listdir(data_dir)):
        if not name.lower().endswith(".txt"):
            continue
        path = os.path.join(data_dir, name)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        if not raw:
            continue
        lines = raw.splitlines()
        title = lines[0].strip().lstrip("#").strip()
        body = "\n".join(lines[1:]).strip()
        for i, piece in enumerate(_split_paragraph_groups(body)):
            chunks.append(Chunk(text=piece, source=name, title=title, idx=i))
    return chunks
