import math
import re
from collections import Counter


class EmbeddingService:

    def __init__(self, vector_dim=384):
        self.vector_dim = vector_dim

    def embed_text(self, text):
        if not text:
            return [0.0] * self.vector_dim

        words = re.findall(r"\w+", text.lower())
        if not words:
            return [0.0] * self.vector_dim

        vec = [0.0] * self.vector_dim
        counts = Counter(words)

        for word, count in counts.items():
            idx = abs(hash(word)) % self.vector_dim
            vec[idx] += count

        magnitude = math.sqrt(sum(v * v for v in vec))
        if magnitude > 0:
            vec = [v / magnitude for v in vec]

        return vec

    def embed_texts(self, texts):
        return [self.embed_text(t) for t in texts]