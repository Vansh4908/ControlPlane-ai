from app.services.rag.vector_store import VectorStore


class RetrievalService:

    # Chroma's default distance metric is L2.
    # Lower distance = more similar.
    MAX_DISTANCE = 1.0

    def __init__(self):
        self.vector_store = VectorStore()

    def retrieve(self, query, top_k=3):

        results = self.vector_store.search(
            query,
            top_k=top_k
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved = []
        seen = set()

        for content, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):

            if distance > self.MAX_DISTANCE:
                continue

            # Prevent duplicate evidence
            evidence_key = (
                metadata.get("document_id"),
                metadata.get("chunk_index")
            )

            if evidence_key in seen:
                continue

            seen.add(evidence_key)

            retrieved.append({
                "content": content,
                "document_id": metadata.get("document_id"),
                "document_name": metadata.get("document_name"),
                "chunk_index": metadata.get("chunk_index"),
                "distance": round(distance, 4)
            })

        return retrieved