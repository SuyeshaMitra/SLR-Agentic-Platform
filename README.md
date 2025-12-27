# SLR Agentic Platform - Automated Systematic Literature Review

An **enterprise-grade, production-ready platform** for automating systematic literature reviews using AI-powered multi-layer screening with PubMed integration and Hugging Face language models.

## 🎯 Features

✅ **Agentic Conversational Interface** - React-based chat UI for natural language literature review criteria  
✅ **PubMed API Integration** - Automated article fetching with rich metadata  
✅ **Hugging Face Models** - Zero-shot & fine-tuned BERT/SBERT for screening  
✅ **Multi-Layer Screening**:
   - Rule-based filtering (publication type, year, disease keywords)
   - ML classification (sklearn + Hugging Face transformers)
   - Semantic similarity scoring (sentence-transformers + FAISS)
✅ **Async Job Processing** - Celery + Redis for scalable parallel execution  
✅ **Performance Metrics** - Precision, recall, F1-score with confidence tracking  
✅ **Excel Export** - Results with decision rationale and layer attribution  
✅ **Docker Support** - Production-ready containerization  

## 🏗️ Architecture

```
User (Web Browser)
    ↓
React Agentic UI (TypeScript/Vite)
    ↓ HTTP REST API
FastAPI Backend (Python)
    ↓ Celery Task Queue
Redis Broker
    ↓
Celery Worker(s)
    ├─ PubMed API Integration
    │  └─ Fetch articles with rich metadata
    ├─ Data Ingestion Pipeline
    │  └─ CSV/Excel/API sources
    ├─ Deduplication Engine
    │  └─ FAISS semantic similarity
    ├─ Disease Validation (Rules)
    ├─ Multi-Layer Screening
    │  ├─ Rule-Based Filtering
    │  ├─ HF Zero-Shot Classification
    │  ├─ BERT Fine-Tuned Classifier
    │  └─ Semantic Similarity Scoring
    ├─ Metrics Calculation
    └─ Excel/JSON Export
    ↓
Artifacts (Excel + JSON results)
```

## 📋 Project Structure

```
slr-agentic-platform/
├── backend/                    # FastAPI + ML Backend
│   ├── app/
│   │   ├── main.py            # FastAPI app
│   │   ├── api/
│   │   │   └── routes_slr.py  # API endpoints
│   │   ├── core/
│   │   │   ├── config.py      # Settings
│   │   │   └── celery_app.py  # Celery setup
│   │   ├── services/
│   │   │   ├── pubmed_api.py  # PubMed integration
│   │   │   ├── ingestion.py
│   │   │   ├── deduplication.py
│   │   │   ├── screening.py   # ML screening
│   │   │   ├── metrics.py
│   │   │   └── persistence.py
│   │   └── ml_models/
│   │       ├── hf_classifier.py # Hugging Face models
│   │       ├── bert_screening.py
│   │       └── ensemble.py
│   ├── celery_worker.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/                   # React + TypeScript UI
│   ├── src/
│   │   ├── App.tsx            # Main agentic UI
│   │   ├── api.ts             # API client
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MetricsPanel.tsx
│   │   │   └── StatusIndicator.tsx
│   │   └── styles/
│   └── package.json
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── README.md                   # This file
└── requirements-all.txt
```

## 🚀 Quick Start (3 Steps)

### Step 1: Clone & Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your PubMed credentials
```

### Step 2: Start Services

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: FastAPI
uvicorn app.main:app --reload --port 8000

# Terminal 3: Celery Worker
celery -A app.core.celery_app.celery_app worker -l info -Q slr

# Terminal 4 (Optional): Flower Monitoring
celery -A app.core.celery_app.celery_app flower
```

### Step 3: Start Frontend

```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:5173
```

## 📖 API Endpoints

