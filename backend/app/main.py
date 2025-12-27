"""FastAPI entry point for SLR Agentic Platform"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.routes_slr import router as slr_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered Systematic Literature Review Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "slr-backend"}

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "SLR Agentic Platform",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Include routers
app.include_router(slr_router, prefix=settings.API_V1_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
