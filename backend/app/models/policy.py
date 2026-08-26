from datetime import datetime, timezone

from app.database.connection import db


class Policy(db.Model):
    __tablename__ = "policies"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    pii_action = db.Column(
        db.String(30),
        nullable=False,
        default="BLOCK"
    )

    hallucination_action = db.Column(
        db.String(30),
        nullable=False,
        default="FLAG"
    )

    bias_action = db.Column(
        db.String(30),
        nullable=False,
        default="EDIT"
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    applications = db.relationship(
        "Application",
        back_populates="policy"
    )