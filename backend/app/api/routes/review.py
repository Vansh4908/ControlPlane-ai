from flask import Blueprint, jsonify, request

from app.database.connection import db
from app.models.evaluation import Evaluation
from app.models.audit_log import AuditLog


review_bp = Blueprint(
    "review",
    __name__,
    url_prefix="/api/evaluations"
)


@review_bp.post("/<int:evaluation_id>/review")
def review_evaluation(evaluation_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    decision = data.get("decision")
    reason = data.get("reason")

    if decision not in ["APPROVE", "REJECT"]:
        return jsonify({
            "error": "decision must be APPROVE or REJECT"
        }), 400

    if not reason or not reason.strip():
        return jsonify({
            "error": "reason is required"
        }), 400

    evaluation = Evaluation.query.get(evaluation_id)

    if not evaluation:
        return jsonify({
            "error": "Evaluation not found"
        }), 404

    if evaluation.final_decision != "REVIEW":
        return jsonify({
            "error": "Evaluation is not awaiting human review"
        }), 400

    # Convert human decision into final governance decision
    final_decision = (
        "ALLOW"
        if decision == "APPROVE"
        else "BLOCK"
    )

    evaluation.final_decision = final_decision

    audit_log = AuditLog(
        evaluation_id=evaluation.id,
        action="HUMAN_REVIEW",
        actor="HUMAN",
        reason=(
            f"Human decision: {decision}. "
            f"Decision changed from REVIEW to {final_decision}. "
            f"Reason: {reason}"
        )
    )

    db.session.add(audit_log)
    db.session.commit()

    return jsonify({
        "message": "Human review completed",
        "evaluation": {
            "id": evaluation.id,
            "final_decision": evaluation.final_decision
        },
        "review": {
            "decision": decision,
            "reason": reason,
            "actor": "HUMAN"
        }
    }), 200

@review_bp.get("/<int:evaluation_id>/audit")
def get_audit_logs(evaluation_id):

    evaluation = Evaluation.query.get(evaluation_id)

    if not evaluation:
        return jsonify({
            "error": "Evaluation not found"
        }), 404

    audit_logs = AuditLog.query.filter_by(
        evaluation_id=evaluation.id
    ).order_by(
        AuditLog.created_at.asc()
    ).all()

    return jsonify({
        "evaluation_id": evaluation.id,
        "audit_logs": [
            {
                "id": log.id,
                "action": log.action,
                "actor": log.actor,
                "reason": log.reason,
                "created_at": log.created_at.isoformat()
            }
            for log in audit_logs
        ]
    }), 200

@review_bp.get("/review")
def get_review_queue():

    evaluations = Evaluation.query.filter_by(
        final_decision="REVIEW"
    ).order_by(
        Evaluation.created_at.desc()
    ).all()

    return jsonify({
        "evaluations": [
            {
                "id": evaluation.id,
                "application_id": evaluation.application_id,
                "prompt": evaluation.prompt,
                "ai_response": evaluation.ai_response,
                "final_decision": evaluation.final_decision,
                "overall_risk": evaluation.overall_risk,
                "confidence": evaluation.confidence,
                "created_at": evaluation.created_at.isoformat(),

                "policy": (
                    {
                        "id": evaluation.application.policy.id,
                        "name": evaluation.application.policy.name,
                        "pii_action": evaluation.application.policy.pii_action,
                        "hallucination_action": (
                            evaluation.application.policy.hallucination_action
                        ),
                        "bias_action": evaluation.application.policy.bias_action
                    }
                    if evaluation.application.policy
                    else None
                )
            }
            for evaluation in evaluations
        ]
    }), 200