import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.services import embedding_service

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
    force: bool = False


class ReindexResponse(BaseModel):
    status: str
    files_processed: int
    checklist_items_indexed: int
    vendor_docs_indexed: int
    duration_seconds: float
    errors: list[str] = Field(default_factory=list)


class ReindexStatus(BaseModel):
    indexed: bool
    total_embeddings: int
    knowledge_file_count: int
    vendor_doc_count: int
    last_indexed_at: Optional[datetime] = None


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


@router.post("/reindex", response_model=ReindexResponse)
async def reindex_knowledge(
    request: ReindexRequest = None,
    session: AsyncSession = Depends(get_session),
):
    """Re-index the knowledge library into vector embeddings."""
    if request is None:
        request = ReindexRequest()

    result = await embedding_service.reindex_knowledge(
        session=session,
        knowledge_dir=KNOWLEDGE_DIR,
        include_vendor_docs=request.include_vendor_docs,
        force=request.force,
    )

    return ReindexResponse(**result)


@router.get("/reindex/status", response_model=ReindexStatus)
async def get_reindex_status(
    session: AsyncSession = Depends(get_session),
):
    """Get current embedding index status."""
    status = await embedding_service.get_index_status(session)
    return ReindexStatus(**status)


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
