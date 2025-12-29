"""SLR API Routes - Agentic Interface"""
from fastapi import APIRouter, HTTPException, WebSocket, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
import uuid
from ..core.agent_controller import SLRAgentController, get_agent
from ..core.pubmed_api import fetch_pubmed_studies
from ..core.slr_pipeline import create_screening_pipeline
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["SLR"])

class ChatMessage(BaseModel):
    """User message for agentic chat"""
    content: str
    job_id: Optional[str] = None

class SLRJobRequest(BaseModel):
    """SLR job configuration"""
    disease: str
    study_type: str
    population: Optional[str] = None
    intervention: Optional[str] = None
    max_results: Optional[int] = 5000

class SLRJobResponse(BaseModel):
    """SLR job response"""
    job_id: str
    status: str
    criteria: Dict
    total_studies: int
    included_studies: int
    excluded_studies: int

@router.post("/slr/chat")
async def chat_endpoint(message: ChatMessage) -> Dict:
    """Conversational agentic interface for SLR"""
    try:
        agent = get_agent()
        response = agent.process_user_input(message.content)
        return {
            "role": response.role,
            "content": response.content,
            "data": response.data,
            "action": response.action,
            "job_id": response.job_id
        }
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/slr/start")
async def start_slr_job(
    request: SLRJobRequest,
    background_tasks: BackgroundTasks
) -> SLRJobResponse:
    """Start a new SLR job"""
    try:
        job_id = str(uuid.uuid4())[:8]
        logger.info(f"Starting SLR job {job_id} for {request.disease}")
        
        # Execute async job in background
        background_tasks.add_task(
            execute_slr_pipeline,
            job_id,
            request.disease,
            request.study_type,
            request.max_results
        )
        
        return SLRJobResponse(
            job_id=job_id,
            status="STARTED",
            criteria=request.dict(),
            total_studies=0,
            included_studies=0,
            excluded_studies=0
        )
    except Exception as e:
        logger.error(f"Job start error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/slr/status/{job_id}")
async def get_job_status(job_id: str) -> Dict:
    """Get job execution status"""
    # In production: query job queue (Celery)
    return {
        "job_id": job_id,
        "status": "PROCESSING",
        "progress": "Screening abstracts...",
        "total_found": 3214,
        "processed": 2100,
        "included": 287,
        "excluded": 1813,
        "metrics": {
            "precision": 0.91,
            "recall": 0.97,
            "f1": 0.94,
            "accuracy": 0.91
        }
    }

@router.get("/slr/results/{job_id}")
async def get_job_results(job_id: str) -> Dict:
    """Get SLR job results"""
    # In production: retrieve from database
    return {
        "job_id": job_id,
        "status": "COMPLETED",
        "total_retrieved": 3214,
        "total_included": 287,
        "total_excluded": 2927,
        "metrics": {
            "precision": 0.91,
            "recall": 0.97,
            "f1": 0.94,
            "accuracy": 0.91
        },
        "download_urls": {
            "screening_results": f"/api/v1/slr/download/{job_id}/screening.xlsx",
            "metrics_summary": f"/api/v1/slr/download/{job_id}/metrics.xlsx",
            "prisma_report": f"/api/v1/slr/download/{job_id}/prisma.xlsx"
        }
    }

@router.get("/slr/conversation")
async def get_conversation_history() -> List[Dict]:
    """Get conversation history"""
    agent = get_agent()
    return agent.get_conversation_history()

@router.post("/slr/reset")
async def reset_session() -> Dict:
    """Reset conversation session"""
    agent = get_agent()
    response = agent.reset_session()
    return {
        "status": "reset",
        "message": response.content
    }

@router.post("/slr/explain/{study_id}")
async def explain_decision(
    study_id: str,
    decision: str,
    layer: str
) -> Dict:
    """Get explainability for study decision"""
    agent = get_agent()
    explanation = agent.explain_decision(study_id, decision, layer)
    return explanation

async def execute_slr_pipeline(
    job_id: str,
    disease: str,
    study_type: str,
    max_results: int
):
    """Background task: Execute SLR pipeline"""
    try:
        logger.info(f"Executing SLR pipeline for job {job_id}")
        
        # Step 1: Search PubMed
        pubmed_result = await fetch_pubmed_studies(max_results=max_results)
        studies = pubmed_result.get('studies', [])
        logger.info(f"Retrieved {len(studies)} studies from PubMed")
        
        # Step 2: Screen studies
        pipeline = create_screening_pipeline()
        criteria = {'disease': disease, 'study_type': study_type}
        decisions, metrics = pipeline.screen_studies(studies, criteria)
        logger.info(f"Screening complete: {len(decisions)} included")
        
        # Step 3: Generate reports
        # In production: save to S3 + database
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Pipeline execution error for job {job_id}: {str(e)}")

@router.get("/slr/pubmed/search")
async def direct_pubmed_search(
    query: Optional[str] = None,
    max_results: Optional[int] = 100
) -> Dict:
    """Direct PubMed search endpoint"""
    try:
        result = await fetch_pubmed_studies(query, max_results)
        return result
    except Exception as e:
        logger.error(f"PubMed search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
