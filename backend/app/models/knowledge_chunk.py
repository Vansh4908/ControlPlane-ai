from datetime import datetime, timezone

from app.database.connection import db


class KnowledgeChunk(db.Model):
    __tablename__ = "knowledge_chunks"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("knowledge_documents.id"),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    chunk_index = db.Column(
        db.Integer,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    document = db.relationship(
        "KnowledgeDocument",
        back_populates="chunks"
    )