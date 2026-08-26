from datetime import datetime, timezone

from app.database.connection import db


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    model_provider = db.Column(db.String(50), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)

    policy_id = db.Column(
        db.Integer,
        db.ForeignKey("policies.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    policy = db.relationship(
        "Policy",
        back_populates="applications"
    )

    evaluations = db.relationship(
        "Evaluation",
        back_populates="application",
        cascade="all, delete-orphan"
    )