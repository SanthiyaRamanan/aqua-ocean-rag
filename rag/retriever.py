"""Pure-Python TF-IDF retriever.
No numpy / scipy / scikit-learn needed, so it also runs on locked-down Windows PCs
where Application Control blocks compiled (.dll / .pyd) files.
"""
import math
import re
from collections import Counter

_STOP = set("""a an the and or of to in on for with is are was were be been being what which who whom
how why when where do does did can could should would will shall may might about tell me please
explain describe give i you it its this that these those as at by from into than then so such
world there their they them he she we our your my not no yes any some more most much many very
today""".split())


def _stem(w):
    """Light suffix stripper: reefs->reef, coastal->coast, protecting->protect."""
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    for suf in ("ing", "ed", "al", "es", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf) and not w.endswith("ss"):
            return w[: -len(suf)]
    return w


def tokenize(text):
    return [_stem(w) for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in _STOP]


def _features(text):
    """Unigrams + bigrams (like sklearn ngram_range=(1,2))."""
    toks = tokenize(text)
    return toks + [a + " " + b for a, b in zip(toks, toks[1:])]


def _split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) > 3]


class Retriever:
    def __init__(self, chunks):
        self.chunks = chunks
        docs = [_features(c.title + ". " + c.text) for c in chunks]
        n = len(docs)
        df = Counter()
        for d in docs:
            df.update(set(d))
        # smoothed idf, same formula scikit-learn uses
        self.idf = {t: math.log((1 + n) / (1 + f)) + 1.0 for t, f in df.items()}
        self.vectors = [self._vectorize_tokens(d) for d in docs]

    def _vectorize_tokens(self, tokens):
        tf = Counter(t for t in tokens if t in self.idf)
        vec = {t: (1.0 + math.log(c)) * self.idf[t] for t, c in tf.items()}
        norm = math.sqrt(sum(v * v for v in vec.values()))
        return {t: v / norm for t, v in vec.items()} if norm else {}

    def vectorize(self, text):
        return self._vectorize_tokens(_features(text))

    @staticmethod
    def _cos(a, b):
        if len(a) > len(b):
            a, b = b, a
        return sum(v * b.get(t, 0.0) for t, v in a.items())

    def search(self, query, k=4):
        q = self.vectorize(query)
        scores = [self._cos(q, v) for v in self.vectors]
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [(self.chunks[i], scores[i]) for i in order if scores[i] > 0]

    def best_sentences(self, query, hits, n=3, rel=0.45):
        """Best n sentences across the retrieved chunks, dropping weak ones."""
        q = self.vectorize(query)
        cand = []  # (score, chunk_rank, position, sentence)
        for rank, (chunk, cscore) in enumerate(hits[:3]):
            if rank > 0 and cscore < 0.8 * hits[0][1]:
                continue
            for pos, sent in enumerate(_split_sentences(chunk.text)):
                v = self._cos(q, self.vectorize(sent))
                if v > 0:
                    cand.append((v, rank, pos, sent))
        if not cand:
            return [hits[0][0].text[:300]]
        top = max(c[0] for c in cand)
        keep = sorted([c for c in cand if c[0] >= rel * top], reverse=True)[:n]
        seen, out = set(), []
        for _, _, _, t in sorted(keep, key=lambda c: (c[1], c[2])):
            if t not in seen:
                seen.add(t)
                out.append(t)
        return out