### Start SLR Job
```http
POST /api/v1/slr/start
Content-Type: application/json

{
  "disease": "PCOS",
  "population": "Women of reproductive age",
  "study_type": "randomized controlled trial",
  "max_results": 200,
  "filters": {
    "min_year": 2018,
    "max_year": 2024
  }
}

Response:
{
  "job_id": "abc123def456"
}
```

### Check Job Status
```http
GET /api/v1/slr/status/abc123def456

Response:
{
  "status": "COMPLETED|RUNNING|FAILED|PENDING",
  "message": "SLR job completed successfully",
  "precision": 0.92,
  "recall": 0.88,
  "f1": 0.90,
  "total_articles_found": 150,
  "after_dedup": 145,
  "included": 35,
  "excluded": 105
}
```

## 🤖 ML Models Integration

### Hugging Face Zero-Shot Classification
- **Model**: `facebook/bart-large-mnli`
- **Purpose**: Classify articles without fine-tuning
- **Example**: Input article → Labels (relevant PCOS study, irrelevant) → Score

### Sentence Transformers (Semantic Similarity)
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Purpose**: Find semantically similar articles & compute relevance scores
- **Use Case**: Deduplication + Relevance scoring

### Fine-Tuned BERT (Optional)
- **Model**: `bert-base-uncased` (fine-tuned on domain-specific SLR data)
- **Purpose**: High-precision screening
- **Training**: Requires labeled dataset (~1000 articles)

## 📊 Output Example

### Screening Results (Excel Export)

| PMID | Title | Abstract | Disease_Match | Decision | Confidence | Layer |
|------|-------|----------|---|---|---|---|
| 123456 | PCOS Treatment Trial | Study about PCOS... | PCOS | INCLUDE | 0.94 | HF |
| 123457 | Diabetes Study | Study about diabetes... | PCOS | EXCLUDE | 0.87 | RULE |

### JSON Response
```json
{
  "metrics": {
    "precision": 0.92,
    "recall": 0.88,
    "f1": 0.90
  },
  "screening_summary": {
    "total_fetched": 150,
    "included_studies": 35,
    "excluded_studies": 105
  },
  "articles": [
    {
      "pmid": "123456",
      "title": "PCOS Treatment Study",
      "decision": "INCLUDE",
      "confidence": 0.94,
      "layer": "ML"
    }
  ]
}
```

## 🔧 Environment Variables

Create `backend/.env`:

```bash
# FastAPI
DEBUG=False

# PubMed
PUBMED_EMAIL=your-email@example.com
PUBMED_API_KEY=your_ncbi_api_key
PUBMED_TOOL=slr-agentic-platform

# Redis/Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Hugging Face
HF_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
HF_SCREENING_MODEL=bert-base-uncased

# Output
OUTPUT_DIR=./outputs
CACHE_DIR=./cache
```

## 🐳 Docker Deployment

```bash
cd docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 💾 How to Download

### Option 1: GitHub (Recommended)
```bash
git clone https://github.com/[your-username]/SLR-Agentic-Platform.git
cd SLR-Agentic-Platform
```

### Option 2: Download ZIP
1. Visit: https://github.com/[your-username]/SLR-Agentic-Platform
2. Click **Code** → **Download ZIP**
3. Extract and navigate to folder

### Option 3: Using GitHub CLI
```bash
gh repo clone [your-username]/SLR-Agentic-Platform
```

## 🧪 Testing

```bash
# Unit tests
pytest backend/tests/ -v

# Integration tests
pytest backend/tests/integration/ -v

# Load testing
locust -f backend/tests/load/locustfile.py
```

## 📚 Documentation

- **SETUP.md** - Detailed environment setup
- **ARCHITECTURE.md** - System design & data flow
- **API_REFERENCE.md** - Complete API documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

## 📄 License

MIT License - See LICENSE file

## 📞 Support

- **Issues**: GitHub Issues tab
- **Email**: support@slr-platform.dev
- **Documentation**: See docs/ folder

---

**Built with ❤️ using FastAPI, Celery, React, and Hugging Face**
