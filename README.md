# ControlPlane

## AI Safety & Governance Control Plane

ControlPlane is an AI governance layer that evaluates AI-generated responses before they are released to users.

It sits between a target AI application and its users and independently evaluates generated responses for:

- Safety risks
- Hallucination and factual inconsistency
- Bias
- Privacy / PII leakage
- Enterprise knowledge conflicts
- Policy violations

The system combines deterministic PII detection, retrieval-augmented verification, multiple independent LLM judges, consensus, risk aggregation, configurable policies, human review, controlled release, and auditability.

---

## 1. Problem

Enterprise AI systems can generate responses that are:

- Factually incorrect
- Inconsistent with internal company knowledge
- Biased or discriminatory
- Unsafe
- Leaking personally identifiable information
- Inappropriate for an application's risk policy

ControlPlane acts as an independent governance layer that evaluates the target model's response before it reaches the end user.

```text
USER
  |
  v
TARGET AI
  |
  v
CONTROLPLANE
  |
  +--> PII Detection
  |
  +--> RAG / Enterprise Knowledge Verification
  |
  +--> Independent LLM Judges
  |
  +--> Consensus Engine
  |
  +--> Risk Engine
  |
  +--> Policy Engine
  |
  +--> ALLOW / REVIEW / BLOCK
              |
              +--> REVIEW --> Human Review --> Approve/Edit/Reject
              |
              +--> ALLOW  --> Release
              |
              +--> BLOCK  --> Prevent Release
```

---

## 2. Solution Architecture

```text
+-------------------------------------------------------------+
|                         FRONTEND                            |
|                       React + Vite                          |
|                                                             |
| Overview | Evaluate | Human Review | History       |
+-----------------------------+-------------------------------+
                              |
                           REST API
                              |
                              v
+-------------------------------------------------------------+
|                         FLASK API                           |
|                                                             |
| Applications | Evaluations | Knowledge | Review | Policies |
+-----------------------------+-------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                    GOVERNANCE PIPELINE                      |
|                                                             |
| Target LLM -> PII -> RAG -> 3 LLM Judges                   |
|                              |                              |
|                              v                              |
|                       Consensus Engine                      |
|                              |                              |
|                              v                              |
|                         Risk Engine                         |
|                              |                              |
|                              v                              |
|                        Policy Engine                        |
|                              |                              |
|                    ALLOW / REVIEW / BLOCK                   |
+-----------------------------+-------------------------------+
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
        PostgreSQL         ChromaDB       LLM Providers
                                           Groq / Gemini /
                                           OpenRouter
```

---

## 3. Implementation Architecture

```text
backend/
|
+-- app/
|   |
|   +-- api/
|   |   +-- routes/
|   |   |   +-- evaluation.py
|   |   |   +-- knowledge.py
|   |   |   +-- applications.py
|   |   |   +-- policies.py
|   |   |   +-- review.py
|   |   |
|   |   +-- schemas/
|   |
|   +-- engines/
|   |   +-- consensus_engine.py
|   |   +-- risk_engine.py
|   |   +-- policy_engine.py
|   |
|   +-- services/
|   |   |
|   |   +-- llm/
|   |   |   +-- groq_service.py
|   |   |   +-- openrouter_service.py
|   |   |   +-- llm_judge.py
|   |   |
|   |   +-- judge/
|   |   |   +-- judge_factory.py
|   |   |   +-- judge_config.py
|   |   |   +-- groq_judge.py
|   |   |   +-- gemini_judge.py
|   |   |   +-- openrouter_judge.py
|   |   |
|   |   +-- pii/
|   |   |   +-- pii_detector.py
|   |   |
|   |   +-- rag/
|   |       +-- document_parser.py
|   |       +-- document_service.py
|   |       +-- embedding_service.py
|   |       +-- retrieval_service.py
|   |       +-- vector_store.py
|   |
|   +-- models/
|       +-- application.py
|       +-- evaluation.py
|       +-- knowledge_document.py
|       +-- knowledge_chunk.py
|       +-- policy.py
|       +-- audit_log.py
|       +-- feedback.py
|
+-- run.py
+-- requirements.txt
+-- .env
```

---

## 4. End-to-End Execution Flow

### 4.1 Target AI

```text
User Prompt
    |
    v
Target AI / Groq
    |
    v
Generated Response
```

The original response is stored internally for evaluation.

### 4.2 PII Detection

```text
Generated Response
       |
       v
PII Detector
       |
       +--> Email
       +--> Phone
       +--> IP Address
       |
       v
Privacy Risk Signal
```

Example:

```text
Input:
Contact me at test@example.com

Result:
has_pii = true
detected_types = ["email"]
```

