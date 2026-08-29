from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def embed_text(self, text):
        return self.model.encode(
            text,
            normalize_embeddings=True
        ).tolist()

    def embed_texts(self, texts):
        return self.model.encode(
            texts,
            normalize_embeddings=True
        ).tolist()