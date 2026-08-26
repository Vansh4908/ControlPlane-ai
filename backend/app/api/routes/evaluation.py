from flask import Blueprint, jsonify, request

from app.database.connection import db
from app.models.application import Application
from app.models.evaluation import Evaluation


evaluation_bp = Blueprint(
    "evaluation",
    __name__,
    url_prefix="/api/evaluations"
)


@evaluation_bp.post("")
def create_evaluation():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    application_id = data.get("application_id")
    prompt = data.get("prompt")

    if not application_id:
        return jsonify({
            "error": "application_id is required"
        }), 400

    if not prompt or not prompt.strip():
        return jsonify({
            "error": "prompt is required"
        }), 400

    application = Application.query.get(application_id)

    if not application:
        return jsonify({
            "error": "Application not found"
        }), 404

    # Temporary response.
    # Day 2 will replace this with the actual target LLM call.
    ai_response = "Evaluation pipeline connected successfully."

    evaluation = Evaluation(
        application_id=application.id,
        prompt=prompt,
        ai_response=ai_response
    )

    db.session.add(evaluation)
    db.session.commit()

    return jsonify({
        "message": "Evaluation created successfully",
        "evaluation": {
            "id": evaluation.id,
            "application_id": evaluation.application_id,
            "prompt": evaluation.prompt,
            "ai_response": evaluation.ai_response,
            "final_decision": evaluation.final_decision,
            "overall_risk": evaluation.overall_risk,
            "confidence": evaluation.confidence,
            "latency_ms": evaluation.latency_ms,
        }
    }), 201