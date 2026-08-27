import { useEffect, useState } from "react";
import { getApplications, createEvaluation } from "./services/api";
import {
  ArrowRight,
  ShieldCheck,
  BrainCircuit,
  LockKeyhole,
  Activity,
  CheckCircle2,
} from "lucide-react";
import "./App.css";

function App() {
  const [page, setPage] = useState("home");

  if (page === "evaluation") {
    return (
      <EvaluationPage onBack={() => setPage("home")} />
    );
  }

  return <HomePage onEvaluate={() => setPage("evaluation")} />;
}

function Navbar({ onEvaluate }) {
  return (
    <nav className="navbar">
      <div className="brand">
        <div className="brand-mark">
          <ShieldCheck size={21} />
        </div>

        <div>
          <div className="brand-name">ControlPlane</div>
          <div className="brand-subtitle">AI GOVERNANCE</div>
        </div>
      </div>

      <div className="nav-links">
        <button className="nav-link active">Overview</button>
        <button className="nav-link" onClick={onEvaluate}>
          Evaluate
        </button>
        <button className="nav-link">Policies</button>
        <button className="nav-link">Audit Logs</button>
      </div>

      <div className="nav-status">
        <span className="status-dot" />
        System operational
      </div>
    </nav>
  );
}

function HomePage({ onEvaluate }) {
  return (
    <div className="app-shell">
      <Navbar onEvaluate={onEvaluate} />

      <main>
        <section className="hero-section">
          <div className="hero-eyebrow">
            <span className="eyebrow-line" />
            AI SAFETY & GOVERNANCE
          </div>

          <h1>
            The control plane
            <br />
            for <span>trustworthy AI.</span>
          </h1>

          <p className="hero-description">
            Evaluate AI responses, detect hidden risks, and enforce
            configurable policies before unsafe outputs reach users.
          </p>

          <div className="hero-actions">
            <button className="primary-button" onClick={onEvaluate}>
              Evaluate an AI response
              <ArrowRight size={18} />
            </button>

            <button className="secondary-button">
              Explore the platform
            </button>
          </div>

          <div className="hero-meta">
            <div>
              <CheckCircle2 size={16} />
              Multi-model evaluation
            </div>

            <div>
              <CheckCircle2 size={16} />
              Explainable decisions
            </div>

            <div>
              <CheckCircle2 size={16} />
              Full audit trail
            </div>
          </div>
        </section>

        <section className="architecture-preview">
          <div className="section-label">HOW CONTROLPLANE WORKS</div>

          <div className="flow">
            <FlowCard
              icon={<BrainCircuit />}
              title="AI Response"
              text="Target model generates an answer."
            />

            <div className="flow-arrow">
              <ArrowRight />
            </div>

            <FlowCard
              icon={<ShieldCheck />}
              title="Evaluate"
              text="Independent safety checks run in parallel."
            />

            <div className="flow-arrow">
              <ArrowRight />
            </div>

            <FlowCard
              icon={<Activity />}
              title="Risk Engine"
              text="Signals are combined into a risk level."
            />

            <div className="flow-arrow">
              <ArrowRight />
            </div>

            <FlowCard
              icon={<LockKeyhole />}
              title="Decision"
              text="Policy determines the final action."
            />
          </div>
        </section>

        <section className="capabilities">
          <Capability
            number="01"
            title="Multi-model judging"
            text="Independent evaluator models assess the same AI response."
          />

          <Capability
            number="02"
            title="Privacy protection"
            text="Detect sensitive information before it becomes a data leak."
          />

          <Capability
            number="03"
            title="Policy-driven control"
            text="Convert risk signals into configurable enterprise actions."
          />

          <Capability
            number="04"
            title="Explainable governance"
            text="Every decision is supported by scores, reasons and audit records."
          />
        </section>
      </main>

      <footer>
        <span>CONTROLPLANE</span>
        <span>AI GOVERNANCE PLATFORM · V1</span>
      </footer>
    </div>
  );
}

function FlowCard({ icon, title, text }) {
  return (
    <div className="flow-card">
      <div className="flow-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{text}</p>
    </div>
  );
}

function Capability({ number, title, text }) {
  return (
    <div className="capability">
      <span className="capability-number">{number}</span>
      <div>
        <h3>{title}</h3>
        <p>{text}</p>
      </div>
    </div>
  );
}