PII detection is deterministic and independent from the LLM judges.

### 4.3 RAG Knowledge Verification

Users can upload PDF or TXT enterprise documents.

```text
Document
   |
   v
Document Parser
   |
   v
Text Extraction
   |
   v
Chunking
   |
   v
Embedding Model
   |
   v
ChromaDB
```

During evaluation:

```text
User Prompt
    |
    v
Query Embedding
    |
    v
ChromaDB Similarity Search
    |
    v
Top-K Knowledge Chunks
    |
    v
Truthfulness Judge
```

Example:

```text
Trusted enterprise knowledge:
Employees are entitled to 25 paid vacation days per year.

Target AI:
Employees receive 10 paid vacation days.

Result:
Potential factual conflict
        |
        v
Truthfulness risk
        |
        v
REVIEW
```

### 4.4 Independent LLM Judges

```text
                 +------------------+
                 |   Safety Judge   |
                 +--------+---------+
                          |
                 +--------v---------+
                 | Truthfulness     |
                 | Judge            |
                 | + RAG Evidence   |
                 +--------+---------+
                          |
                 +--------v---------+
                 | Fairness /       |
                 | Privacy Judge    |
                 +--------+---------+
                          |
                          v
                    Consensus
```

Each judge returns structured data:

```text
bias_score
hallucination_score
privacy_score
overall_risk
confidence
reason
recommendation
```

Recommendations:

```text
ALLOW
REVIEW
BLOCK
```

The judges run concurrently to reduce latency.

---

## 5. Consensus Engine

The Consensus Engine combines the independent judge results.

```text
Safety Judge
       Truthfulness Judge ---> Consensus Engine ---> Overall Risk
       /                                      Confidence
Fairness/Privacy Judge                       Recommendation
```

This reduces dependence on a single evaluator.

---

## 6. Risk Engine

Risk categories:

```text
Safety
Hallucination
Bias
Privacy
```

Risk levels:

```text
0.00 - 0.29  LOW
0.30 - 0.59  MEDIUM
0.60 - 0.79  HIGH
0.80 - 1.00  CRITICAL
```

The Risk Engine uses confidence-weighted aggregation for judge signals.

PII detection provides an independent deterministic privacy signal.

A judge recommendation of `REVIEW` is also treated as a governance signal rather than being hidden by an average score.

---

## 7. Policy Engine

The Policy Engine converts risk into a governance decision.

Example policy:

```text
PII:
BLOCK

Hallucination:
REVIEW

Bias:
REVIEW
```

The final decision is:

```text
ALLOW
REVIEW
BLOCK
```

Governance priority:

```text
BLOCK
  |
  v
REVIEW
  |
  v
Policy-based decision
  |
  v
ALLOW
```

A blocking judge recommendation has priority over review. A review recommendation or detected PII can force human review.

---

## 8. Human-in-the-Loop Governance

A response requiring review is held before release.

```text
AI Response
     |
     v
Risk Evaluation
     |
     v
REVIEW
     |
     v
Human Review Queue
     |
     +--------+---------+
     |        |         |
     v        v         v
  APPROVE    EDIT      REJECT
     |        |         |
     v        v         v
  Release  Release    Block
```

The reviewer can inspect:

- Original AI response
- Risk scores
- Judge results
- Judge explanations
- RAG evidence
- PII findings
- Policy decision
- Evaluation history

The backend also prevents another prompt from bypassing an unresolved review for the same application.

---

## 9. Audit and History

Governance actions are recorded.

```text
Evaluation
   |
   +--> Prompt
   +--> Target AI Response
   +--> Judge Results
   +--> RAG Evidence
   +--> PII Findings
   +--> Risk Assessment
   +--> Policy Decision
   +--> Human Review
   +--> Final Action
   +--> Audit Logs
```

This provides traceability for governance decisions.

---

## 10. Knowledge Base Architecture

```text
                 KNOWLEDGE BASE
                       |
                       v
              +-----------------+
              | Document Upload |
              +--------+--------+
                       |
                       v
              +-----------------+
              | Document Parser |
              +--------+--------+
                       |
                       v
              +-----------------+
              |     Chunking    |
              +--------+--------+
                       |
                       v
              +-----------------+
              |   Embeddings    |
              | all-MiniLM-L6-v2|
              +--------+--------+
                       |
                       v
              +-----------------+
              |    ChromaDB     |
              |   Vector Store  |
              +-----------------+
```

---

## 11. Technology Stack

### Frontend

```text
React
Vite
CSS
Lucide Icons
```

### Backend

