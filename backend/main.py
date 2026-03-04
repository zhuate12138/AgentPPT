"""AgentPPT Backend - Main Application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.v1 import projects, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    settings = get_settings()
    print(f"🚀 AgentPPT starting...")
    print(f"   Data directory: {settings.data_dir}")
    print(f"   LLM Provider: {settings.llm_provider}")
    
    # Ensure data directory exists
    from pathlib import Path
    data_dir = Path(settings.data_dir).resolve()
    (data_dir / "projects").mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Shutdown
    print("👋 AgentPPT shutting down...")


app = FastAPI(
    title="AgentPPT",
    description="Create and edit PPT using natural language with AI agents",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(projects.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AgentPPT",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)