function EvaluationPage({ onBack }) {
  const [prompt, setPrompt] = useState("");
  const [applications, setApplications] = useState([]);
  const [selectedApplication, setSelectedApplication] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

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

  async function handleEvaluate() {
    if (!prompt.trim() || !selectedApplication) {
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await createEvaluation({
        application_id: Number(selectedApplication),
        prompt,
      });

      setResult(data.evaluation);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <nav className="navbar">
        <div className="brand">
          <div className="brand-mark">
            <ShieldCheck size={21} />
          </div>

          <div>
            <div className="brand-name">ControlPlane</div>
            <div className="brand-subtitle">AI GOVERNANCE</div>
          </div>
        </div>

        <button className="back-button" onClick={onBack}>
          ← Back to overview
        </button>
      </nav>

      <main className="evaluation-page">
        <div className="evaluation-header">
          <div className="hero-eyebrow">
            <span className="eyebrow-line" />
            RESPONSE EVALUATION
          </div>

          <h2>Evaluate an AI response</h2>

          <p>
            Send a prompt to your target AI and let ControlPlane
            independently evaluate the generated response.
          </p>
        </div>

        <section className="evaluation-card">
          <div className="form-group">
            <label>Target application</label>

            <select
              value={selectedApplication}
              onChange={(event) => setSelectedApplication(event.target.value)}
            >
              {applications.map((application) => (
                <option
                  key={application.id}
                  value={application.id}
                >
                  {application.name} · {application.model_name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Prompt</label>

            <textarea
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              placeholder="Enter the prompt you want the target AI to answer..."
              rows={8}
            />
          </div>

          <div className="evaluation-footer">
            <div className="evaluation-info">
              <span className="status-dot" />
              3 evaluator models · PII detection · Policy analysis
            </div>

            <button
              className="primary-button"
              disabled={
                !prompt.trim() ||
                !selectedApplication ||
                loading
              }
              onClick={handleEvaluate}
            >
              {loading ? "Evaluating..." : "Run evaluation"}
              {!loading && <ArrowRight size={18} />}
            </button>
          </div>
        </section>

        {error && (
          <div className="error-box">
            {error}
          </div>
        )}

        {result && (
          <section className="result-preview">
            <div className="section-label">EVALUATION RESULT</div>

            <div className="result-card">
              <div className="result-label">TARGET AI RESPONSE</div>

              <p>{result.ai_response}</p>

              <div className="result-meta">
                <span>Evaluation #{result.id}</span>
                <span>3 judges evaluated</span>
              </div>
            </div>

            {result.consensus && (
              <div className="consensus-card">
                <div className="result-label">CONSENSUS</div>

                <div className="consensus-grid">
                  <div className="consensus-stat">
                    <span>OVERALL RISK</span>
                    <strong>
                      {result.consensus.overall_risk.toFixed(2)}
                    </strong>
                  </div>
        
                  <div className="consensus-stat">
                    <span>CONFIDENCE</span>
                    <strong>
                      {(result.consensus.confidence * 100).toFixed(0)}%
                    </strong>
                  </div>
        
                  <div className="consensus-stat">
                    <span>RECOMMENDATION</span>
                    <strong>
                      {result.consensus.recommendation}
                    </strong>
                  </div>
        
                  <div className="consensus-stat">
                    <span>JUDGES</span>
                    <strong>
                      {result.consensus.judge_count}
                    </strong>
                  </div>
                </div>
              </div>
            )}
        
            {result.judge_results && (
              <div className="judges-section">
                <div className="result-label">JUDGE RESULTS</div>
        
                <div className="judge-list">
                  {result.judge_results.map((judge) => (
                    <div
                      className="judge-card"
                      key={judge.detector_name}
                    >
                      <div className="judge-header">
                        <span className="judge-name">
                          {judge.detector_name.replace("_", " ")}
                        </span>
        
                        <span className="judge-recommendation">
                          {judge.metadata.recommendation}
                        </span>
                      </div>
        
                      <div className="judge-score">
                        Risk: {judge.score.toFixed(2)}
                      </div>
        
                      <p>{judge.reason}</p>
        
                      <div className="judge-meta">
                        Confidence:{" "}
                        {(judge.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        <section className="evaluation-preview">
          <div className="section-label">EVALUATION PIPELINE</div>

          <div className="pipeline-row">
            <span>Groq Target</span>
            <ArrowRight size={16} />
            <span>Safety</span>
            <span>Truthfulness</span>
            <span>Fairness / Privacy</span>
            <ArrowRight size={16} />
            <strong>Consensus</strong>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;