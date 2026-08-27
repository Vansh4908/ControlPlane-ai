from flask import Blueprint, jsonify, request

from app.database.connection import db
from app.models.application import Application
from app.models.evaluation import Evaluation , EvaluationResult
from app.services.llm.groq_service import GroqService
from app.services.judge.gemini_judge import GeminiJudge
from app.services.judge.judge_config import JUDGE_CONFIGS
from app.engines.consensus_engine import ConsensusEngine


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

    if application.model_provider.lower() != "groq":
        return jsonify({
            "error": f"Unsupported model provider: {application.model_provider}"
        }), 400

    try:
        llm = GroqService()
        ai_response = llm.generate_response(prompt,application.model_name)
    except Exception as exc:
        return jsonify({
            "error": "Failed to generate AI response",
            "details": str(exc)
        }), 502

    evaluation = Evaluation(
        application_id=application.id,
        prompt=prompt,
        ai_response=ai_response
    )

    db.session.add(evaluation)
    db.session.commit()

    judge = GeminiJudge()
    evaluation_results = []
    judge_results = []

    for judge_config in JUDGE_CONFIGS:
        try:
            judge_result = judge.evaluate(
                prompt,
                ai_response,
                judge_config["display_name"],
                judge_config["criteria"]
            )
            judge_results.append(judge_result)
        except Exception as exc:
            return jsonify({
                "error": "Judge evaluation failed",
                "judge": judge_config["name"],
                "details": str(exc)
            }), 502

        evaluation_result = EvaluationResult(
            evaluation_id=evaluation.id,
            detector_type="llm_judge",
            detector_name=judge_config["name"],
            score=judge_result.overall_risk,
            confidence=judge_result.confidence,
            reason=judge_result.reason,
            metadata_json={
                "bias_score": judge_result.bias_score,
                "hallucination_score": judge_result.hallucination_score,
                "privacy_score": judge_result.privacy_score,
                "recommendation": judge_result.recommendation
            }
        )

        db.session.add(evaluation_result)
        evaluation_results.append(evaluation_result)

    db.session.commit()
    consensus_engine = ConsensusEngine()

    consensus = consensus_engine.calculate(
        judge_results
    )

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

            "judge_results": [
            {
                "detector_type": result.detector_type,
                "detector_name": result.detector_name,
                "score": result.score,
                "confidence": result.confidence,
                "reason": result.reason,
                "metadata": result.metadata_json
            }
            for result in evaluation_results
            ],
            "consensus": consensus
        }
    }), 201