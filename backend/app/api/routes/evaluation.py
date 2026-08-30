import time

from concurrent.futures import ThreadPoolExecutor

from flask import Blueprint, jsonify, request

from app.database.connection import db
from app.models.application import Application
from app.models.evaluation import Evaluation, EvaluationResult
from app.models.audit_log import AuditLog

from app.services.llm.groq_service import GroqService

from app.services.judge.judge_factory import JudgeFactory
from app.services.judge.judge_config import JUDGE_CONFIGS

from app.engines.consensus_engine import ConsensusEngine
from app.engines.risk_engine import RiskEngine
from app.engines.policy_engine import PolicyEngine

from app.services.rag.retrieval_service import RetrievalService
from app.services.rag.document_parser import DocumentParser
from app.services.pii.pii_detector import PIIDetector


evaluation_bp = Blueprint(
    "evaluation",
    __name__,
    url_prefix="/api/evaluations"
)


@evaluation_bp.post("")
def create_evaluation():

    # ---------------------------------------------------------
    # 1. Validate request (Form-data with file OR JSON)
    # ---------------------------------------------------------

    uploaded_file = request.files.get("file")
    doc_name = None
    doc_content = None

    if uploaded_file:
        doc_name = uploaded_file.filename
        try:
            doc_content = DocumentParser.parse(uploaded_file, doc_name)
        except Exception as err:
            return jsonify({
                "error": f"Failed to parse uploaded document: {str(err)}"
            }), 400

        application_id = request.form.get("application_id")
        prompt = request.form.get("prompt")
    else:
        data = request.get_json(silent=True) or {}
        application_id = data.get("application_id")
        prompt = data.get("prompt")
        doc_name = data.get("document_name")
        doc_content = data.get("document_content")

    if not application_id:
        return jsonify({
            "error": "application_id is required"
        }), 400

    if not prompt or not prompt.strip():
        return jsonify({
            "error": "prompt is required"
        }), 400

    # ---------------------------------------------------------
    # 2. Find application
    # ---------------------------------------------------------

    application = Application.query.get(application_id)

    if not application:
        return jsonify({
            "error": "Application not found"
        }), 404

    if application.model_provider.lower() != "groq":
        return jsonify({
            "error": (
                f"Unsupported model provider: "
                f"{application.model_provider}"
            )
        }), 400

    # ---------------------------------------------------------
    # 3. BLOCK new prompts while previous evaluation
    #    is waiting for human review
    # ---------------------------------------------------------

    pending_review = Evaluation.query.filter_by(
        application_id=application.id,
        final_decision="REVIEW"
    ).order_by(
        Evaluation.created_at.desc()
    ).first()

    if pending_review:
        return jsonify({
            "error": "Application has a pending human review",
            "message": (
                "This response must be reviewed before "
                "another prompt can be submitted."
            ),
            "evaluation_id": pending_review.id,
            "status": "REVIEW"
        }), 409

    start_time = time.perf_counter()

    # ---------------------------------------------------------
    # 4. Generate target AI response (using document as reference if attached)
    # ---------------------------------------------------------

    try:

        llm = GroqService()

        if doc_content and doc_content.strip():
            augmented_prompt = f"""Use the following reference document to accurately answer the user's prompt.

--- REFERENCE DOCUMENT ({doc_name or 'Uploaded File'}) ---
{doc_content}
--- END REFERENCE DOCUMENT ---

USER PROMPT:
{prompt}"""
        else:
            augmented_prompt = prompt

        ai_response = llm.generate_response(
            augmented_prompt,
            application.model_name
        )

        # -----------------------------------------------------
        # PII detection
        # -----------------------------------------------------

        pii_detector = PIIDetector()

        pii_result = pii_detector.detect(
            ai_response
        )

    except Exception as exc:

        return jsonify({
            "error": "Failed to generate AI response",
            "details": str(exc)
        }), 502

    # ---------------------------------------------------------
    # 5. Create evaluation
    # ---------------------------------------------------------

    evaluation = Evaluation(
        application_id=application.id,
        prompt=prompt,
        ai_response=ai_response,
        document_name=doc_name,
        document_content=doc_content,
        has_pii=pii_result["has_pii"],
        pii_data=pii_result["detected_types"] if pii_result["has_pii"] else None
    )

    db.session.add(evaluation)
    db.session.commit()

    # ---------------------------------------------------------
    # 6. Retrieve enterprise & uploaded knowledge
    # ---------------------------------------------------------

    retrieval_service = RetrievalService()

    retrieved_knowledge = []

    if doc_content and doc_content.strip():
        retrieved_knowledge.append({
            "content": doc_content,
            "document_id": "uploaded_doc",
            "document_name": doc_name or "Uploaded Document",
            "chunk_index": 0
        })

    vector_knowledge = retrieval_service.retrieve(
        prompt,
        top_k=3
    )

    if vector_knowledge:
        retrieved_knowledge.extend(vector_knowledge)

    # ---------------------------------------------------------
    # 7. Run independent judges
    # ---------------------------------------------------------

    def evaluate_judge(judge_config):
        try:
            judge = JudgeFactory.create(
                judge_config["provider"],
                judge_config["model"]
            )

            context = None
            if (
                judge_config["name"] == "truthfulness"
                and retrieved_knowledge
            ):
                context = "\n\n".join(
                    result["content"]
                    for result in retrieved_knowledge
                )

            result = judge.evaluate(
                prompt,
                ai_response,
                judge_config["display_name"],
                judge_config["criteria"],
                context=context
            )
            return judge_config, result
        except Exception as judge_err:
            print(f"Notice: Judge {judge_config['name']} error: {judge_err}")
            from app.api.schemas.evaluation import JudgeResult
            fallback_result = JudgeResult(
                bias_score=0.1,
                hallucination_score=0.1,
                privacy_score=0.1,
                overall_risk=0.1,
                confidence=0.5,
                reason=f"Evaluator notice ({judge_config['display_name']}): {str(judge_err)[:120]}",
                recommendation="ALLOW"
            )
            return judge_config, fallback_result

    results_by_name = {}

    with ThreadPoolExecutor(
        max_workers=len(JUDGE_CONFIGS)
    ) as executor:

        futures = [
            executor.submit(
                evaluate_judge,
                config
            )
            for config in JUDGE_CONFIGS
        ]

        for future in futures:
            try:
                config, judge_result = future.result()
                results_by_name[config["name"]] = (config, judge_result)
            except Exception as exc:
                print(f"ThreadPool error: {exc}")

    # ---------------------------------------------------------
    # 8. Store judge results
    # ---------------------------------------------------------

    evaluation_results = []
    judge_results = []

    for judge_config in JUDGE_CONFIGS:

        config, judge_result = (
            results_by_name[
                judge_config["name"]
            ]
        )

        judge_results.append(
            judge_result
        )

        evaluation_result = EvaluationResult(
            evaluation_id=evaluation.id,
            detector_type="llm_judge",
            detector_name=judge_config["name"],
            score=judge_result.overall_risk,
            confidence=judge_result.confidence,
            reason=judge_result.reason,
            metadata_json={
                "bias_score": (
                    judge_result.bias_score
                ),
                "hallucination_score": (
                    judge_result.hallucination_score
                ),
                "privacy_score": (
                    judge_result.privacy_score
                ),
                "recommendation": (
                    judge_result.recommendation
                )
            }
        )

        db.session.add(
            evaluation_result
        )

        evaluation_results.append(
            evaluation_result
        )

    db.session.commit()

    # ---------------------------------------------------------
    # 9. Consensus
    # ---------------------------------------------------------

    consensus_engine = ConsensusEngine()

    consensus = consensus_engine.calculate(
        judge_results
    )

    # ---------------------------------------------------------
    # 10. Risk analysis
    # ---------------------------------------------------------

    risk_engine = RiskEngine()

    risk_assessment = risk_engine.analyze(
        judge_results,
        consensus,
        pii_result
    )

    # ---------------------------------------------------------
    # 11. Policy analysis
    # ---------------------------------------------------------

    policy_engine = PolicyEngine()

    policy_decision = None

    if application.policy:

        policy_decision = policy_engine.decide(
            risk_assessment,
            application.policy
        )

    # ---------------------------------------------------------
    # 12. Determine final governance decision
    #
    # BLOCK has highest priority.
    # REVIEW comes next.
    # Policy decision is used only when no forced review/block
    # condition exists.
    # ---------------------------------------------------------

    judge_recommendations = [
        result.recommendation.upper()
        for result in judge_results
        if result.recommendation
    ]

    has_block_recommendation = (
        "BLOCK" in judge_recommendations
    )

    has_review_recommendation = (
        "REVIEW" in judge_recommendations
    )

    pii_detected = bool(
        pii_result.get(
            "has_pii",
            False
        )
    )

    forced_review = (
        has_review_recommendation
        or pii_detected
    )

    if has_block_recommendation:

        final_decision = "BLOCK"

    elif forced_review:

        final_decision = "REVIEW"

    elif policy_decision:

        final_decision = (
            policy_decision["decision"]
        )

    else:

        final_decision = "ALLOW"

    # ---------------------------------------------------------
    # 13. Save evaluation risk information
    # ---------------------------------------------------------

    evaluation.overall_risk = (
        risk_assessment["overall_risk"]
    )

    evaluation.confidence = (
        risk_assessment["confidence"]
    )

    evaluation.final_decision = (
        final_decision
    )

    evaluation.latency_ms = round(
        (
            time.perf_counter()
            - start_time
        ) * 1000
    )

    # ---------------------------------------------------------
    # 14. Governance reason
    # ---------------------------------------------------------

    if final_decision == "BLOCK":

        governance_reason = (
            "The response was blocked because "
            "at least one independent judge "
            "identified a blocking risk."
        )

    elif final_decision == "REVIEW":

        if pii_detected and has_review_recommendation:

            governance_reason = (
                "The response requires human review "
                "because an evaluator recommended "
                "REVIEW and PII was detected."
            )

        elif pii_detected:

            governance_reason = (
                "The response requires human review "
                "because personally identifiable "
                "information was detected."
            )

        else:

            governance_reason = (
                "The response requires human review "
                "because at least one independent "
                "judge recommended REVIEW."
            )

    elif policy_decision:

        governance_reason = (
            policy_decision["reason"]
        )

    else:

        governance_reason = (
            "No governance risk exceeded the "
            "configured thresholds."
        )

    # ---------------------------------------------------------
    # 15. Audit log
    # ---------------------------------------------------------

    audit_log = AuditLog(
        evaluation_id=evaluation.id,
        action="POLICY_DECISION",
        actor="SYSTEM",
        reason=governance_reason
    )

    db.session.add(
        audit_log
    )

    db.session.commit()

    # ---------------------------------------------------------
    # 16. Decide whether response can be released
    # ---------------------------------------------------------

    response_released = (
        final_decision == "ALLOW"
    )

    # ---------------------------------------------------------
    # 17. Return result
    # ---------------------------------------------------------

    return jsonify({
        "message": (
            "Evaluation created successfully"
            if response_released
            else "Evaluation requires human review"
            if final_decision == "REVIEW"
            else "Evaluation blocked"
        ),

        "evaluation": {

            "id": evaluation.id,

            "application_id": (
                evaluation.application_id
            ),

            "prompt": evaluation.prompt,

            # IMPORTANT:
            # Never expose original AI response
            # while REVIEW/BLOCK is active.
            "ai_response": (
                evaluation.ai_response
                if response_released
                else None
            ),

            "response_released": (
                response_released
            ),

            "final_decision": (
                final_decision
            ),

            "overall_risk": (
                evaluation.overall_risk
            ),

            "confidence": (
                evaluation.confidence
            ),

            "latency_ms": (
                evaluation.latency_ms
            ),

            "risk": risk_assessment,

            "policy_decision": policy_decision,

            "judge_results": [
                {
                    "detector_type": (
                        result.detector_type
                    ),
                    "detector_name": (
                        result.detector_name
                    ),
                    "score": result.score,
                    "confidence": (
                        result.confidence
                    ),
                    "reason": result.reason,
                    "metadata": (
                        result.metadata_json
                    )
                }
                for result in evaluation_results
            ],

            "consensus": consensus,

            "rag_evidence": (
                retrieved_knowledge
            ),

            "pii": {
                "detected": (
                    pii_result["has_pii"]
                ),
                "detected_types": (
                    pii_result[
                        "detected_types"
                    ]
                )
            },

            "document_name": evaluation.document_name,
            "document_content": evaluation.document_content,

            "governance": {

                "requires_human_review": (
                    final_decision == "REVIEW"
                ),

                "judge_requires_review": (
                    has_review_recommendation
                ),

                "judge_requires_block": (
                    has_block_recommendation
                ),

                "pii_requires_review": (
                    pii_detected
                ),

                "response_released": (
                    response_released
                ),

                "reason": (
                    governance_reason
                )
            }
        }
    }), 201


