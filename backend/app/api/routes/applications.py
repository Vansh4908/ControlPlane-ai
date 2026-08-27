from flask import Blueprint, jsonify, request

from app.database.connection import db
from app.models.application import Application
from app.models.policy import Policy

applications_bp = Blueprint("applications", __name__, url_prefix="/api/applications")


@applications_bp.get("")
def get_application():
    applications = Application.query.order_by(Application.created_at.desc()).all()

    return jsonify([
        {
            "id": application.id,
            "name": application.name,
            "description": application.description,
            "model_provider": application.model_provider,
            "model_name": application.model_name,
            "policy_id": application.policy_id,
            "created_at": application.created_at.isoformat(),
        }
        for application in applications
    ])


@applications_bp.post("")
def create_application():
    data = request.get_json()

    required_fields = [
        "name",
        "model_provider",
        "model_name"
    ]

    missing_fields = [
        field for field in required_fields
        if not data.get(field)
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400

    application = Application(
        name=data["name"],
        description=data.get("description"),
        model_provider=data["model_provider"],
        model_name=data["model_name"],
        policy_id=data.get("policy_id")
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({
        "message": "Application created successfully",
        "application": {
            "id": application.id,
            "name": application.name,
            "description": application.description,
            "model_provider": application.model_provider,
            "model_name": application.model_name,
            "policy_id": application.policy_id,
            "created_at": application.created_at.isoformat(),
        }
    }), 201

@applications_bp.patch("/<int:application_id>/policy")
def assign_policy(application_id):
    data = request.get_json()

    if not data or "policy_id" not in data:
        return jsonify({
            "error": "policy_id is required"
        }), 400

    application = Application.query.get(application_id)

    if not application:
        return jsonify({
            "error": "Application not found"
        }), 404

    policy = Policy.query.get(data["policy_id"])

    if not policy:
        return jsonify({
            "error": "Policy not found"
        }), 404

    application.policy_id = policy.id

    db.session.commit()

    return jsonify({
        "message": "Policy assigned successfully",
        "application": {
            "id": application.id,
            "name": application.name,
            "policy_id": application.policy_id
        }
    })


