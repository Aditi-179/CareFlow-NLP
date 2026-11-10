import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging

from app.config import settings, ROOT_DIR
from app.routes.chat import router as chat_router
from app.retrieval import get_vector_store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("CareFlow-NLP")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup & shutdown events:
    Initializes knowledge base indexing and warms up embedding engine.
    """
    logger.info("Initializing CareFlow NLP Knowledge Base & Vector Store...")
    try:
        vs = get_vector_store()
        stats = vs.get_stats()
        logger.info(f"Loaded {stats['total_documents']} documents into {stats['total_chunks']} chunks with {stats['indexed_vectors']} vectors.")
    except Exception as e:
        logger.error(f"Error during vector store initialization: {e}")
    yield
    logger.info("CareFlow NLP application shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS configuration
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes FIRST so they take precedence over frontend static routes
app.include_router(chat_router)

# Mount Frontend if dist exists (All-in-one Single Deployment)
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    logger.info(f"Serving compiled React frontend from {FRONTEND_DIST}")
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Serve exact file if it exists (e.g., favicon, robots.txt)
        requested_file = FRONTEND_DIST / full_path
        if full_path and requested_file.is_file():
            return FileResponse(requested_file)
        # Otherwise serve SPA index.html
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    async def root():
        return {
            "project": settings.PROJECT_NAME,
            "description": settings.PROJECT_DESCRIPTION,
            "version": settings.VERSION,
            "docs_url": "/docs",
            "api_endpoints": {
                "chat": "POST /api/chat",
                "categories": "GET /api/categories",
                "health": "GET /api/health",
                "knowledge_base": "GET /api/knowledge-base"
            }
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)

