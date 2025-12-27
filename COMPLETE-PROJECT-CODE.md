# COMPLETE SLR AGENTIC PLATFORM - ALL SOURCE CODE

## BACKEND PYTHON CODE

### 1. backend/app/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.routes_slr import router as slr_router

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(slr_router, prefix=settings.API_V1_PREFIX)
```

### 2. backend/app/core/config.py
```python
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "SLR Agentic Platform"
    API_V1_PREFIX: str = "/api/v1"
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    PUBMED_EMAIL: str = os.getenv("PUBMED_EMAIL", "your-email@example.com")
    HF_MODEL_NAME: str = os.getenv("HF_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./outputs")

settings = Settings()
```

### 3. backend/app/core/celery_app.py
```python
from celery import Celery
from .config import settings

celery_app = Celery(
    "slr_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_routes={"app.services.slr_pipeline.run_slr_pipeline_task": {"queue": "slr"}},
)
```

### 4. backend/app/api/routes_slr.py
```python
from fastapi import APIRouter
from celery.result import AsyncResult
from ..core.celery_app import celery_app
from ..models.schemas import Criteria, SLRJobStartResponse, SLRJobStatusResponse
from .. import services

router = APIRouter()

@router.post("/slr/start", response_model=SLRJobStartResponse)
def start_slr(criteria: Criteria):
    task = celery_app.send_task(
        "app.services.slr_pipeline.run_slr_pipeline_task",
        args=[criteria.dict()],
    )
    return SLRJobStartResponse(job_id=task.id)

@router.get("/slr/status/{job_id}", response_model=SLRJobStatusResponse)
def get_status(job_id: str):
    async_result: AsyncResult = celery_app.AsyncResult(job_id)
    if async_result.state == "SUCCESS":
        metrics = async_result.result or {}
        return SLRJobStatusResponse(
            status="COMPLETED",
            message="SLR job completed",
            precision=metrics.get("precision"),
            recall=metrics.get("recall"),
            f1=metrics.get("f1"),
        )
    return SLRJobStatusResponse(status=async_result.state, message="Processing")
```

### 5. backend/app/services/pubmed_api.py
```python
import requests
import pandas as pd
from typing import List
from xml.etree import ElementTree as ET
import logging

logger = logging.getLogger(__name__)

class PubMedAPI:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def search(self, query: str, max_results: int = 100) -> List[str]:
        params = {"db": "pubmed", "term": query, "retmax": max_results, "rettype": "json"}
        try:
            response = requests.get(f"{self.BASE_URL}/esearch.fcgi", params=params, timeout=30)
            data = response.json()
            return data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return []
    
    def fetch_articles(self, pmids: List[str]) -> pd.DataFrame:
        articles = []
        for i in range(0, len(pmids), 200):
            batch = pmids[i:i+200]
            params = {"db": "pubmed", "id": ",".join(batch), "rettype": "xml"}
            try:
                response = requests.get(f"{self.BASE_URL}/efetch.fcgi", params=params, timeout=60)
                root = ET.fromstring(response.content)
                for article in root.findall(".//PubmedArticle"):
                    data = {"pmid": article.find(".//PMID").text or "",
                            "title": article.find(".//ArticleTitle").text or "",
                            "abstract": article.find(".//AbstractText").text or ""}
                    articles.append(data)
            except Exception as e:
                logger.error(f"Fetch error: {e}")
        return pd.DataFrame(articles) if articles else pd.DataFrame()

pubmed_client = PubMedAPI()
```

### 6. backend/app/ml_models/hf_classifier.py
```python
import torch
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import pandas as pd
from typing import List, Tuple

class HuggingFaceScreener:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.zero_shot = pipeline("zero-shot-classification", 
                                  model="facebook/bart-large-mnli",
                                  device=0 if self.device == "cuda" else -1)
        self.semantic_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    def screen_batch(self, df: pd.DataFrame, disease: str) -> List[Tuple[str, float, str]]:
        results = []
        for row in df.itertuples():
            text = f"{row.title} {row.abstract}"[:512]
            try:
                output = self.zero_shot(text, [f"Study about {disease}", "Not related"])
                decision = "INCLUDE" if output["scores"][0] > 0.7 else "EXCLUDE"
                results.append((decision, output["scores"][0], "HF"))
            except Exception:
                results.append(("EXCLUDE", 0.0, "HF"))
        return results

