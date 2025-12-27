# SLR AGENTIC PLATFORM - COMPLETE FOLDER STRUCTURE

## Project Layout (Copy This Structure)

```
slr-agentic-platform/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI entry point
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                    # Settings & environment
│   │   │   ├── celery_app.py                # Celery task queue
│   │   │   └── logger.py                    # Logging configuration
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes_slr.py                # API endpoints
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── pubmed_api.py                # PubMed API service
│   │   │   ├── ingestion.py                 # Data ingestion service
│   │   │   ├── deduplication.py             # Deduplication service
│   │   │   ├── disease_validation.py        # Disease filtering
│   │   │   ├── screening.py                 # ML screening orchestrator
│   │   │   ├── metrics.py                   # Metrics calculation
│   │   │   ├── persistence.py               # Save results
│   │   │   └── slr_pipeline.py              # Main pipeline
│   │   │
│   │   ├── ml_models/
│   │   │   ├── __init__.py
│   │   │   ├── hf_classifier.py             # Hugging Face models
│   │   │   ├── bert_screening.py            # BERT fine-tuning
│   │   │   └── ensemble.py                  # Model ensemble
│   │   │
│   │   └── models/
│   │       ├── __init__.py
│   │       └── schemas.py                   # Pydantic schemas
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_pubmed.py                   # PubMed tests
│   │   ├── test_screening.py                # Screening tests
│   │   └── test_api.py                      # API tests
│   │
│   ├── celery_worker.py                     # Worker launcher
│   ├── requirements.txt                     # Dependencies
│   ├── .env.example                         # Environment template
│   └── .gitignore                           # Git ignore
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   │
│   ├── src/
│   │   ├── main.tsx                         # React entry
│   │   ├── App.tsx                          # Main app component
│   │   │
│   │   ├── api/
│   │   │   └── client.ts                    # API client
│   │   │
│   │   ├── components/
│   │   │   ├── AgenticInterface.tsx         # 🎯 Agentic Chat UI
│   │   │   ├── ChatMessage.tsx              # Message component
│   │   │   ├── StatusPanel.tsx              # Status display
│   │   │   ├── MetricsPanel.tsx             # Results display
│   │   │   └── InputForm.tsx                # Input form
│   │   │
│   │   ├── hooks/
│   │   │   ├── useChat.ts                   # Chat logic hook
│   │   │   └── useJob.ts                    # Job polling hook
│   │   │
│   │   └── styles/
│   │       ├── global.css                   # Global styles
│   │       ├── agentic.css                  # Agentic UI styles
│   │       └── variables.css                # CSS variables
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .gitignore
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── docs/
│   ├── API.md                               # API documentation
│   ├── SETUP.md                             # Setup guide
│   ├── ARCHITECTURE.md                      # Architecture
│   └── ML-MODELS.md                         # ML models guide
│
├── README.md                                # Main readme
├── PROJECT-STRUCTURE.md                     # This file
├── COMPLETE-PROJECT-CODE.md                 # All code
├── .gitignore
└── requirements-all.txt
```

## 📁 Key Folders Explained

### backend/app/core/ - Configuration & Setup
- **config.py**: Environment variables & settings
- **celery_app.py**: Celery task queue configuration
- **logger.py**: Logging setup

### backend/app/services/ - Business Logic (Separate Files)
- **pubmed_api.py**: Handles PubMed API calls
- **ingestion.py**: Data loading from Excel/CSV/PubMed
- **deduplication.py**: FAISS semantic deduplication
- **disease_validation.py**: Disease keyword filtering
- **screening.py**: Orchestrates ML screening
- **metrics.py**: Calculates precision/recall/F1
- **persistence.py**: Exports to Excel
- **slr_pipeline.py**: Main Celery task pipeline

### backend/app/ml_models/ - ML Models
- **hf_classifier.py**: Hugging Face zero-shot + SBERT
- **bert_screening.py**: Fine-tuned BERT classifier
- **ensemble.py**: Combines multiple models

### frontend/src/components/ - React UI
- **AgenticInterface.tsx**: 🎯 Main conversational UI
- **ChatMessage.tsx**: Message display
- **StatusPanel.tsx**: Job status
- **MetricsPanel.tsx**: Results metrics
- **InputForm.tsx**: Disease/criteria input

## 📋 File Creation Order

1. **Backend Setup**
   - backend/app/__init__.py
   - backend/app/main.py
   - backend/app/core/__init__.py
   - backend/app/core/config.py
   - backend/app/core/celery_app.py

2. **Services (Separate Files)**
   - backend/app/services/__init__.py
   - backend/app/services/pubmed_api.py
   - backend/app/services/ingestion.py
   - backend/app/services/deduplication.py
   - backend/app/services/disease_validation.py
   - backend/app/services/screening.py
   - backend/app/services/metrics.py
   - backend/app/services/persistence.py
   - backend/app/services/slr_pipeline.py

3. **ML Models**
   - backend/app/ml_models/__init__.py
   - backend/app/ml_models/hf_classifier.py
   - backend/app/ml_models/bert_screening.py

4. **API**
   - backend/app/api/__init__.py
   - backend/app/api/routes_slr.py

5. **Frontend (Separate Agentic Folder)**
   - frontend/src/main.tsx
   - frontend/src/App.tsx
   - frontend/src/components/AgenticInterface.tsx  ← Agentic UI
   - frontend/src/api/client.ts

## 🚀 Running the Project

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Worker
celery -A app.core.celery_app.celery_app worker -l info

# Frontend (in separate terminal)
cd frontend
npm install
npm run dev
```

## ✨ Each File Has One Responsibility

✅ pubmed_api.py - ONLY PubMed API calls
✅ screening.py - ONLY orchestrates ML models
✅ metrics.py - ONLY calculates metrics
✅ hf_classifier.py - ONLY Hugging Face models
✅ AgenticInterface.tsx - ONLY agentic chat UI
✅ routes_slr.py - ONLY REST API endpoints
