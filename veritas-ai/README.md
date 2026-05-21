# VERITAS AI — Autonomous Banking Trust Intelligence Platform

<div align="center">

![VERITAS AI](https://img.shields.io/badge/VERITAS_AI-v1.0.0-blue?style=for-the-badge&logo=shield)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=nextdotjs)
![Ollama](https://img.shields.io/badge/Ollama-llama3.1:8b-orange?style=for-the-badge)

**Production-ready MVP for autonomous banking fraud detection, regulatory compliance, and explainable underwriting — powered entirely by local AI models.**

</div>

---

## 🚀 One-Command Setup

```bash
git clone <repo-url> veritas-ai
cd veritas-ai
chmod +x install.sh
./install.sh
```

Then open **http://localhost:3000** and login with `admin@veritas.ai / veritas123`

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│                  VERITAS AI Platform                │
├──────────────┬──────────────────────────────────────┤
│  Frontend    │  Next.js 14 + TypeScript + Tailwind  │
│  :3000       │  Framer Motion + Recharts            │
├──────────────┼──────────────────────────────────────┤
│  Backend     │  FastAPI + Python 3.11               │
│  :8000       │  JWT + RBAC + Rate Limiting           │
├──────────────┼──────────────────────────────────────┤
│  AI Layer    │  Ollama (llama3.1:8b) — LOCAL        │
│              │  LangGraph Agents                    │
│              │  BAAI/bge-small-en-v1.5 Embeddings  │
├──────────────┼──────────────────────────────────────┤
│  Databases   │  ChromaDB (vector store)             │
│              │  Neo4j Community Edition (graph)     │
│              │  Redis (real-time)                   │
├──────────────┼──────────────────────────────────────┤
│  ML Models   │  IsolationForest + XGBoost           │
│              │  Tesseract OCR + OpenCV              │
└──────────────┴──────────────────────────────────────┘
```

---

## ✨ Features

### 1. 📄 Document Upload System
- Drag-and-drop multi-file upload (PDF, PNG, JPG, TIFF)
- File preview and size validation
- Real-time upload progress
- Secure server-side storage

### 2. 🔍 OCR + Document Extraction
- Tesseract OCR for scanned documents
- pdfplumber for native PDF text extraction
- OpenCV image pre-processing (denoising, thresholding)
- Entity extraction: dates, amounts, PAN, names, account numbers
- Signature region detection

### 3. 🚨 Anomaly Detection Engine
- **IsolationForest** statistical anomaly detection
- **XGBoost** fraud classifier
- **Heuristic checks**: edit markers, metadata tampering, suspicious keywords, date inconsistencies
- Generates: Fraud Score (0-100), Trust Score, Risk Level, Flag Details

### 4. 📋 Regulatory Intelligence (RAG)
- RBI/SEBI regulations stored in ChromaDB
- RAG retrieval pipeline with BAAI/bge-small-en-v1.5 embeddings
- Auto-generates Measurable Action Points (MAPs)
- Compliance status tracking

### 5. 🕸 Knowledge Graph
- Neo4j Community Edition graph database
- NetworkX in-memory fallback
- Canvas-based force-directed visualization
- Nodes: borrowers, entities, collateral, transactions
- Detects: circular ownership, duplicate collateral, suspicious associations

### 6. 🤖 AI Underwriting Copilot
- LangGraph multi-step agent pipeline
- Ollama llama3.1:8b for narrative generation
- Explainable decision: APPROVE / REVIEW / REJECT
- Key risk factors + recommendations

### 7. ✅ Compliance Validation
- AI-powered evidence validation
- File upload for compliance proof
- RAG-augmented validation reasoning
- Actionable suggestions for non-compliant items

### 8. 📊 Real-Time Dashboard
- Fraud Risk Meter (animated SVG gauge)
- Trust Score (circular progress)
- 7-day risk trend chart (Recharts)
- Risk distribution bar chart
- Live alert feed
- Compliance heatmap

---

## 🛠 Manual Setup

### Prerequisites
- macOS (Apple Silicon) or Linux
- Python 3.11+
- Node.js 18+
- Homebrew (macOS)

### Step-by-step

```bash
# 1. Install system deps
brew install tesseract redis ollama node python@3.11

# 2. Pull Ollama model (~5GB)
ollama pull llama3.1:8b

# 3. Backend setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 4. Frontend setup
cd frontend && npm install && cd ..

# 5. Configure env
cp .env.example .env

# 6. Seed demo data
python3 scripts/seed_demo.py

# 7. Start services
redis-server --daemonize yes
ollama serve &
cd backend && uvicorn main:app --reload --port 8000 &
cd frontend && npm run dev
```

---

## 🐳 Docker Setup

```bash
docker-compose up -d
# Wait for all services to start (~3-5 min for Ollama model download)
open http://localhost:3000
```

---

## 📚 API Documentation

Interactive Swagger docs: **http://localhost:8000/docs**

Key endpoints:
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | JWT authentication |
| POST | `/documents/upload` | Multi-file upload |
| POST | `/anomaly/analyze/{id}` | Trigger AI analysis |
| GET | `/anomaly/results/{id}` | Get analysis results |
| GET | `/compliance/maps` | List MAPs |
| POST | `/compliance/validate/{id}` | AI compliance validation |
| GET | `/graph/data` | Knowledge graph |
| GET | `/risk/dashboard` | Dashboard metrics |
| GET | `/risk/underwriting/{id}` | Underwriting decision |

---

## 🔐 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@veritas.ai | veritas123 |
| Analyst | analyst@veritas.ai | analyst123 |
| Viewer | viewer@veritas.ai | viewer123 |

---

## 📁 Project Structure

```
veritas-ai/
├── frontend/           # Next.js 14 app (8 pages, 15+ components)
├── backend/            # FastAPI application
│   ├── api/            # Route handlers
│   ├── core/           # Config, security, database
│   ├── models/         # Pydantic schemas
│   ├── services/       # OCR, anomaly, vector store, graph
│   └── data/           # Regulations data
├── ai_agents/          # LangGraph agents (fraud, compliance, underwriting)
├── data/               # Demo docs, ChromaDB, uploads
├── scripts/            # Seed script
├── docker/             # Dockerfiles
├── docker-compose.yml
├── install.sh
└── requirements.txt
```

---

## 🤝 License

MIT — Built for hackathon demonstration. Not for production banking use without proper security auditing.
