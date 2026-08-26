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


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True, port=5000)