"""
FastAPI Web Application for BGB RAG
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_engine import BGBQueryEngine

# Initialize FastAPI app
app = FastAPI(
    title="BGB RAG API",
    description="Query German Civil Code (BGB) using natural language",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize RAG engine (will be done on startup)
rag_engine: BGBQueryEngine = None


# Pydantic models
class QueryRequest(BaseModel):
    query: str = Field(..., description="The question to ask about German Civil Code (BGB)", min_length=1)
    top_k: int = Field(6, description="Number of sources to retrieve", ge=1, le=10)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "Wer erbt, wenn es kein Testament gibt?",
                    "top_k": 6
                }
            ]
        }
    }


class SourceDocument(BaseModel):
    section: str
    title: str
    content: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    num_sources: int


@app.on_event("startup")
async def startup_event():
    """Initialize the RAG engine on startup"""
    global rag_engine
    print("Initializing BGB RAG Engine...")
    try:
        rag_engine = BGBQueryEngine()
        rag_engine.initialize()
        print("✓ RAG Engine initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing RAG engine: {e}")
        print("API will not function properly without the RAG engine.")
        # In production, you might want to fail startup here
        # raise e


@app.get("/")
async def root():
    """Serve the chat interface"""
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": "BGB RAG API",
        "version": "1.0.0",
        "description": "Query German Civil Code (BGB) using natural language",
        "endpoints": {
            "POST /query": "Submit a question about German Civil Code",
            "GET /health": "Check API health status",
            "GET /docs": "Interactive API documentation",
            "GET /": "Chat interface"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    if rag_engine is None:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")

    return {
        "status": "healthy",
        "rag_engine": "initialized"
    }


@app.post("/query", response_model=QueryResponse)
async def query_bgb(request: QueryRequest):
    """
    Query the BGB RAG system

    Submit a question about German Civil Code (BGB) and receive an answer
    with citations to relevant BGB paragraphs.
    """
    if rag_engine is None:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized. Please check server logs."
        )

    try:
        # Override top_k if specified in request
        if request.top_k != 6:
            rag_engine.top_k = request.top_k

        # Query the RAG engine
        result = rag_engine.query(request.query)

        # Convert to response model
        sources = [
            SourceDocument(
                section=source["section"],
                title=source["title"],
                content=source["content"]
            )
            for source in result["sources"]
        ]

        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            num_sources=result["num_sources"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