```text
Python
Flask
Flask-Cors
Flask-SQLAlchemy
SQLAlchemy
PostgreSQL
```

### AI / LLM

```text
Target Model:
Groq

Judges:
Gemini
Groq
OpenRouter
```

The Judge Factory and configuration-based architecture allow additional providers to be added.

### RAG

```text
ChromaDB
Sentence Transformers
all-MiniLM-L6-v2
PyTorch
Transformers
```

### Governance

```text
PII Detection
Consensus Engine
Risk Engine
Policy Engine
Human Review
Audit Logging
```

---

## 12. Dependencies

Major backend dependencies:

```text
Flask
Flask-Cors
Flask-SQLAlchemy
SQLAlchemy
psycopg2-binary
OpenAI
ChromaDB
Sentence Transformers
PyTorch
Transformers
scikit-learn
NumPy
SciPy
python-dotenv
Gunicorn
```

The complete pinned dependency list is available in:

```text
backend/requirements.txt
```

Install all dependencies with:

```powershell
pip install -r requirements.txt
```

---

## 13. Environment Variables

Create:

```text
backend/.env
```

Example:

```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
DATABASE_URL=your_database_connection_string
```

Never commit `.env` or API keys to GitHub.

For production deployment, configure these values through the hosting provider's environment-variable system.

---

## 14. Project Structure

```text
Controlplane/
|
+-- backend/
|   +-- app/
|   +-- chroma_data/
|   +-- requirements.txt
|   +-- run.py
|   +-- .env
|
+-- frontend/
|   +-- src/
|   +-- public/
|   +-- package.json
|   +-- vite.config.js
|
+-- README.md
```

---

## 15. Local Execution Instructions

### Prerequisites

Install:

```text
Python 3.11+
Node.js
npm
PostgreSQL
Git
```

### Clone Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Controlplane
```

---

## 16. Backend Setup

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure environment variables:

```text
backend/.env
```

Start backend:

```powershell
python run.py
```

Backend:

```text
http://localhost:5000
```

---

## 17. Frontend Setup

Open another terminal:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Run:

```powershell
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## 18. Knowledge Base Execution

Open the Knowledge Base section of the application.

Upload:

```text
PDF
or
TXT
```

The system automatically:

```text
Upload
  |
  v
Parse
  |
  v
Chunk
  |
  v
Embed
  |
  v
Index in ChromaDB
```

The uploaded document becomes trusted enterprise knowledge for retrieval-based verification.

---

## 19. Example Governance Scenario

Enterprise policy:

```text
Employees are entitled to 25 paid vacation days per year.
```

Upload the policy into the Knowledge Base.

Submit:

```text
According to company policy, employees receive
10 paid vacation days per year.
```

Suppose the target AI responds:

```text
Employees receive 10 paid vacation days per year.
```

ControlPlane retrieves:

```text
Trusted Evidence:
Employees are entitled to 25 paid vacation days per year.
```

The Truthfulness Judge identifies the conflict.

```text
Target AI
   |
   | "10 paid days"
   v
RAG
   |
   | "25 paid days"
   v
Truthfulness Judge
   |
   v
REVIEW
   |
   v
Risk Engine
   |
   v
Policy Engine
   |
   v
Human Review
```

The unreviewed response is held and is not released to the end user.

---

## 20. Example PII Scenario

Target response:

```text
You can contact John at
john.doe@example.com
or +91 9876543210.
```

PII detector:

```text
has_pii: true

detected_types:
- email
- phone
```

Governance:

```text
PII
 |
 v
Privacy Risk
 |
 v
Policy
 |
 +--> REVIEW
 |
 +--> BLOCK
```

The configured application policy determines the final action.

---

## 21. Security & Governance Principles

### Independent Evaluation

The target model does not evaluate itself.

### Deterministic PII Detection

Privacy-sensitive patterns are checked independently from LLM reasoning.

### Retrieval Verification

Enterprise factual claims can be checked against trusted knowledge sources.

### Multiple Judges

Multiple independent evaluators reduce dependence on a single model.

### Confidence-Aware Decisions

Risk assessments include confidence information.

### Human Escalation

Uncertain or risky responses can be held for human review.

### Configurable Policies

Different applications can use different governance requirements.

### Auditability

Governance decisions and human actions are recorded.

### Fail-Safe Response Handling

Responses requiring review are not released until the review process is completed.

---

## 22. Why LLMs Are Not the Final Authority

ControlPlane deliberately does not rely exclusively on LLM reasoning.