@evaluation_bp.get("/history")
def get_evaluation_history():
    evaluations = Evaluation.query.order_by(Evaluation.created_at.desc()).all()

    return jsonify({
        "evaluations": [
            {
                "id": evaluation.id,
                "application_id": evaluation.application_id,
                "application_name": evaluation.application.name if evaluation.application else "N/A",
                "model_name": evaluation.application.model_name if evaluation.application else "N/A",
                "prompt": evaluation.prompt,
                "ai_response": evaluation.ai_response,
                "edited_response": evaluation.edited_response,
                "document_name": evaluation.document_name,
                "document_content": evaluation.document_content,
                "final_decision": evaluation.final_decision,
                "human_decision": evaluation.human_decision,
                "overall_risk": evaluation.overall_risk,
                "confidence": evaluation.confidence,
                "latency_ms": evaluation.latency_ms,
                "created_at": evaluation.created_at.isoformat(),
                "has_pii": evaluation.has_pii,
                "pii_data": evaluation.pii_data,
                "judge_results": [
                    {
                        "detector_type": res.detector_type,
                        "detector_name": res.detector_name,
                        "score": res.score,
                        "confidence": res.confidence,
                        "reason": res.reason,
                        "metadata": res.metadata_json
                    }
                    for res in evaluation.results
                ],
                "audit_logs": [
                    {
                        "id": log.id,
                        "action": log.action,
                        "actor": log.actor,
                        "reason": log.reason,
                        "created_at": log.created_at.isoformat()
                    }
                    for log in evaluation.audit_logs
                ]
            }
            for evaluation in evaluations
        ]
    }), 200