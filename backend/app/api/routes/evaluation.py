import time

from concurrent.futures import ThreadPoolExecutor

from flask import Blueprint, jsonify, request
from app.database.connection import db
from app.models.application import Application
from app.models.evaluation import Evaluation , EvaluationResult
from app.services.llm.groq_service import GroqService
from app.services.judge.judge_factory import JudgeFactory
from app.services.judge.judge_config import JUDGE_CONFIGS
from app.engines.consensus_engine import ConsensusEngine
from app.engines.risk_engine import RiskEngine
from app.engines.policy_engine import PolicyEngine
from app.models.audit_log import AuditLog
from app.services.rag.retrieval_service import RetrievalService
from app.services.pii.pii_detector import PIIDetector


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

    start_time = time.perf_counter()

    try:
        llm = GroqService()
        ai_response = llm.generate_response(prompt,application.model_name)

        pii_detector = PIIDetector()
        pii_result = pii_detector.detect(ai_response)
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

    if pii_result["has_pii"]:
        evaluation.has_pii = True
        evaluation.pii_data = pii_result["detected_types"]

    db.session.add(evaluation)
    db.session.commit()


    retrieval_service = RetrievalService()

    retrieved_knowledge = retrieval_service.retrieve(
        prompt,
        top_k=3
    )

    def evaluate_judge(judge_config):
        judge = JudgeFactory.create(
            judge_config["provider"],
            judge_config["model"]
        )

        context = None

        if judge_config["name"] == "truthfulness":
            context = "\n\n".join(
                result["content"]
                for result in retrieved_knowledge
            )

        res = judge.evaluate(
            prompt,
            ai_response,
            judge_config["display_name"],
            judge_config["criteria"],
            context=context
        )

        return judge_config, res

    results_by_name = {}
    with ThreadPoolExecutor(max_workers=len(JUDGE_CONFIGS)) as executor:
        futures = [
            executor.submit(evaluate_judge, config)
            for config in JUDGE_CONFIGS
        ]
        for future in futures:
            try:
                config, judge_result = future.result()
                results_by_name[config["name"]] = (config, judge_result)
            except Exception as exc:
                return jsonify({
                    "error": "Judge evaluation failed",
                    "details": str(exc)
                }), 502

    evaluation_results = []
    judge_results = []

    for judge_config in JUDGE_CONFIGS:
        config, judge_result = results_by_name[judge_config["name"]]
        judge_results.append(judge_result)

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

    risk_engine = RiskEngine()

    risk_assessment = risk_engine.analyze(
        judge_results,
        consensus,
        pii_result
    )

    policy_engine = PolicyEngine()

    policy_decision = None

    if application.policy :
        policy_decision = policy_engine.decide(
            risk_assessment,
            application.policy
        )

    evaluation.overall_risk = risk_assessment["overall_risk"]
    evaluation.confidence = risk_assessment["confidence"]

    if policy_decision:
        evaluation.final_decision = policy_decision["decision"]

    evaluation.latency_ms = round(
        (time.perf_counter() - start_time) * 1000
    )

    if policy_decision:
        audit_log = AuditLog(
            evaluation_id=evaluation.id,
            action="POLICY_DECISION",
            actor="SYSTEM",
            reason=policy_decision["reason"]
        )

        db.session.add(audit_log)

    db.session.commit()

    return jsonify({
        "message": "Evaluation created successfully",
        "evaluation": {
            "id": evaluation.id,
            "application_id": evaluation.application_id,
            "prompt": evaluation.prompt,
            "ai_response": evaluation.ai_response,
            "final_decision": (
                policy_decision["decision"]
                if policy_decision
                else None
            ),
            "overall_risk": evaluation.overall_risk,
            "confidence": evaluation.confidence,
            "latency_ms": evaluation.latency_ms,
            "risk": risk_assessment,
            "policy_decision": policy_decision,

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
            "consensus": consensus,
            "rag_evidence": retrieved_knowledge,
            "pii": {
                "detected": pii_result["has_pii"],
                "detected_types": pii_result["detected_types"]
            }
        }
    }), 201

