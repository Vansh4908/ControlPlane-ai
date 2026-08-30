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

    decision = data.get("decision", "").upper()
    reason = data.get("reason", "")
    edited_response = data.get("edited_response")

    allowed_decisions = ["APPROVE", "ALLOW", "REJECT", "BLOCK", "EDIT_ALLOW", "EDITED_ALLOW"]

    if decision not in allowed_decisions:
        return jsonify({
            "error": f"Invalid decision: {decision}. Must be APPROVE, REJECT, or EDIT_ALLOW"
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

    if decision in ["EDIT_ALLOW", "EDITED_ALLOW"]:
        if not edited_response or not edited_response.strip():
            return jsonify({
                "error": "edited_response is required when choosing Edit & Allow"
            }), 400

        evaluation.edited_response = edited_response.strip()
        evaluation.ai_response = edited_response.strip()
        final_decision = "ALLOW"
        human_decision = "EDITED_ALLOW"
        action_name = "HUMAN_REVIEW_EDITED_ALLOW"
        log_reason = f"Human edited response and approved. Reason: {reason}"

    elif decision in ["APPROVE", "ALLOW"]:
        final_decision = "ALLOW"
        human_decision = "ALLOW"
        action_name = "HUMAN_REVIEW_ALLOW"
        log_reason = f"Human approved response. Reason: {reason}"

    else:
        final_decision = "BLOCK"
        human_decision = "REJECT"
        action_name = "HUMAN_REVIEW_REJECT"
        log_reason = f"Human rejected response. Reason: {reason}"

    evaluation.final_decision = final_decision
    evaluation.human_decision = human_decision

    audit_log = AuditLog(
        evaluation_id=evaluation.id,
        action=action_name,
        actor="HUMAN",
        reason=log_reason
    )

    db.session.add(audit_log)
    db.session.commit()

    return jsonify({
        "message": "Human review completed",
        "evaluation": {
            "id": evaluation.id,
            "final_decision": evaluation.final_decision,
            "human_decision": evaluation.human_decision,
            "ai_response": evaluation.ai_response
        },
        "review": {
            "decision": human_decision,
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
                "application_name": evaluation.application.name if evaluation.application else "N/A",
                "prompt": evaluation.prompt,
                "ai_response": evaluation.ai_response,
                "document_name": evaluation.document_name,
                "document_content": evaluation.document_content,
                "final_decision": evaluation.final_decision,
                "overall_risk": evaluation.overall_risk,
                "confidence": evaluation.confidence,
                "created_at": evaluation.created_at.isoformat(),
                "has_pii": evaluation.has_pii,
                "pii_data": evaluation.pii_data,
                "judge_results": [
                    {
                        "detector_name": res.detector_name,
                        "score": res.score,
                        "confidence": res.confidence,
                        "reason": res.reason,
                        "metadata": res.metadata_json
                    }
                    for res in evaluation.results
                ],
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
                    if evaluation.application and evaluation.application.policy
                    else None
                )
            }
            for evaluation in evaluations
        ]
    }), 200