from app.services.rag.vector_store import VectorStore


class RetrievalService:

    def __init__(self):
        self.vector_store = VectorStore()

    def retrieve(self, query, top_k=3):
        results = self.vector_store.search(
            query,
            top_k=top_k
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        retrieved = []

        for content, metadata in zip(
            documents,
            metadatas
        ):
            retrieved.append({
                "content": content,
                "document_id": metadata.get("document_id"),
                "chunk_index": metadata.get("chunk_index")
            })

        return retrieved