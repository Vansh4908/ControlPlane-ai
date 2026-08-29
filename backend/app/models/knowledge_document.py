from datetime import datetime, timezone

from app.database.connection import db


class KnowledgeDocument(db.Model):
    __tablename__ = "knowledge_documents"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    source_type = db.Column(
        db.String(50),
        nullable=False,
        default="document"
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    chunks = db.relationship(
        "KnowledgeChunk",
        back_populates="document",
        cascade="all, delete-orphan"
    )