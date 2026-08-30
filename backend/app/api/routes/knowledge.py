from flask import Blueprint, jsonify, request

from app.models.knowledge_document import KnowledgeDocument
from app.services.rag.document_parser import DocumentParser
from app.services.rag.document_service import DocumentService


knowledge_bp = Blueprint(
    "knowledge",
    __name__,
    url_prefix="/api/knowledge"
)


@knowledge_bp.post("/upload")
def upload_document():

    if "file" not in request.files:
        return jsonify({
            "error": "file is required"
        }), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({
            "error": "Filename is required"
        }), 400

    filename = file.filename

    if not filename.lower().endswith((".pdf", ".txt")):
        return jsonify({
            "error": "Only PDF and TXT files are supported"
        }), 400

    try:

        # ---------------------------------------------------------
        # Prevent duplicate uploads
        # ---------------------------------------------------------

        existing_document = KnowledgeDocument.query.filter_by(
            name=filename
        ).first()

        if existing_document:
            return jsonify({
                "message": "Document already exists",
                "document": {
                    "id": existing_document.id,
                    "name": existing_document.name,
                    "source_type": existing_document.source_type,
                    "chunk_count": len(existing_document.chunks)
                }
            }), 200

        # ---------------------------------------------------------
        # Parse document
        # ---------------------------------------------------------

        content = DocumentParser.parse(
            file,
            filename
        )

        # ---------------------------------------------------------
        # Store document + chunks + embeddings
        # ---------------------------------------------------------

        document, chunks = DocumentService.ingest_text(
            name=filename,
            content=content,
            source_type=(
                "pdf"
                if filename.lower().endswith(".pdf")
                else "text"
            )
        )

        return jsonify({
            "message": "Document uploaded successfully",
            "document": {
                "id": document.id,
                "name": document.name,
                "source_type": document.source_type,
                "chunk_count": len(chunks)
            }
        }), 201

    except Exception as exc:

        return jsonify({
            "error": "Failed to process document",
            "details": str(exc)
        }), 500


@knowledge_bp.get("")
def get_documents():

    documents = KnowledgeDocument.query.order_by(
        KnowledgeDocument.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": document.id,
            "name": document.name,
            "description": document.description,
            "source_type": document.source_type,
            "chunk_count": len(document.chunks),
            "created_at": document.created_at.isoformat()
        }
        for document in documents
    ])