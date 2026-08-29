from app.database.connection import db
from app.models.knowledge_document import KnowledgeDocument
from app.models.knowledge_chunk import KnowledgeChunk


class DocumentService:

    CHUNK_SIZE = 1000

    @staticmethod
    def ingest_text(
        name,
        content,
        description=None
    ):
        if not content or not content.strip():
            raise ValueError("Document content cannot be empty")

        document = KnowledgeDocument(
            name=name,
            description=description,
            source_type="text"
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

        return document, chunks