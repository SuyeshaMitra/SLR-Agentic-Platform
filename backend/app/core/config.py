"""Configuration settings for SLR Agentic Platform"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SLR Agentic Platform"
    PROJECT_DESCRIPTION: str = "AI-powered Systematic Literature Review Platform"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # PubMed Configuration
    PUBMED_BASE_URL: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    PUBMED_DB: str = "pubmed"
    PUBMED_BATCH_SIZE: int = 100
    PUBMED_MAX_RESULTS: int = 10000
    PUBMED_RETMODE: str = "json"
    PUBMED_EMAIL: Optional[str] = "researcher@example.com"
    PUBMED_API_KEY: Optional[str] = None
    
    # ML Model Configuration
    BERT_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    SCREENING_BATCH_SIZE: int = 32
    SIMILARITY_THRESHOLD: float = 0.7
    ML_CONFIDENCE_THRESHOLD: float = 0.85
    
    # Database Configuration
    DATABASE_URL: Optional[str] = "postgresql://user:password@localhost/slr_db"
    NEO4J_URI: Optional[str] = "bolt://localhost:7687"
    NEO4J_USER: Optional[str] = "neo4j"
    NEO4J_PASSWORD: Optional[str] = "password"
    
    # Task Queue
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # S3 Configuration
    S3_BUCKET: Optional[str] = "slr-agentic-outputs"
    AWS_REGION: str = "us-east-1"
    
    # API Configuration
    ENABLE_CORS: bool = True
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
