from datetime import datetime, timezone

from app.database.connection import db


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)

    evaluation_id = db.Column(
        db.Integer,
        db.ForeignKey("evaluations.id"),
        nullable=False,
        unique=True
    )

    user_action = db.Column(
        db.String(50),
        nullable=False
    )

    correct_decision = db.Column(
        db.String(30),
        nullable=True
    )

    comment = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    evaluation = db.relationship(
        "Evaluation",
        back_populates="feedback"
    )