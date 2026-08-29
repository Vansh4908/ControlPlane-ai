import chromadb

from app.services.rag.embedding_service import EmbeddingService


class VectorStore:

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path="./chroma_data"
        )

        self.collection = self.client.get_or_create_collection(
            name="controlplane_knowledge"
        )

        self.embedding_service = EmbeddingService()

    def add_chunks(self, chunks):
        if not chunks:
            return

        documents = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = self.embedding_service.embed_texts(
            documents
        )

        ids = [
            f"chunk_{chunk.id}"
            for chunk in chunks
        ]

        metadatas = [
            {
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index
            }
            for chunk in chunks
        ]

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(self, query, top_k=3):

        query_embedding = self.embedding_service.embed_text(
            query
        )

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )