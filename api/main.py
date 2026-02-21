"""
SellSmart API — FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from services.database import connect_db, close_db
from services.qdrant_client import init_qdrant_collections, close_qdrant


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown."""
    # Startup
    await connect_db()
    await init_qdrant_collections()
    print("🚀 SellSmart API is ready")
    yield
    # Shutdown
    close_qdrant()
    await close_db()
    print("👋 SellSmart API shutting down")


app = FastAPI(
    title="SellSmart API",
    description="AI-powered sales intelligence platform for real estate brokers",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (for tracker.js, etc.)
import os
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from services.database import get_db
    from services.qdrant_client import get_qdrant

    # Check MongoDB
    try:
        db = get_db()
        await db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Check Qdrant
    try:
        qdrant = get_qdrant()
        qdrant.get_collections()
        qdrant_status = "connected"
    except Exception as e:
        qdrant_status = f"error: {str(e)}"

    return {
        "status": "ok" if db_status == "connected" and qdrant_status == "connected" else "degraded",
        "db": db_status,
        "qdrant": qdrant_status,
    }


# Import and register routers
from api.persona_router import router as persona_router
from api.microsite_router import router as microsite_router
from api.engagement_router import router as engagement_router
from api.trigger_router import router as trigger_router

app.include_router(persona_router)
app.include_router(microsite_router)
app.include_router(engagement_router)
app.include_router(trigger_router)