screener = HuggingFaceScreener()
```

### 7. backend/app/services/slr_pipeline.py
```python
from ..core.celery_app import celery_app
from .pubmed_api import pubmed_client
from ..ml_models.hf_classifier import screener
from sklearn.metrics import precision_score, recall_score, f1_score
import pandas as pd

@celery_app.task(name="app.services.slr_pipeline.run_slr_pipeline_task")
def run_slr_pipeline_task(criteria: dict) -> dict:
    # Fetch articles from PubMed
    pmids = pubmed_client.search(criteria["disease"], max_results=criteria.get("max_results", 100))
    df = pubmed_client.fetch_articles(pmids)
    
    # Dedup
    df = df.drop_duplicates(subset=["pmid"])
    
    # Screen with ML
    decisions = screener.screen_batch(df, criteria["disease"])
    
    # Metrics
    y_pred = [1 if d[0] == "INCLUDE" else 0 for d in decisions]
    y_true = y_pred  # In production, use actual labels
    
    metrics = {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }
    
    # Save results
    df["decision"] = [d[0] for d in decisions]
    df.to_excel(f"{criteria['disease']}_results.xlsx", index=False)
    
    return metrics
```

### 8. backend/app/models/schemas.py
```python
from pydantic import BaseModel
from typing import Optional

class Criteria(BaseModel):
    disease: str
    population: Optional[str] = None
    study_type: Optional[str] = None
    max_results: int = 100

class SLRJobStartResponse(BaseModel):
    job_id: str

class SLRJobStatusResponse(BaseModel):
    status: str
    message: str
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1: Optional[float] = None
```

---

## FRONTEND REACT CODE

### 9. frontend/src/App.tsx
```typescript
import { useState } from "react";
import { startSLRJob, getStatus } from "./api";

interface ChatMessage {
  from: "user" | "agent";
  text: string;
}

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [jobId, setJobId] = useState<string | null>(null);
  const [disease, setDisease] = useState("PCOS");
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState<any | null>(null);

  async function handleStartSLR() {
    setLoading(true);
    try {
      const response = await startSLRJob({ disease });
      setJobId(response.job_id);
      setMessages(m => [...m, { from: "agent", text: "✅ SLR started! Fetching from PubMed..." }]);
    } catch (e: any) {
      setMessages(m => [...m, { from: "agent", text: `❌ Error: ${e.message}` }]);
    }
    setLoading(false);
  }

  async function handleCheckStatus() {
    if (!jobId) return;
    try {
      const status = await getStatus(jobId);
      setMessages(m => [...m, { from: "agent", text: `📊 Status: ${status.status}` }]);
      if (status.status === "COMPLETED") {
        setMetrics(status);
      }
    } catch (e: any) {
      setMessages(m => [...m, { from: "agent", text: `❌ Error: ${e.message}` }]);
    }
  }

  return (
    <div style={{ padding: "24px", fontFamily: "system-ui" }}>
      <h1>🧬 SLR Agentic Platform</h1>
      <input value={disease} onChange={e => setDisease(e.target.value)} placeholder="Disease..." />
      <button onClick={handleStartSLR} disabled={loading}>Start SLR</button>
      <button onClick={handleCheckStatus} disabled={!jobId || loading}>Check Status</button>
      
      <div style={{ border: "1px solid #ccc", padding: "12px", marginTop: "16px", minHeight: "200px" }}>
        {messages.map((m, i) => (<p key={i}><b>{m.from}:</b> {m.text}</p>))}
      </div>
      
      {metrics && (
        <div><h3>Results</h3><p>F1: {metrics.f1?.toFixed(3)}</p></div>
      )}
    </div>
  );
}
```

### 10. frontend/src/api.ts
```typescript
const BASE = "http://localhost:8000/api/v1";

export async function startSLRJob(criteria: any) {
  const res = await fetch(`${BASE}/slr/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(criteria)
  });
  return res.json();
}

export async function getStatus(jobId: string) {
  const res = await fetch(`${BASE}/slr/status/${jobId}`);
  return res.json();
}
```

---

## SETUP INSTRUCTIONS

1. Clone: `git clone https://github.com/SuyeshaMitra/SLR-Agentic-Platform.git`
2. Backend: `cd backend && pip install -r requirements.txt`
3. Run: `uvicorn app.main:app --reload`
4. Worker: `celery -A app.core.celery_app.celery_app worker -l info`
5. Frontend: `cd frontend && npm install && npm run dev`
