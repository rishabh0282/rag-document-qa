"""
FastAPI minimal API exposing upload, query, documents endpoints.
"""
from typing import List, Optional, Any, Dict
import os
import uuid
import logging
import json
from pathlib import Path
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.document_loader import DocumentLoader
from src.embeddings import EmbeddingManager
from src.vector_store import VectorStore
from utils.preprocessing import chunk_text, clean_text

logger = logging.getLogger(__name__)
app = FastAPI(title="RAG Document QA")

# CORS middleware - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory registry
DOCS: Dict[str, Dict[str, Any]] = {}
EM: Optional[EmbeddingManager] = None  # Lazy initialization
VS: Optional[VectorStore] = None


def get_em():
    """Get EmbeddingManager with lazy initialization."""
    global EM
    if EM is None:
        logger.info("Initializing EmbeddingManager...")
        EM = EmbeddingManager()
        logger.info("EmbeddingManager initialized successfully")
    return EM


class UploadResponse(BaseModel):
    id: str
    filename: str


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    try:
        logger.info(f"Uploading file: {file.filename}")
        # Use system temp directory instead of /tmp (works on Windows/Mac/Linux)
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}_{file.filename}")
        
        with open(temp_path, "wb") as fh:
            content = await file.read()
            logger.info(f"File size: {len(content)} bytes")
            fh.write(content)
        
        loader = DocumentLoader()
        doc = loader.load(temp_path)
        logger.info(f"Document loaded: {doc.filename}, text length: {len(doc.text)}")
        
        chunks = chunk_text(clean_text(doc.text))
        logger.info(f"Text chunked into {len(chunks)} chunks")
        
        em = get_em()
        logger.info(f"Computing embeddings for {len(chunks)} chunks...")
        embeddings = em.embed_batch(chunks)
        logger.info(f"Embeddings computed successfully")
        
        global VS
        if VS is None:
            dim = len(embeddings[0])
            logger.info(f"Creating VectorStore with dimension {dim}")
            VS = VectorStore(dim=dim)
        
        metadatas = [
            {
                "doc_id": doc.id,
                "filename": doc.filename,
                "chunk": i,
                "text": chunks[i][:500],
            }
            for i in range(len(chunks))
        ]
        VS.add(embeddings, metadatas)
        VS.save()
        DOCS[doc.id] = {"filename": doc.filename, "chunks": len(chunks)}
        logger.info(f"Document uploaded successfully: {doc.id}")
        return UploadResponse(id=doc.id, filename=doc.filename)
    except Exception as e:
        logger.exception("Upload failed")
        logger.error(f"Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/query")
async def query(request: Request):
    """Query documents with robust JSON parsing."""
    try:
        payload: Dict[str, Any] = {}
        try:
            payload = await request.json()
            logger.debug("Parsed JSON payload: %s", payload)
        except Exception as ex_json:
            logger.debug("JSON parse failed: %s", ex_json)
            try:
                form = await request.form()
                payload = dict(form)
                logger.debug("Parsed form payload: %s", payload)
            except Exception as ex_form:
                logger.debug("Form parse failed: %s", ex_form)
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        payload = json.loads(body_bytes.decode("utf-8"))
                        logger.debug("Parsed raw JSON payload: %s", payload)
                    except Exception as ex_raw:
                        raw_text = body_bytes.decode("utf-8", errors="replace")
                        logger.warning("Raw body not valid JSON: %s", raw_text)
                        raise HTTPException(
                            status_code=422,
                            detail=f"Invalid JSON body. Raw body: {raw_text}",
                        )
                else:
                    raise HTTPException(status_code=400, detail="Request body is empty")

        query_text = None
        if isinstance(payload, dict):
            query_text = payload.get("query") or payload.get("q")
            top_k = (
                int(payload.get("top_k", 5))
                if payload.get("top_k") is not None
                else 5
            )
        else:
            raise HTTPException(status_code=422, detail="Invalid request payload format")

        if not query_text or not isinstance(query_text, str):
            raise HTTPException(
                status_code=400,
                detail="`query` field is required and must be a string",
            )

        global VS
        if VS is None:
            raise HTTPException(
                status_code=400, detail="No documents indexed yet. Upload documents first."
            )

        em = get_em()
        logger.info(f"Computing embedding for query: {query_text}")
        q_emb = em.embed_text(query_text)
        results = VS.search(q_emb, top_k=top_k)
        logger.info(f"Query returned {len(results)} results")
        return {"query": query_text, "results": results}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Query failed")
        logger.error(f"Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/documents")
async def list_documents():
    return DOCS


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    if doc_id not in DOCS:
        raise HTTPException(status_code=404, detail="Not found")
    DOCS.pop(doc_id)
    return {"status": "deleted"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/init")
async def init():
    """Initialize embeddings model on demand."""
    try:
        em = get_em()
        return {"status": "ok", "message": "EmbeddingManager initialized successfully"}
    except Exception as e:
        logger.exception("Failed to initialize embeddings")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")


@app.get("/api")
async def api_info():
    """API info endpoint."""
    return {
        "message": "RAG Document QA API",
        "endpoints": {
            "health": "/health",
            "upload": "POST /upload",
            "query": "POST /query",
            "documents": "GET /documents",
            "delete": "DELETE /documents/{id}",
            "docs": "/docs",
        },
    }


# Serve frontend static files
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
logger.info(f"Frontend dist path: {frontend_dist}")
logger.info(f"Frontend dist exists: {frontend_dist.exists()}")

if frontend_dist.exists():
    logger.info("Mounting static files from frontend/dist")
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve SPA - return index.html for any non-API route."""
        # Don't intercept API routes
        if full_path.startswith(("api/", "upload", "query", "documents", "health", "init", "docs", "openapi")):
            # Let FastAPI handle these
            raise HTTPException(status_code=404)
        # For everything else (including root), serve index.html
        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Frontend not found")
else:
    logger.warning("Frontend dist folder not found!")