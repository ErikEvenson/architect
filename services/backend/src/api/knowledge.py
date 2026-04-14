import asyncio
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session, async_session
from src.services import embedding_service

logger = structlog.get_logger()

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# Knowledge directory is at the repo root, mounted or available at this path
# In Docker, we'll copy it into the image. In dev, it's relative.
KNOWLEDGE_DIR = Path(os.environ.get("KNOWLEDGE_DIR", "/app/knowledge"))


# --- Pydantic models ---


class KnowledgeFile(BaseModel):
    path: str
    name: str
    category: str


class KnowledgeTree(BaseModel):
    general: list[KnowledgeFile]
    providers: dict[str, list[KnowledgeFile]]
    patterns: list[KnowledgeFile]


class KnowledgeContent(BaseModel):
    path: str
    name: str
    content: str


class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=10, ge=1, le=50)
    min_score: float = Field(default=0.3, ge=0.0, le=1.0)
    exclude_files: list[str] = Field(default_factory=list)
    priority_filter: Optional[str] = None


class KnowledgeSearchResult(BaseModel):
    id: str
    source_file: str
    source_type: str
    section: str
    checklist_item: Optional[str] = None
    priority: Optional[str] = None
    content: str
    score: float


class KnowledgeSearchResponse(BaseModel):
    results: list[KnowledgeSearchResult]
    query: str
    total_results: int


class ReindexRequest(BaseModel):
    include_vendor_docs: bool = True
    include_uploads: bool = True
    force: bool = False
    timeout_seconds: Optional[float] = None


class ReindexResponse(BaseModel):
    status: str
    files_processed: int
    checklist_items_indexed: int
    vendor_docs_indexed: int
    uploads_indexed: int = 0
    duration_seconds: float
    errors: list[str] = Field(default_factory=list)


class ReindexProgress(BaseModel):
    phase: str
    chunks_processed: int
    total_chunks: int
    current_batch: int
    total_batches: int
    vendor_docs_fetched: int
    vendor_docs_total: int
    vendor_docs_failed: int = 0
    vendor_docs_failed_by_host: dict[str, int] = Field(default_factory=dict)
    uploads_processed: int
    uploads_total: int


class ReindexStatus(BaseModel):
    indexed: bool
    total_embeddings: int
    knowledge_file_count: int
    vendor_doc_count: int
    upload_count: int = 0
    last_indexed_at: Optional[datetime] = None
    reindexing: bool = False
    paused: bool = False
    reindex_started_at: Optional[float] = None
    reindex_timeout: Optional[float] = None
    reindex_last_result: Optional[ReindexResponse] = None
    reindex_last_error: Optional[str] = None
    progress: Optional[ReindexProgress] = None


# --- Endpoints ---


@router.get("", response_model=KnowledgeTree)
async def list_knowledge():
    """List all available knowledge files organized by category."""
    tree = KnowledgeTree(general=[], providers={}, patterns=[])

    # General
    general_dir = KNOWLEDGE_DIR / "general"
    if general_dir.exists():
        for f in sorted(general_dir.glob("*.md")):
            tree.general.append(KnowledgeFile(
                path=f"general/{f.name}",
                name=f.stem.replace("-", " ").title(),
                category="general",
            ))

    # Providers
    providers_dir = KNOWLEDGE_DIR / "providers"
    if providers_dir.exists():
        for provider_dir in sorted(providers_dir.iterdir()):
            if provider_dir.is_dir():
                files = []
                for f in sorted(provider_dir.glob("*.md")):
                    files.append(KnowledgeFile(
                        path=f"providers/{provider_dir.name}/{f.name}",
                        name=f.stem.replace("-", " ").title(),
                        category=provider_dir.name,
                    ))
                if files:
                    tree.providers[provider_dir.name] = files

    # Patterns
    patterns_dir = KNOWLEDGE_DIR / "patterns"
    if patterns_dir.exists():
        for f in sorted(patterns_dir.glob("*.md")):
            tree.patterns.append(KnowledgeFile(
                path=f"patterns/{f.name}",
                name=f.stem.replace("-", " ").title(),
                category="patterns",
            ))

    return tree


@router.post("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    request: KnowledgeSearchRequest,
    session: AsyncSession = Depends(get_session),
):
    """Semantic search across knowledge embeddings."""
    return await _do_search(
        query=request.query,
        top_k=request.top_k,
        min_score=request.min_score,
        exclude_files=request.exclude_files or None,
        priority_filter=request.priority_filter,
        session=session,
    )