```text
Component                 Responsibility
------------------------------------------------------------
Target LLM                Generate response

PII Detector              Deterministic privacy detection

RAG                       Retrieve trusted evidence

LLM Judges                Semantic risk evaluation

Consensus Engine          Combine evaluator outputs

Risk Engine               Calculate risk

Policy Engine             Apply governance rules

Human Review              Resolve uncertain/high-risk cases

Audit System              Record decisions
```

This separation prevents the target LLM from becoming the sole source of truth or governance authority.

---

## 23. Latency Optimization

The independent judges run concurrently.

Sequential:

```text
Judge 1
   |
Judge 2
   |
Judge 3
```

ControlPlane:

```text
             +--> Judge 1 --+
             |              |
Target ------+--> Judge 2 --+--> Consensus
             |              |
             +--> Judge 3 --+
```

This reduces total evaluation latency compared with purely sequential judge execution.

---

## 24. Extensibility

The architecture can be extended with:

```text
Additional LLM providers
        |
        v
Additional safety detectors
        |
        v
Advanced PII/entity detection
        |
        v
More enterprise data sources
        |
        v
Conversation-level evaluation
        |
        v
Agent/action governance
        |
        v
Advanced analytics
        |
        v
Continuous evaluation
```

---

## 25. Production Architecture

```text
                         USERS
                           |
                           v
                    +-------------+
                    |   Vercel    |
                    |  Frontend   |
                    +------+------+
                           |
                           v
                    +-------------+
                    | Flask API   |
                    |   Render    |
                    +------+------+
                           |
                           v
                 +--------------------+
                 | Governance Pipeline|
                 +---------+----------+
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
        PostgreSQL      ChromaDB     LLM APIs
                                      /  |                                     Groq Gemini OpenRouter
```

---

## 26. Deployment

Recommended prototype deployment:

```text
Frontend   -> Vercel
Backend    -> Render
Database   -> PostgreSQL
LLM APIs   -> Groq / Gemini / OpenRouter
Vector DB  -> ChromaDB
```

Production API keys must be configured using environment variables.

The local `chroma_data` directory should not be treated as permanent production storage. For a production-scale system, a persistent/vector database deployment should be used.

---

## 27. Prototype Scope

The prototype demonstrates:

```text
✓ AI response evaluation
✓ Multiple independent LLM judges
✓ PII detection
✓ Enterprise knowledge retrieval
✓ RAG-based factual verification
✓ Risk scoring
✓ Confidence scoring
✓ Configurable policies
✓ ALLOW / REVIEW / BLOCK decisions
✓ Human review
✓ Response editing
✓ Response approval/rejection
✓ Controlled release
✓ Audit logging
✓ Evaluation history
✓ Knowledge source management
```

The system is a proof-of-concept and is not intended to replace enterprise security, compliance, legal, or human governance processes.

---

## 28. Key Differentiator

Traditional AI applications often follow:

```text
User
 |
 v
AI
 |
 v
Response
```

ControlPlane introduces an independent governance layer:

```text
User
 |
 v
Target AI
 |
 v
+-----------------------------------+
|           CONTROLPLANE            |
|                                   |
| PII -> RAG -> Judges -> Risk      |
|                         |         |
|                       Policy      |
|                         |         |
|                   Human Review    |
+-----------------------------------+
 |
 v
Approved / Safe Response
```

The goal is not to build another AI assistant.

The goal is to build the **governance infrastructure around AI systems**.

---

## 29. Submission Links

Project:

```text
ControlPlane
AI Safety & Governance Control Plane
```

GitHub:

```text
https://github.com/Vansh4908/ControlPlane-ai.git
```

Live Demo:

```text
<YOUR_VERCEL_URL>
```

Backend:

```text
https://controlplane-ai-a760.onrender.com
```

Demo Video:

```text
<YOUR_DEMO_VIDEO_URL>
```

---

## 30. Submission Snapshot

```text
Team:
Binary_brains

Project:
ControlPlane-AI

Participant:
Vansh Rohit

GitHub:
https://github.com/Vansh4908/ControlPlane-ai.git

Backend:
https://controlplane-ai-a760.onrender.com
```

Frontend : https://control-plane-ai-gray.vercel.app

---

## 30. Conclusion

ControlPlane demonstrates how an enterprise can place an independent governance layer around generative AI systems.

Instead of assuming that a model's response is trustworthy:

```text
GENERATE
   |
   v
DETECT
   |
   v
RETRIEVE
   |
   v
EVALUATE
   |
   v
AGGREGATE
   |
   v
ASSESS RISK
   |
   v
APPLY POLICY
   |
   v
HUMAN REVIEW WHEN REQUIRED
   |
   v
RELEASE
   |
   v
AUDIT
```

This architecture provides a foundation for building safer, more explainable, policy-aware, and auditable enterprise AI systems.
