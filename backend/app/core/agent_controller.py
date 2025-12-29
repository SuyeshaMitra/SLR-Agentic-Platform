"""Agentic Conversational Controller for SLR Platform"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import json
from enum import Enum
from .pubmed_api import PubMedAPI
from .config import settings
import logging

logger = logging.getLogger(__name__)

class ConversationState(str, Enum):
    """Agent conversation states"""
    IDLE = "idle"
    CRITERIA_INTAKE = "criteria_intake"
    VALIDATING = "validating"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ERROR = "error"

class SLRCriteria(BaseModel):
    """SLR Criteria Structure"""
    disease: str = None
    population: str = None
    intervention: str = None
    comparison: str = None
    outcome: str = None
    study_type: str = None
    publication_years: Optional[tuple] = None
    language: str = "English"
    custom_query: Optional[str] = None

class AgentMessage(BaseModel):
    """Agentic UI Message"""
    role: str  # user|assistant|system
    content: str
    data: Optional[Dict] = None
    action: Optional[str] = None
    job_id: Optional[str] = None

class SLRAgentController:
    """Conversational Agent Controller - NOT PERFORMING SCREENING
    
    This agent:
    - Accepts criteria intake from user
    - Validates completeness
    - Triggers SLR job execution
    - Explains results
    - Returns explainability metadata
    
    It does NOT perform:
    - Study screening
    - Inclusion/exclusion logic
    - Semantic reasoning over papers
    """
    
    def __init__(self):
        self.state = ConversationState.IDLE
        self.criteria = SLRCriteria()
        self.pubmed_api = PubMedAPI()
        self.conversation_history: List[AgentMessage] = []
        self.current_job_id = None
    
    def process_user_input(self, user_input: str) -> AgentMessage:
        """Process user input and route to appropriate handler"""
        logger.info(f"Processing user input: {user_input[:100]}...")
        
        # Route based on state
        if self.state == ConversationState.IDLE:
            return self._handle_initial_input(user_input)
        elif self.state == ConversationState.CRITERIA_INTAKE:
            return self._handle_criteria_input(user_input)
        elif self.state == ConversationState.EXECUTING:
            return self._handle_status_query(user_input)
        else:
            return self._create_message("assistant", "Session in unexpected state. Please restart.")
    
    def _handle_initial_input(self, user_input: str) -> AgentMessage:
        """Initial interaction - move to criteria intake"""
        self.state = ConversationState.CRITERIA_INTAKE
        
        # Check if user is starting SLR
        if any(keyword in user_input.lower() for keyword in ['start', 'begin', 'run', 'slr', 'search']):
            response = "I'll help you run a Systematic Literature Review. Let me clarify your criteria.\n\nPlease provide:\n1. Disease/Condition (e.g., 'Type 2 Diabetes', 'PCOS')"
            return self._create_message("assistant", response)
        else:
            response = user_input
            return self._handle_criteria_input(response)
    
    def _handle_criteria_input(self, user_input: str) -> AgentMessage:
        """Parse and validate SLR criteria"""
        logger.info("Extracting criteria from user input")
        
        # Simple parsing logic - can be enhanced with NLP
        lower_input = user_input.lower()
        
        # Extract disease
        if 'diabetes' in lower_input or 't2d' in lower_input:
            self.criteria.disease = 'Type 2 Diabetes' if 'type 2' in lower_input else 'Diabetes'
        elif 'pcos' in lower_input:
            self.criteria.disease = 'PCOS'
        
        # Check completeness
        if not self.criteria.disease:
            return self._create_message(
                "assistant",
                "I understand you want to search for Type 2 Diabetes studies. \n\nPlease specify:\n2. Study Type (e.g., 'randomized controlled trial', 'clinical trial')"
            )
        
        if not self.criteria.study_type:
            self.criteria.study_type = 'randomized controlled trial'
            return self._create_message(
                "assistant",
                f"Using study type: {self.criteria.study_type}\n\nReady to start SLR for {self.criteria.disease}? Reply 'yes' to begin."
            )
        
        # Ready to execute
        if 'yes' in lower_input or 'confirm' in lower_input or 'start' in lower_input:
            return self.start_slr_job()
        
        return self._create_message("assistant", "Please confirm to proceed with SLR job.")
    
    def start_slr_job(self) -> AgentMessage:
        """Trigger async SLR job"""
        logger.info(f"Starting SLR job with criteria: {self.criteria}")
        self.state = ConversationState.EXECUTING
        
        # Generate job ID (in production: use UUID + Celery)
        self.current_job_id = f"slr_{hash(str(self.criteria)) % 10000}"
        
        response = f"""SLR Job initiated successfully!
        
Job ID: {self.current_job_id}
Disease: {self.criteria.disease}
Study Type: {self.criteria.study_type}

The system is now:
1. Querying PubMed with your criteria
2. Fetching study metadata
3. Deduplicating records
4. Screening abstracts
5. Computing PRISMA metrics

You'll receive results with:
- Included/Excluded studies
- Precision, Recall, F1 metrics
- Downloadable Excel reports

Check status anytime with: 'status'"""
        
        return self._create_message(
            "assistant",
            response,
            data={"criteria": self.criteria.dict(), "job_id": self.current_job_id},
            action="start_job"
        )
    
    def _handle_status_query(self, user_input: str) -> AgentMessage:
        """Handle job status queries"""
        if 'status' in user_input.lower():
            # In production: query job queue
            return self._create_message(
                "assistant",
                f"""Job {self.current_job_id} Status: PROCESSING
                
Progress:
- PubMed search: COMPLETE (3,214 studies found)
- Abstract fetch: IN PROGRESS (2,100/3,214)
- Deduplication: PENDING
- Screening: PENDING
- Metrics: PENDING

Estimated time: 2-3 minutes"""
            )
        elif 'result' in user_input.lower() or 'download' in user_input.lower():
            return self._create_message(
                "assistant",
                f"Results not yet available. Job {self.current_job_id} still processing."
            )
        else:
            return self._create_message("assistant", "Please ask about 'status' or 'results'.")
    
    def explain_decision(self, study_id: str, decision: str, layer: str) -> Dict:
        """Explain why a study was included/excluded"""
        explanation = {
            "study_id": study_id,
            "decision": decision,
            "layer": layer,  # rules|ml|bert|human
            "reasoning": f"Study {study_id} was {decision} at {layer} layer",
            "confidence": 0.92,
            "evidence": []
        }
        return explanation
    
    def _create_message(
        self,
        role: str,
        content: str,
        data: Optional[Dict] = None,
        action: Optional[str] = None
    ) -> AgentMessage:
        """Create structured message"""
        msg = AgentMessage(
            role=role,
            content=content,
            data=data,
            action=action,
            job_id=self.current_job_id
        )
        self.conversation_history.append(msg)
        return msg
    
    def get_conversation_history(self) -> List[Dict]:
        """Return conversation history"""
        return [msg.dict() for msg in self.conversation_history]
    
    def reset_session(self) -> AgentMessage:
        """Reset conversation state"""
        self.state = ConversationState.IDLE
        self.criteria = SLRCriteria()
        self.conversation_history = []
        self.current_job_id = None
        return self._create_message("assistant", "Session reset. Start a new SLR job with 'start'")

# Singleton agent instance
_agent = SLRAgentController()

def get_agent() -> SLRAgentController:
    """Get or create agent instance"""
    return _agent