@router.get("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge_get(
    q: str,
    top_k: int = 10,
    min_score: float = 0.4,
    priority: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """Semantic search via GET for clients that only support URL fetching."""
    return await _do_search(
        query=q,
        top_k=top_k,
        min_score=min_score,
        exclude_files=None,
        priority_filter=priority,
        session=session,
    )


async def _do_search(
    query: str,
    top_k: int,
    min_score: float,
    exclude_files: list[str] | None,
    priority_filter: str | None,
    session: AsyncSession,
) -> KnowledgeSearchResponse:
    """Shared search implementation for GET and POST endpoints."""
    status = await embedding_service.get_index_status(session)
    if not status["indexed"]:
        raise HTTPException(
            status_code=400,
            detail="Knowledge embeddings not indexed yet. Call POST /knowledge/reindex first.",
        )

    results = await embedding_service.search_knowledge(
        session=session,
        query=query,
        top_k=top_k,
        min_score=min_score,
        exclude_files=exclude_files,
        priority_filter=priority_filter,
    )

    return KnowledgeSearchResponse(
        results=[KnowledgeSearchResult(**r) for r in results],
        query=query,
        total_results=len(results),
    )


async def _run_reindex_background(
    knowledge_dir: Path,
    include_vendor_docs: bool,
    include_uploads: bool,
    force: bool,
):
    """Run reindex as a background task with its own DB session."""
    import src.services.embedding_service as es

    es._reindex_running = True
    es._reindex_cancelled = False
    es._reindex_paused = False
    es._reindex_started_at = time.time()
    es._reindex_last_error = None

    try:
        async with async_session() as session:
            result = await es.reindex_knowledge(
                session=session,
                knowledge_dir=knowledge_dir,
                include_vendor_docs=include_vendor_docs,
                include_uploads=include_uploads,
                force=force,
            )
            es._reindex_last_result = result
            logger.info("Background reindex finished", status=result["status"])
    except Exception as e:
        es._reindex_last_error = str(e)
        logger.error("Background reindex failed", error=str(e))
    finally:
        es._reindex_running = False
        es._reindex_paused = False


@router.post("/reindex")
async def reindex_knowledge(
    request: ReindexRequest = None,
):
    """Start re-indexing the knowledge library as a background task."""
    if request is None:
        request = ReindexRequest()

    task_state = embedding_service.get_reindex_task_state()
    if task_state["running"]:
        raise HTTPException(
            status_code=409,
            detail="Reindex already in progress.",
        )

    if request.timeout_seconds is not None:
        embedding_service.set_reindex_timeout(request.timeout_seconds)

    asyncio.create_task(_run_reindex_background(
        knowledge_dir=KNOWLEDGE_DIR,
        include_vendor_docs=request.include_vendor_docs,
        include_uploads=request.include_uploads,
        force=request.force,
    ))

    return {"status": "started", "message": "Reindex started in background."}


@router.post("/reindex/stop")
async def stop_reindex():
    """Cancel a running reindex task."""
    task_state = embedding_service.get_reindex_task_state()
    if not task_state["running"]:
        raise HTTPException(status_code=409, detail="No reindex in progress.")
    embedding_service.cancel_reindex()
    return {"status": "stopping", "message": "Cancel signal sent."}


@router.post("/reindex/pause")
async def pause_reindex():
    """Pause a running reindex task."""
    task_state = embedding_service.get_reindex_task_state()
    if not task_state["running"]:
        raise HTTPException(status_code=409, detail="No reindex in progress.")
    if task_state["paused"]:
        raise HTTPException(status_code=409, detail="Already paused.")
    embedding_service.pause_reindex()
    return {"status": "paused", "message": "Pause signal sent."}


@router.post("/reindex/resume")
async def resume_reindex():
    """Resume a paused reindex task."""
    task_state = embedding_service.get_reindex_task_state()
    if not task_state["running"]:
        raise HTTPException(status_code=409, detail="No reindex in progress.")
    if not task_state["paused"]:
        raise HTTPException(status_code=409, detail="Not paused.")
    embedding_service.resume_reindex()
    return {"status": "resumed", "message": "Resume signal sent."}


@router.post("/reindex/clear")
async def clear_index(
    session: AsyncSession = Depends(get_session),
):
    """Delete all embeddings from the index."""
    task_state = embedding_service.get_reindex_task_state()
    if task_state["running"]:
        raise HTTPException(
            status_code=409,
            detail="Cannot clear while reindex is in progress.",
        )

    from sqlalchemy import delete as sa_delete
    from src.models.knowledge_embedding import KnowledgeEmbedding

    result = await session.execute(sa_delete(KnowledgeEmbedding))
    await session.commit()
    deleted = result.rowcount

    # Clear last result so the UI doesn't show stale data
    import src.services.embedding_service as es
    es._reindex_last_result = None
    es._reindex_last_error = None

    logger.info("Cleared knowledge index", deleted=deleted)
    return {"status": "cleared", "deleted": deleted}


@router.post("/reindex/timeout")
async def set_timeout(seconds: Optional[float] = None):
    """Set or clear the reindex timeout."""
    embedding_service.set_reindex_timeout(seconds)
    return {"status": "ok", "timeout_seconds": seconds}


@router.get("/reindex/status", response_model=ReindexStatus)
async def get_reindex_status(
    session: AsyncSession = Depends(get_session),
):
    """Get current embedding index status, including background task state."""
    status = await embedding_service.get_index_status(session)
    task_state = embedding_service.get_reindex_task_state()

    last_result = None
    if task_state["last_result"]:
        last_result = ReindexResponse(**task_state["last_result"])

    progress = None
    if task_state["running"]:
        progress = ReindexProgress(**task_state["progress"])

    return ReindexStatus(
        **status,
        reindexing=task_state["running"],
        paused=task_state["paused"],
        reindex_started_at=task_state["started_at"],
        reindex_timeout=task_state["timeout"],
        reindex_last_result=last_result,
        reindex_last_error=task_state["last_error"],
        progress=progress,
    )


@router.get("/{path:path}", response_model=KnowledgeContent)
async def get_knowledge_file(path: str):
    """Read a specific knowledge file."""
    file_path = KNOWLEDGE_DIR / path

    # Prevent path traversal
    if not file_path.resolve().is_relative_to(KNOWLEDGE_DIR.resolve()):
        raise HTTPException(status_code=400, detail="Invalid path")

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Knowledge file not found")

    content = file_path.read_text(encoding="utf-8")
    name = file_path.stem.replace("-", " ").title()

    return KnowledgeContent(path=path, name=name, content=content)
