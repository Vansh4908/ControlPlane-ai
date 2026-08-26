from flask import Blueprint, jsonify, request

from app.database.connection import db
from app.models.policy import Policy

policies_bp = Blueprint(
    "policies",
    __name__,
    url_prefix="/api/policies"
)


@policies_bp.get("")
def get_policies():
    policies = Policy.query.order_by(
        Policy.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": policy.id,
            "name": policy.name,
            "description": policy.description,
            "pii_action": policy.pii_action,
            "hallucination_action": policy.hallucination_action,
            "bias_action": policy.bias_action,
            "created_at": policy.created_at.isoformat(),
        }
        for policy in policies
    ])


@policies_bp.post("")
def create_policy():
    data = request.get_json()

    required_fields = [
        "name",
        "pii_action",
        "hallucination_action",
        "bias_action"
    ]

    missing_fields = [
        field
        for field in required_fields
        if not data.get(field)
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400

    policy = Policy(
        name=data["name"],
        description=data.get("description"),
        pii_action=data["pii_action"],
        hallucination_action=data["hallucination_action"],
        bias_action=data["bias_action"]
    )

    db.session.add(policy)
    db.session.commit()

    return jsonify({
        "message": "Policy created successfully",
        "policy": {
            "id": policy.id,
            "name": policy.name,
            "description": policy.description,
            "pii_action": policy.pii_action,
            "hallucination_action": policy.hallucination_action,
            "bias_action": policy.bias_action,
            "created_at": policy.created_at.isoformat(),
        }
    }), 201