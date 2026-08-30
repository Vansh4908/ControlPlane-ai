from app import create_app
from app.database.connection import db
from app.models import (
    Application,
    Policy,
    Evaluation,
    EvaluationResult,
    AuditLog,
    Feedback,
)

app = create_app()


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ControlPlane API"
    }


from sqlalchemy import inspect, text

with app.app_context():
    db.create_all()

    # Migration helper for SQLite columns on evaluations table
    inspector = inspect(db.engine)
    if inspector.has_table("evaluations"):
        existing_cols = {col["name"] for col in inspector.get_columns("evaluations")}
        new_cols = {
            "document_name": "VARCHAR(255)",
            "document_content": "TEXT",
            "edited_response": "TEXT",
            "human_decision": "VARCHAR(30)",
            "has_pii": "BOOLEAN DEFAULT 0",
            "pii_data": "JSON"
        }
        for col_name, col_type in new_cols.items():
            if col_name not in existing_cols:
                try:
                    db.session.execute(text(f"ALTER TABLE evaluations ADD COLUMN {col_name} {col_type}"))
                    db.session.commit()
                except Exception as exc:
                    db.session.rollback()
                    print(f"Migration notice for {col_name}: {exc}")


import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")