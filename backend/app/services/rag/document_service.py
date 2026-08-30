from app.database.connection import db
from app.models.knowledge_document import KnowledgeDocument
from app.models.knowledge_chunk import KnowledgeChunk
from app.services.rag.vector_store import VectorStore

class DocumentService:

    CHUNK_SIZE = 1000

    @staticmethod
    def ingest_text(
        name,
        content,
        description=None,
        source_type="text"
    ):

        if not content or not content.strip():
            raise ValueError(
                "Document content cannot be empty"
            )

        document = KnowledgeDocument(
            name=name,
            description=description,
            source_type=source_type
        )

        db.session.add(document)
        db.session.flush()

        chunks = []

        for index in range(
            0,
            len(content),
            DocumentService.CHUNK_SIZE
        ):

            chunk_content = content[
                index:index + DocumentService.CHUNK_SIZE
            ]

            chunk = KnowledgeChunk(
                document_id=document.id,
                content=chunk_content,
                chunk_index=len(chunks)
            )

            db.session.add(chunk)
            chunks.append(chunk)

        db.session.commit()

        vector_store = VectorStore()
        vector_store.add_chunks(chunks)

        return document, chunks