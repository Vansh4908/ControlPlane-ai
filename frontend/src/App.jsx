import { useEffect, useRef, useState } from "react";
import {
  getApplications,
  createEvaluation,
  getReviewQueue,
  submitHumanReview,
  getAuditLogs,
  getEvaluationHistory,
} from "./services/api";

import {
  ArrowRight,
  ArrowLeft,
  ShieldCheck,
  BrainCircuit,
  LockKeyhole,
  Activity,
  CheckCircle2,
  FileText,
  Upload,
  Search,
  AlertTriangle,
  Eye,
  Scale,
  Paperclip,
  X,
  History,
  Edit3,
  Check,
  Ban,
  Clock,
  ChevronRight,
  Filter,
  FileCheck,
  ShieldAlert,
  Info,
} from "lucide-react";

import ReactMarkdown from "react-markdown";
import "./App.css";

function App() {
  const [page, setPage] = useState("home");

  const handleNavigate = (targetPage) => {
    setPage(targetPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  if (page === "evaluation") {
    return <EvaluationPage onNavigate={handleNavigate} />;
  }

  if (page === "review") {
    return <ReviewPage onNavigate={handleNavigate} />;
  }

  if (page === "history") {
    return <HistoryPage onNavigate={handleNavigate} />;
  }

  return <HomePage onNavigate={handleNavigate} />;
}

/* =========================================================
   NAVBAR
========================================================= */

function Navbar({ activePage, onNavigate }) {
  return (
    <nav className="navbar">
      <div className="brand" onClick={() => onNavigate("home")} style={{ cursor: "pointer" }}>
        <div className="brand-mark">
          <ShieldCheck size={22} />
        </div>
        <div>
          <div className="brand-name">ControlPlane</div>
          <div className="brand-subtitle">AI GOVERNANCE</div>
        </div>
      </div>

      <div className="nav-links">
        <button
          className={`nav-link ${activePage === "home" ? "active" : ""}`}
          onClick={() => onNavigate("home")}
        >
          Overview
        </button>

        <button
          className={`nav-link ${activePage === "evaluation" ? "active" : ""}`}
          onClick={() => onNavigate("evaluation")}
        >
          Evaluate
        </button>

        <button
          className={`nav-link ${activePage === "review" ? "active" : ""}`}
          onClick={() => onNavigate("review")}
        >
          Human Review
        </button>

        <button
          className={`nav-link ${activePage === "history" ? "active" : ""}`}
          onClick={() => onNavigate("history")}
        >
          History
        </button>
      </div>

      <div className="nav-status">
        <span className="status-dot" />
        System operational
      </div>
    </nav>
  );
}

/* =========================================================
   HOME PAGE
========================================================= */

function HomePage({ onNavigate }) {
  return (
    <div className="app-shell">
      <Navbar activePage="home" onNavigate={onNavigate} />

      <main>
        <section className="hero-section">
          <div className="hero-eyebrow">
            <span className="eyebrow-line" />
            ENTERPRISE AI SAFETY & GOVERNANCE
          </div>

          <h1>
            The control plane
            <br />
            for <span>trustworthy AI.</span>
          </h1>

          <p className="hero-description">
            Evaluate AI responses in real-time, attach reference documents directly to prompts, verify outputs with multi-model RAG judges, and enforce human-in-the-loop governance.
          </p>

          <div className="hero-actions">
            <button className="primary-button" onClick={() => onNavigate("evaluation")}>
              Evaluate Prompt & Doc
              <ArrowRight size={18} />
            </button>

            <button className="secondary-button" onClick={() => onNavigate("review")}>
              Human Review Queue
              <ShieldAlert size={17} />
            </button>

            <button className="secondary-button" onClick={() => onNavigate("history")}>
              View Audit History
              <History size={17} />
            </button>
          </div>

          <div className="hero-meta">
            <div>
              <CheckCircle2 size={16} />
              Inline Prompt RAG Upload
            </div>
            <div>
              <CheckCircle2 size={16} />
              Truthfulness RAG Verification
            </div>
            <div>
              <CheckCircle2 size={16} />
              Redesigned PII Detection
            </div>
            <div>
              <CheckCircle2 size={16} />
              Human Edit & Release
            </div>
          </div>
        </section>

        <section className="architecture-preview">
          <div className="section-label">HOW CONTROLPLANE GOVERNS AI</div>
          <div className="architecture-flow">
            <ArchitectureStep
              icon={<Paperclip />}
              title="Prompt & Upload"
              text="Attach doc directly to prompt."
            />
            <FlowArrow />
            <ArchitectureStep
              icon={<BrainCircuit />}
              title="Groq Target AI"
              text="Generate answer using doc context."
            />
            <FlowArrow />
            <ArchitectureStep
              icon={<Search />}
              title="RAG Truthfulness"
              text="Verify target answer against doc."
            />
            <FlowArrow />
            <ArchitectureStep
              icon={<ShieldCheck />}
              title="3 LLM Judges"
              text="Gemini, Groq, OpenRouter risk evaluation."
            />
            <FlowArrow />
            <ArchitectureStep
              icon={<Edit3 />}
              title="Human Review"
              text="Allow, Reject, or Edit & Allow."
            />
          </div>
        </section>
      </main>

      <footer>
        <span>CONTROLPLANE</span>
        <span>AI GOVERNANCE PLATFORM · V2</span>
      </footer>
    </div>
  );
}

function ArchitectureStep({ icon, title, text }) {
  return (
    <div className="architecture-step">
      <div className="architecture-icon">{icon}</div>
      <strong>{title}</strong>
      <span>{text}</span>
    </div>
  );
}

function FlowArrow() {
  return (
    <div className="flow-arrow">
      <ArrowRight size={17} />
    </div>
  );
}

/* =========================================================
   EVALUATION PAGE (INLINE UPLOAD + PROMPT)
========================================================= */

function EvaluationPage({ onNavigate }) {
  const [prompt, setPrompt] = useState("");
  const [applications, setApplications] = useState([]);
  const [selectedApplication, setSelectedApplication] = useState("");
  const [attachedFile, setAttachedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);
  const isSubmittingRef = useRef(false);

  useEffect(() => {
    async function loadApplications() {
      try {
        const data = await getApplications();
        setApplications(data);
        if (data.length > 0) {
          setSelectedApplication(String(data[0].id));
        }
      } catch (err) {
        setError(err.message);
      }
    }
    loadApplications();
  }, []);

  function handleFileSelect(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    const parts = file.name.split(".");
    const ext = parts[parts.length - 1].toLowerCase();
    if (!["txt", "pdf", "md"].includes(ext)) {
      setError("Please attach a .txt, .pdf, or .md document.");
      return;
    }

    setError("");
    setAttachedFile(file);
  }

  function handleRemoveFile() {
    setAttachedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  async function handleEvaluate() {
    if (!prompt.trim() || !selectedApplication || loading || isSubmittingRef.current) {
      return;
    }

    isSubmittingRef.current = true;
    setLoading(true);
    setError("");
    setResult(null);

    try {
      let payload;
      if (attachedFile) {
        const formData = new FormData();
        formData.append("application_id", selectedApplication);
        formData.append("prompt", prompt.trim());
        formData.append("file", attachedFile);
        payload = formData;
      } else {
        payload = {
          application_id: Number(selectedApplication),
          prompt: prompt.trim(),
        };
      }

      const data = await createEvaluation(payload);
      setResult(data.evaluation);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      isSubmittingRef.current = false;
    }
  }

  return (
    <div className="app-shell">
      <Navbar activePage="evaluation" onNavigate={onNavigate} />

      <main className="evaluation-page">
        <div className="page-nav-bar">
          <button className="back-link-button" onClick={() => onNavigate("home")}>
            <ArrowLeft size={16} /> Back to Overview
          </button>
        </div>

        <div className="evaluation-header">
          <div className="hero-eyebrow">
            <span className="eyebrow-line" />
            AI RESPONSE EVALUATION
          </div>
          <h2>Evaluate AI Prompt & Reference Document</h2>
          <p>
            Prompt Groq Target AI directly. Attach a reference document then and there like GPT/Gemini—ControlPlane will pass the document to Groq as reference and let the 3 AI judges verify response truthfulness.
          </p>
        </div>

        <section className="evaluation-card">
          <div className="form-group">
            <label>TARGET APPLICATION</label>
            <select
              value={selectedApplication}
              onChange={(e) => setSelectedApplication(e.target.value)}
            >
              {applications.map((app) => (
                <option key={app.id} value={app.id}>
                  {app.name} · {app.model_name} ({app.model_provider})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>PROMPT</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your prompt for the target AI..."
              rows={6}
            />
          </div>

          {/* INLINE ATTACHMENT BOX */}
          <div className="form-group inline-attachment-group">
            <label>REFERENCE DOCUMENT (OPTIONAL)</label>
            <input
              type="file"
              ref={fileInputRef}
              accept=".txt,.pdf,.md"
              onChange={handleFileSelect}
              hidden
            />

            {!attachedFile ? (
              <div
                className="attachment-dropzone"
                onClick={() => fileInputRef.current?.click()}
              >
                <Paperclip size={20} />
                <span>Click or drag a <strong>.txt, .pdf, or .md</strong> file to attach as reference for Groq target AI</span>
              </div>
            ) : (
              <div className="attached-file-pill">
                <div className="attached-file-info">
                  <FileText size={18} className="file-icon" />
                  <div>
                    <strong>{attachedFile.name}</strong>
                    <span>{(attachedFile.size / 1024).toFixed(1)} KB</span>
                  </div>
                </div>
                <button
                  type="button"
                  className="icon-button-danger"
                  onClick={handleRemoveFile}
                  title="Remove document"
                >
                  <X size={16} />
                </button>
              </div>
            )}
          </div>

          <div className="evaluation-footer">
            <div className="evaluation-info">
              <span className="status-dot" />
              Groq Target AI · RAG Verification · 3 Judges (Gemini, Groq, OpenRouter) · PII Scan
            </div>

            <button
              className="primary-button"
              disabled={!prompt.trim() || !selectedApplication || loading}
              onClick={handleEvaluate}
            >
              {loading ? "Evaluating..." : "Run Evaluation"}
              {!loading && <ArrowRight size={18} />}
            </button>
          </div>
        </section>

        {error && (
          <div className="error-box">
            <AlertTriangle size={18} />
            <span>{error}</span>
          </div>
        )}

        {result && <EvaluationResult result={result} />}
      </main>
    </div>
  );
}

/* =========================================================
   EVALUATION RESULT VIEW
========================================================= */

function EvaluationResult({ result }) {
  const risk = result.risk || {};
  const categoryScores = risk.category_scores || {};
  const decision = result.final_decision || "UNKNOWN";
  const riskLevel = risk.risk_level || "LOW";

  return (
    <section className="result-preview">
      <div className="section-label">EVALUATION RESULT</div>

      <div className={`decision-banner decision-${decision.toLowerCase()}`}>
        <div>
          <span className="result-label">GOVERNANCE DECISION</span>
          <div className="decision-value">
            <span className="decision-dot" />
            {decision}
          </div>
        </div>

        <div className="decision-side">
          <div>
            <span>RISK LEVEL</span>
            <strong>{riskLevel}</strong>
          </div>
          <div>
            <span>OVERALL RISK</span>
            <strong>{Number(result.overall_risk || 0).toFixed(2)}</strong>
          </div>
          <div>
            <span>CONFIDENCE</span>
            <strong>{(Number(result.confidence || 0) * 100).toFixed(0)}%</strong>
          </div>
          <div>
            <span>LATENCY</span>
            <strong>{result.latency_ms} ms</strong>
          </div>
        </div>
      </div>

      {result.document_name && (
        <div className="result-card doc-reference-card">
          <div className="result-label">ATTACHED REFERENCE DOCUMENT</div>
          <div className="doc-reference-header">
            <FileCheck size={20} />
            <strong>{result.document_name}</strong>
          </div>
          <p className="doc-content-snippet">
            {result.document_content
              ? result.document_content.substring(0, 300) + (result.document_content.length > 300 ? "..." : "")
              : "Reference document loaded into Groq prompt & RAG."}
          </p>
        </div>
      )}

      <div className="result-card ai-response-card">
        <div className="result-label">GROQ TARGET AI RESPONSE</div>
        {result.ai_response ? (
          <div className="markdown-content">
            <ReactMarkdown>{result.ai_response}</ReactMarkdown>
          </div>
        ) : (
          <div className="response-blocked-message">
            <LockKeyhole size={24} />
            <div>
              <strong>Response Withheld Pending Human Review</strong>
              <p>{result.governance?.reason || "This response requires human review before it can be released."}</p>
            </div>
          </div>
        )}
      </div>

      <RiskAnalysis risk={risk} categoryScores={categoryScores} />
      <JudgeResults judges={result.judge_results} />
      <RagEvidence evidence={result.rag_evidence} />
      <PiiEvidence pii={result.pii} />
    </section>
  );
}

/* =========================================================
   RISK ANALYSIS
========================================================= */

function RiskAnalysis({ risk, categoryScores }) {
  const categories = [
    { key: "safety", label: "Safety", icon: <ShieldCheck size={17} /> },
    { key: "hallucination", label: "Truthfulness / Hallucination", icon: <BrainCircuit size={17} /> },
    { key: "bias", label: "Fairness / Bias", icon: <Scale size={17} /> },
    { key: "privacy", label: "Privacy", icon: <LockKeyhole size={17} /> },
  ];

  return (
    <div className="result-card">
      <div className="result-label">RISK AGGREGATION</div>
      <div className="risk-grid">
        {categories.map((cat) => {
          const score = Number(categoryScores[cat.key] || 0);
          return (
            <div className="risk-item" key={cat.key}>
              <div className="risk-item-header">
                <div className="risk-name">
                  {cat.icon}
                  {cat.label}
                </div>
                <strong>{score.toFixed(2)}</strong>
              </div>
              <div className="risk-bar">
                <div
                  className="risk-bar-fill"
                  style={{
                    width: `${Math.min(score * 100, 100)}%`,
                    backgroundColor: score > 0.6 ? "#ef4444" : score > 0.3 ? "#f59e0b" : "#10b981",
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* =========================================================
   JUDGES
========================================================= */

function JudgeResults({ judges = [] }) {
  return (
    <div className="judges-section">
      <div className="result-label">INDEPENDENT EVALUATOR JUDGES</div>
      <div className="judge-list">
        {judges.map((judge) => (
          <div className="judge-card judge-card-enhanced" key={judge.detector_name}>
            <div className="judge-header">
              <div className="judge-title-group">
                <span className="judge-name">{judge.detector_name.replace("_", " ")}</span>
                <span className="judge-type">LLM JUDGE</span>
              </div>
              <span className={`judge-recommendation ${String(judge.metadata?.recommendation || "").toLowerCase()}`}>
                {judge.metadata?.recommendation}
              </span>
            </div>
            <div className="judge-metrics">
              <div>
                <span>RISK</span>
                <strong>{Number(judge.score || 0).toFixed(2)}</strong>
              </div>
              <div>
                <span>CONFIDENCE</span>
                <strong>{(Number(judge.confidence || 0) * 100).toFixed(0)}%</strong>
              </div>
            </div>
            <p>{judge.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

/* =========================================================
   RAG EVIDENCE
========================================================= */

function RagEvidence({ evidence = [] }) {
  return (
    <div className="evidence-card">
      <div className="evidence-header">
        <div>
          <div className="result-label">RAG TRUTHFULNESS EVIDENCE</div>
          <h3>Document Verification Check</h3>
        </div>
        <Search size={20} />
      </div>

      {evidence.length === 0 ? (
        <div className="evidence-empty">
          <Info size={18} />
          <p>No document attached or knowledge retrieved. Truthfulness judge evaluated based on general model knowledge.</p>
        </div>
      ) : (
        <div className="evidence-list">
          {evidence.map((item, idx) => (
            <div className="evidence-item" key={idx}>
              <div className="evidence-status">
                <CheckCircle2 size={18} />
              </div>
              <div>
                <div className="evidence-meta">
                  Source: <strong>{item.document_name}</strong> {item.chunk_index !== undefined ? `· Chunk #${item.chunk_index}` : ""}
                </div>
                <p>{item.content}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* =========================================================
   PII EVIDENCE
========================================================= */

function PiiEvidence({ pii }) {
  const detected = Boolean(pii?.detected);
  const types = pii?.detected_types || [];

  return (
    <div className="result-card pii-card-modern">
      <div className="result-label">PRIVACY & PII ANALYSIS</div>
      <div className={`pii-status-modern ${detected ? "pii-alert" : "pii-clean"}`}>
        <div className="pii-icon">
          {detected ? <ShieldAlert size={22} /> : <CheckCircle2 size={22} />}
        </div>
        <div className="pii-details">
          <strong>{detected ? "PII Risk Detected" : "No PII Detected"}</strong>
          <p>
            {detected
              ? "Personally Identifiable Information was found in the response."
              : "The response is clean of sensitive personal information."}
          </p>
          {detected && types.length > 0 && (
            <div className="pii-tags-grid">
              {types.map((t) => (
                <span className="pii-tag" key={t}>
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* =========================================================
   HUMAN REVIEW PAGE (REDESIGNED & UI FRIENDLY)
========================================================= */

function ReviewPage({ onNavigate }) {
  const [reviews, setReviews] = useState([]);
  const [selectedReview, setSelectedReview] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [reason, setReason] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [editedResponse, setEditedResponse] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadReviews() {
    try {
      setLoading(true);
      const data = await getReviewQueue();
      setReviews(data.evaluations || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadReviews();
  }, []);

  async function selectReview(evaluation) {
    setSelectedReview(evaluation);
    setReason("");
    setIsEditing(false);
    setEditedResponse(evaluation.ai_response || "");
    setError("");
    setSuccess("");

    try {
      const data = await getAuditLogs(evaluation.id);
      setAuditLogs(data.audit_logs || []);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleReviewAction(decision) {
    if (!selectedReview || !reason.trim()) {
      setError("Please provide a reason for your governance review decision.");
      return;
    }

    if (decision === "EDIT_ALLOW" && !editedResponse.trim()) {
      setError("Please edit the AI response text before choosing Edit & Allow.");
      return;
    }

    setSubmitting(true);
    setError("");
    setSuccess("");

    try {
      const payload = {
        decision,
        reason: reason.trim(),
        edited_response: decision === "EDIT_ALLOW" ? editedResponse.trim() : undefined,
      };

      await submitHumanReview(selectedReview.id, payload);

      setSuccess(`Evaluation #${selectedReview.id} review decision saved successfully!`);
      setSelectedReview(null);
      await loadReviews();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="app-shell">
      <Navbar activePage="review" onNavigate={onNavigate} />

      <main className="evaluation-page">
        <div className="page-nav-bar">
          <button className="back-link-button" onClick={() => onNavigate("home")}>
            <ArrowLeft size={16} /> Back to Overview
          </button>
        </div>

        <div className="evaluation-header">
          <div className="hero-eyebrow">
            <span className="eyebrow-line" />
            HUMAN GOVERNANCE REVIEW
          </div>
          <h2>Review AI Decisions</h2>
          <p>Inspect flagged responses, review PII & RAG truthfulness feedback, and choose to <strong>Allow</strong>, <strong>Reject</strong>, or <strong>Edit & Allow</strong>.</p>
        </div>

        {error && (
          <div className="error-box">
            <AlertTriangle size={18} />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="success-box">
            <CheckCircle2 size={18} />
            <span>{success}</span>
          </div>
        )}

        {loading ? (
          <div className="result-card">Loading review queue...</div>
        ) : reviews.length === 0 ? (
          <div className="empty-card">
            <CheckCircle2 size={32} className="success-icon" />
            <strong>Human Review Queue is Clear</strong>
            <p>No evaluations are currently flagged for human intervention.</p>
          </div>
        ) : (
          <div className="review-layout">
            {/* QUEUE LIST SIDEBAR */}
            <div className="review-sidebar">
              <div className="section-label">PENDING REVIEWS ({reviews.length})</div>
              <div className="review-queue-list">
                {reviews.map((item) => (
                  <div
                    key={item.id}
                    className={`review-queue-card ${selectedReview?.id === item.id ? "active" : ""}`}
                    onClick={() => selectReview(item)}
                  >
                    <div className="queue-card-top">
                      <span className="queue-id">Evaluation #{item.id}</span>
                      <span className="review-badge">REVIEW</span>
                    </div>
                    <p className="queue-prompt-preview">{item.prompt}</p>
                    <div className="queue-card-meta">
                      <span>Risk: {item.overall_risk !== null ? item.overall_risk.toFixed(2) : "N/A"}</span>
                      {item.has_pii && <span className="pii-mini-badge">PII</span>}
                      {item.document_name && <span className="doc-mini-badge">DOC</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* SELECTED REVIEW WORKSPACE */}
            <div className="review-workspace">
              {selectedReview ? (
                <div className="selected-review-panel">
                  <div className="panel-header">
                    <h3>Evaluation #{selectedReview.id} Review Workspace</h3>
                    <span className="application-tag">{selectedReview.application_name}</span>
                  </div>

                  {/* PROMPT */}
                  <div className="result-card">
                    <div className="result-label">ORIGINAL PROMPT</div>
                    <p className="prompt-display">{selectedReview.prompt}</p>
                  </div>

                  {/* ATTACHED DOCUMENT REFERENCE */}
                  {selectedReview.document_name && (
                    <div className="result-card doc-reference-card">
                      <div className="result-label">ATTACHED REFERENCE DOCUMENT</div>
                      <div className="doc-reference-header">
                        <FileCheck size={18} />
                        <strong>{selectedReview.document_name}</strong>
                      </div>
                      {selectedReview.document_content && (
                        <div className="doc-content-box">
                          {selectedReview.document_content.substring(0, 400)}...
                        </div>
                      )}
                    </div>
                  )}

                  {/* BEAUTIFIED PII ALERT SECTION */}
                  {selectedReview.has_pii && (
                    <div className="pii-alert-banner-modern">
                      <div className="pii-alert-header">
                        <ShieldAlert size={22} />
                        <div>
                          <strong>PII (Sensitive Data) Detected</strong>
                          <p>The AI response contains personal information. You can reject or edit it before release.</p>
                        </div>
                      </div>
                      <div className="pii-tags-grid">
                        {(selectedReview.pii_data || []).map((type) => (
                          <span className="pii-tag-alert" key={type}>
                            {type}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* TARGET AI RESPONSE & EDIT MODE */}
                  <div className="result-card">
                    <div className="result-label-row">
                      <span className="result-label">AI GENERATED RESPONSE</span>
                      {!isEditing ? (
                        <button
                          type="button"
                          className="secondary-button compact"
                          onClick={() => setIsEditing(true)}
                        >
                          <Edit3 size={15} /> Edit Response Text
                        </button>
                      ) : (
                        <button
                          type="button"
                          className="secondary-button compact"
                          onClick={() => {
                            setIsEditing(false);
                            setEditedResponse(selectedReview.ai_response);
                          }}
                        >
                          Cancel Edit
                        </button>
                      )}
                    </div>

                    {!isEditing ? (
                      <div className="markdown-content ai-response-box">
                        <ReactMarkdown>{editedResponse || selectedReview.ai_response}</ReactMarkdown>
                      </div>
                    ) : (
                      <div className="interactive-editor-box">
                        <textarea
                          value={editedResponse}
                          onChange={(e) => setEditedResponse(e.target.value)}
                          rows={8}
                          className="code-textarea"
                        />
                        <div className="editor-footer">
                          <span>Chars: {editedResponse.length} | Words: {editedResponse.split(/\s+/).filter(Boolean).length}</span>
                          <span className="editor-tip">Editing will save this as the final released AI response.</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* JUDGES EVALUATION BREAKDOWN */}
                  {selectedReview.judge_results && selectedReview.judge_results.length > 0 && (
                    <div className="result-card">
                      <div className="result-label">EVALUATOR JUDGES FEEDBACK</div>
                      <div className="judge-list">
                        {selectedReview.judge_results.map((j) => (
                          <div className="judge-card" key={j.detector_name}>
                            <div className="judge-header">
                              <strong>{j.detector_name.replace("_", " ")}</strong>
                              <span className={`judge-recommendation ${String(j.metadata?.recommendation || "").toLowerCase()}`}>
                                {j.metadata?.recommendation}
                              </span>
                            </div>
                            <p>{j.reason}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* DECISION ACTION FORM */}
                  <div className="result-card review-actions-card">
                    <div className="result-label">GOVERNANCE DECISION & REASONING</div>
                    <textarea
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                      placeholder="Explain why you approve, reject, or edit this response..."
                      rows={3}
                    />

                    <div className="action-button-group">
                      <button
                        className="primary-button allow-btn"
                        disabled={submitting}
                        onClick={() => handleReviewAction("ALLOW")}
                      >
                        <Check size={18} />
                        Allow As-Is
                      </button>

                      <button
                        className="primary-button edit-allow-btn"
                        disabled={submitting}
                        onClick={() => {
                          if (!isEditing) setIsEditing(true);
                          handleReviewAction("EDIT_ALLOW");
                        }}
                      >
                        <Edit3 size={18} />
                        Edit & Allow
                      </button>

                      <button
                        className="secondary-button reject-btn"
                        disabled={submitting}
                        onClick={() => handleReviewAction("REJECT")}
                      >
                        <Ban size={18} />
                        Reject & Block
                      </button>
                    </div>
                  </div>

                  {/* AUDIT LOGS */}
                  {auditLogs.length > 0 && (
                    <div className="result-card">
                      <div className="result-label">AUDIT TRAIL</div>
                      <div className="audit-timeline">
                        {auditLogs.map((log) => (
                          <div className="audit-timeline-item" key={log.id}>
                            <div className="audit-action">{log.action}</div>
                            <div className="audit-actor">{log.actor}</div>
                            <p>{log.reason}</p>
                            <span className="audit-time">{new Date(log.created_at).toLocaleString()}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="empty-card">
                  <Info size={28} />
                  <p>Select an evaluation from the review queue on the left to inspect and take governance action.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

/* =========================================================
   HISTORY PAGE
========================================================= */

function HistoryPage({ onNavigate }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("ALL");
  const [selectedItem, setSelectedItem] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadHistory() {
      try {
        setLoading(true);
        const data = await getEvaluationHistory();
        setHistory(data.evaluations || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  const filteredHistory = history.filter((item) => {
    if (filter === "ALL") return true;
    if (filter === "ALLOW") return item.final_decision === "ALLOW" && item.human_decision !== "EDITED_ALLOW";
    if (filter === "BLOCK") return item.final_decision === "BLOCK";
    if (filter === "EDITED") return item.human_decision === "EDITED_ALLOW";
    if (filter === "REVIEW") return item.final_decision === "REVIEW";
    return true;
  });

  return (
    <div className="app-shell">
      <Navbar activePage="history" onNavigate={onNavigate} />

      <main className="evaluation-page">
        <div className="page-nav-bar">
          <button className="back-link-button" onClick={() => onNavigate("home")}>
            <ArrowLeft size={16} /> Back to Overview
          </button>
        </div>

        <div className="evaluation-header">
          <div className="hero-eyebrow">
            <span className="eyebrow-line" />
            AUDIT LOG & DECISION HISTORY
          </div>
          <h2>Evaluation History</h2>
          <p>Comprehensive record of all evaluations, human reviews (allowed, rejected, edited), RAG evidence, and risk scores.</p>
        </div>

        {error && (
          <div className="error-box">
            <AlertTriangle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* FILTER BAR */}
        <div className="history-filter-bar">
          <Filter size={16} />
          <span>Filter Status:</span>
          {["ALL", "ALLOW", "EDITED", "BLOCK", "REVIEW"].map((f) => (
            <button
              key={f}
              className={`filter-chip ${filter === f ? "active" : ""}`}
              onClick={() => setFilter(f)}
            >
              {f === "EDITED" ? "Edited & Allowed" : f}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="result-card">Loading history...</div>
        ) : filteredHistory.length === 0 ? (
          <div className="empty-card">
            <History size={30} />
            <p>No evaluation records match the selected filter.</p>
          </div>
        ) : (
          <div className="history-list">
            {filteredHistory.map((item) => (
              <div className="history-card" key={item.id}>
                <div className="history-card-header">
                  <div className="history-title-group">
                    <strong>Evaluation #{item.id}</strong>
                    <span className="history-app">{item.application_name} · {item.model_name}</span>
                  </div>

                  <div className="history-badges">
                    {item.human_decision === "EDITED_ALLOW" ? (
                      <span className="badge badge-edited">EDITED & ALLOWED</span>
                    ) : item.final_decision === "ALLOW" ? (
                      <span className="badge badge-allow">ALLOW</span>
                    ) : item.final_decision === "BLOCK" ? (
                      <span className="badge badge-block">BLOCK</span>
                    ) : (
                      <span className="badge badge-review">REVIEW</span>
                    )}
                  </div>
                </div>

                <div className="history-body">
                  <div className="history-prompt">
                    <strong>Prompt:</strong> {item.prompt}
                  </div>

                  {item.document_name && (
                    <div className="history-doc-tag">
                      <FileCheck size={14} /> Attached Doc: {item.document_name}
                    </div>
                  )}

                  <div className="history-response-preview">
                    <strong>Response:</strong> {item.ai_response ? item.ai_response.substring(0, 200) + "..." : "[Hidden Pending Review]"}
                  </div>
                </div>

                <div className="history-footer">
                  <span>Created: {new Date(item.created_at).toLocaleString()}</span>
                  <span>Risk: {item.overall_risk !== null ? Number(item.overall_risk).toFixed(2) : "N/A"}</span>
                  <button
                    className="secondary-button compact"
                    onClick={() => setSelectedItem(item)}
                  >
                    View Details <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* DETAILS MODAL */}
        {selectedItem && (
          <div className="modal-backdrop" onClick={() => setSelectedItem(null)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Evaluation #{selectedItem.id} Details</h3>
                <button className="icon-button-danger" onClick={() => setSelectedItem(null)}>
                  <X size={18} />
                </button>
              </div>

              <div className="modal-body">
                <div className="result-card">
                  <div className="result-label">PROMPT</div>
                  <p>{selectedItem.prompt}</p>
                </div>

                {selectedItem.document_name && (
                  <div className="result-card doc-reference-card">
                    <div className="result-label">ATTACHED REFERENCE DOCUMENT</div>
                    <strong>{selectedItem.document_name}</strong>
                    {selectedItem.document_content && (
                      <p className="doc-content-box">{selectedItem.document_content}</p>
                    )}
                  </div>
                )}

                <div className="result-card">
                  <div className="result-label">FINAL RELEASED AI RESPONSE</div>
                  <div className="markdown-content">
                    <ReactMarkdown>{selectedItem.ai_response || "Withheld"}</ReactMarkdown>
                  </div>
                </div>

                {selectedItem.human_decision && (
                  <div className="result-card">
                    <div className="result-label">HUMAN REVIEW ACTION</div>
                    <p>Decision: <strong>{selectedItem.human_decision}</strong></p>
                  </div>
                )}

                {selectedItem.audit_logs && selectedItem.audit_logs.length > 0 && (
                  <div className="result-card">
                    <div className="result-label">AUDIT LOGS</div>
                    {selectedItem.audit_logs.map((log) => (
                      <div key={log.id} className="audit-timeline-item">
                        <strong>{log.action} ({log.actor}):</strong> {log.reason}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;