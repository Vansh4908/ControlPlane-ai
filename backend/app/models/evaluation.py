from datetime import datetime, timezone

from app.database.connection import db


class Evaluation(db.Model):
    __tablename__ = "evaluations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id"),
        nullable=False
    )

    prompt = db.Column(
        db.Text,
        nullable=False
    )

    # Original AI response is ALWAYS stored internally.
    # It is only hidden from the user when final_decision == REVIEW/BLOCK.
    ai_response = db.Column(
        db.Text,
        nullable=False
    )

    final_decision = db.Column(
        db.String(30),
        nullable=True
    )

    overall_risk = db.Column(
        db.Float,
        nullable=True
    )

    confidence = db.Column(
        db.Float,
        nullable=True
    )

    latency_ms = db.Column(
        db.Integer,
        nullable=True
    )

    document_name = db.Column(
        db.String(255),
        nullable=True
    )

    document_content = db.Column(
        db.Text,
        nullable=True
    )

    edited_response = db.Column(
        db.Text,
        nullable=True
    )

    human_decision = db.Column(
        db.String(30),
        nullable=True
    )

    has_pii = db.Column(
        db.Boolean,
        default=False
    )

    pii_data = db.Column(
        db.JSON,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    application = db.relationship(
        "Application",
        back_populates="evaluations"
    )

    results = db.relationship(
        "EvaluationResult",
        back_populates="evaluation",
        cascade="all, delete-orphan"
    )

    audit_logs = db.relationship(
        "AuditLog",
        back_populates="evaluation",
        cascade="all, delete-orphan"
    )

    feedback = db.relationship(
        "Feedback",
        back_populates="evaluation",
        cascade="all, delete-orphan",
        uselist=False
    )


class EvaluationResult(db.Model):
    __tablename__ = "evaluation_results"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    evaluation_id = db.Column(
        db.Integer,
        db.ForeignKey("evaluations.id"),
        nullable=False
    )

    detector_type = db.Column(
        db.String(50),
        nullable=False
    )

    detector_name = db.Column(
        db.String(100),
        nullable=True
    )

    score = db.Column(
        db.Float,
        nullable=True
    )

    confidence = db.Column(
        db.Float,
        nullable=True
    )

    reason = db.Column(
        db.Text,
        nullable=True
    )

    metadata_json = db.Column(
        db.JSON,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    evaluation = db.relationship(
        "Evaluation",
        back_populates="results"
    )