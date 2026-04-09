"""Vector embedding service for knowledge library search.

Uses ONNX Runtime with the all-MiniLM-L6-v2 model for lightweight
embeddings (~300MB RAM vs ~3GB for PyTorch-backed sentence-transformers).
"""

import asyncio
import gc
import os
import time
from pathlib import Path

import httpx
import numpy as np
import structlog
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.knowledge_embedding import KnowledgeEmbedding
from src.services.knowledge_parser import (
    ParsedChunk,
    extract_vendor_doc_urls,
    is_indexable,
    parse_knowledge_directory,
    parse_upload_content,
    parse_vendor_doc_content,
)

logger = structlog.get_logger()

# Lazy-loaded ONNX session and tokenizer
_session = None
_tokenizer = None

# Reindex background task state
_reindex_running = False
_reindex_started_at: float | None = None
_reindex_last_result: dict | None = None
_reindex_last_error: str | None = None
_reindex_cancelled = False
_reindex_paused = False
_reindex_timeout: float | None = None
_reindex_progress: dict = {
    "phase": "idle",           # idle | parsing | fetching_vendor_docs | indexing_uploads | embedding | done
    "chunks_processed": 0,
    "total_chunks": 0,
    "current_batch": 0,
    "total_batches": 0,
    "vendor_docs_fetched": 0,
    "vendor_docs_total": 0,
    "uploads_processed": 0,
    "uploads_total": 0,
}

MODEL_DIR = Path(os.environ.get("EMBEDDING_MODEL_DIR", "/app/model-cache/onnx"))


EMBEDDING_WORKERS = int(os.environ.get("EMBEDDING_WORKERS", "2"))
EMBEDDING_BATCH_SIZE = int(os.environ.get("EMBEDDING_BATCH_SIZE", "64"))


def get_model():
    """Lazy-load the ONNX Runtime session and tokenizer."""
    global _session, _tokenizer
    if _session is None:
        import onnxruntime as ort
        from tokenizers import Tokenizer

        model_path = MODEL_DIR / "model.onnx"
        tokenizer_path = MODEL_DIR / "tokenizer.json"

        sess_options = ort.SessionOptions()
        sess_options.inter_op_num_threads = EMBEDDING_WORKERS
        sess_options.intra_op_num_threads = EMBEDDING_WORKERS
        sess_options.execution_mode = ort.ExecutionMode.ORT_PARALLEL

        _session = ort.InferenceSession(
            str(model_path),
            sess_options=sess_options,
            providers=["CPUExecutionProvider"],
        )
        _tokenizer = Tokenizer.from_file(str(tokenizer_path))
        _tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=128)
        _tokenizer.enable_truncation(max_length=128)
        logger.info(
            "Loaded ONNX embedding model",
            model_dir=str(MODEL_DIR),
            workers=EMBEDDING_WORKERS,
            batch_size=EMBEDDING_BATCH_SIZE,
        )
    return _session, _tokenizer


def _mean_pooling(token_embeddings: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    """Apply mean pooling to token embeddings using attention mask."""
    mask_expanded = np.expand_dims(attention_mask, axis=-1).astype(np.float32)
    sum_embeddings = np.sum(token_embeddings * mask_expanded, axis=1)
    sum_mask = np.clip(np.sum(mask_expanded, axis=1), a_min=1e-9, a_max=None)
    return sum_embeddings / sum_mask


def _normalize(embeddings: np.ndarray) -> np.ndarray:
    """L2-normalize embeddings."""
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / np.clip(norms, a_min=1e-9, a_max=None)


def _embed_texts_sync(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts using ONNX Runtime (sync)."""
    ort_session, tokenizer = get_model()

    encoded = tokenizer.encode_batch(texts)
    input_ids = np.array([e.ids for e in encoded], dtype=np.int64)
    attention_mask = np.array([e.attention_mask for e in encoded], dtype=np.int64)
    token_type_ids = np.zeros_like(input_ids, dtype=np.int64)

    outputs = ort_session.run(
        None,
        {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids,
        },
    )

    token_embeddings = outputs[0]
    pooled = _mean_pooling(token_embeddings, attention_mask)
    normalized = _normalize(pooled)

    return normalized.tolist()


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings in a thread to avoid blocking the event loop."""
    return await asyncio.to_thread(_embed_texts_sync, texts)


def get_reindex_task_state() -> dict:
    """Return the current reindex background task state."""
    return {
        "running": _reindex_running,
        "paused": _reindex_paused,
        "started_at": _reindex_started_at,
        "timeout": _reindex_timeout,
        "last_result": _reindex_last_result,
        "last_error": _reindex_last_error,
        "progress": dict(_reindex_progress),
    }


def cancel_reindex():
    """Signal the running reindex task to stop."""
    global _reindex_cancelled, _reindex_paused
    _reindex_cancelled = True
    _reindex_paused = False  # unpause so the loop can exit


def pause_reindex():
    """Signal the running reindex task to pause."""
    global _reindex_paused
    _reindex_paused = True


def resume_reindex():
    """Signal a paused reindex task to continue."""
    global _reindex_paused
    _reindex_paused = False


def set_reindex_timeout(seconds: float | None):
    """Set the timeout for the current or next reindex."""
    global _reindex_timeout
    _reindex_timeout = seconds


def _reset_progress():
    """Reset progress tracking to idle state."""
    global _reindex_progress
    _reindex_progress = {
        "phase": "idle",
        "chunks_processed": 0,
        "total_chunks": 0,
        "current_batch": 0,
        "total_batches": 0,
        "vendor_docs_fetched": 0,
        "vendor_docs_total": 0,
        "uploads_processed": 0,
        "uploads_total": 0,
    }


async def _check_signals(start_time: float) -> str | None:
    """Check cancel, pause, and timeout signals.

    Returns a status string if the task should stop, or None to continue.
    While paused, blocks until resumed or cancelled.
    """
    global _reindex_paused

    # Check cancellation
    if _reindex_cancelled:
        return "cancelled"

    # Check timeout
    if _reindex_timeout and (time.time() - start_time) >= _reindex_timeout:
        return "timed_out"

    # Handle pause: sleep in a loop until unpaused or cancelled
    while _reindex_paused:
        await asyncio.sleep(0.5)
        if _reindex_cancelled:
            return "cancelled"
        if _reindex_timeout and (time.time() - start_time) >= _reindex_timeout:
            return "timed_out"

    return None


async def _index_uploads(
    session: AsyncSession,
    start_time: float,
    errors: list[str],
) -> tuple[list[ParsedChunk], int]:
    """Read all uploaded files and parse indexable ones into chunks.

    Returns (chunks, files_indexed_count).
    """
    global _reindex_progress
    from src.models.upload import Upload
    from src.models.version import Version
    from src.models.project import Project
    from src.models.client import Client
    from src.config import settings

    # Query all uploads with their version/project/client for path resolution
    result = await session.execute(
        select(Upload, Version, Project, Client)
        .join(Version, Upload.version_id == Version.id)
        .join(Project, Version.project_id == Project.id)
        .join(Client, Project.client_id == Client.id)
    )
    rows = result.all()

    _reindex_progress["uploads_total"] = len(rows)
    logger.info("Found uploads to index", count=len(rows))

    chunks: list[ParsedChunk] = []
    files_indexed = 0

    for upload, version, project, client in rows:
        stop = await _check_signals(start_time)
        if stop:
            break

        if not is_indexable(upload.original_filename, upload.content_type):
            _reindex_progress["uploads_processed"] += 1
            continue

        # Resolve file path
        file_path = (
            Path(settings.output_dir)
            / client.slug
            / project.slug
            / version.version_number
            / "uploads"
            / str(upload.id)
            / upload.stored_filename
        )

        if not file_path.exists():
            _reindex_progress["uploads_processed"] += 1
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            if content.strip():
                source_label = f"upload:{upload.id}:{upload.original_filename}"
                file_chunks = parse_upload_content(
                    source_label=source_label,
                    filename=upload.original_filename,
                    content=content,
                )
                chunks.extend(file_chunks)
                files_indexed += 1
        except Exception as e:
            errors.append(f"Failed to read upload {upload.original_filename}: {e}")
            logger.warning(
                "Failed to read upload",
                upload_id=str(upload.id),
                filename=upload.original_filename,
                error=str(e),
            )

        _reindex_progress["uploads_processed"] += 1

    logger.info("Parsed uploads", files_indexed=files_indexed, chunks=len(chunks))
    return chunks, files_indexed


async def reindex_knowledge(
    session: AsyncSession,
    knowledge_dir: Path,
    include_vendor_docs: bool = True,
    include_uploads: bool = True,
    force: bool = False,
) -> dict:
    """Re-index the knowledge library into vector embeddings.

    Returns a summary dict with counts and timing.
    Respects cancel, pause, and timeout signals between batches.
    """
    global _reindex_progress

    start_time = time.time()
    errors: list[str] = []
    _reset_progress()

    # --- Phase: parsing ---
    _reindex_progress["phase"] = "parsing"

    chunks = parse_knowledge_directory(knowledge_dir)
    logger.info("Parsed knowledge files", chunk_count=len(chunks))

    stop = await _check_signals(start_time)
    if stop:
        return _build_result(stop, 0, 0, 0, start_time, errors)

    # --- Phase: fetching vendor docs (concurrent) ---
    vendor_chunks: list[ParsedChunk] = []
    vendor_doc_count = 0
    if include_vendor_docs:
        _reindex_progress["phase"] = "fetching_vendor_docs"
        vendor_urls = extract_vendor_doc_urls(knowledge_dir)
        _reindex_progress["vendor_docs_total"] = len(vendor_urls)
        logger.info("Found vendor doc URLs", url_count=len(vendor_urls))

        semaphore = asyncio.Semaphore(20)
        vendor_lock = asyncio.Lock()

        async def _fetch_one(http_client: httpx.AsyncClient, url_info: dict):
            nonlocal vendor_doc_count
            async with semaphore:
                if _reindex_cancelled:
                    return
                try:
                    resp = await http_client.get(url_info["url"])
                    if resp.status_code == 200:
                        content_type = resp.headers.get("content-type", "")
                        if "text" in content_type or "html" in content_type:
                            doc_chunks = parse_vendor_doc_content(
                                url=url_info["url"],
                                title=url_info["title"],
                                content=resp.text,
                            )
                            async with vendor_lock:
                                vendor_chunks.extend(doc_chunks)
                                vendor_doc_count += 1
                                _reindex_progress["vendor_docs_fetched"] = vendor_doc_count
                except Exception as e:
                    async with vendor_lock:
                        errors.append(f"Failed to fetch {url_info['url']}: {e}")
                    logger.warning(
                        "Failed to fetch vendor doc",
                        url=url_info["url"],
                        error=str(e),
                    )

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as http_client:
            tasks = [_fetch_one(http_client, url_info) for url_info in vendor_urls]
            await asyncio.gather(*tasks)

        stop = await _check_signals(start_time)
        if stop:
            return _build_result(stop, 0, 0, vendor_doc_count, 0, start_time, errors)

    # --- Phase: indexing uploads ---
    upload_chunks: list[ParsedChunk] = []
    uploads_indexed = 0
    if include_uploads:
        _reindex_progress["phase"] = "indexing_uploads"
        upload_chunks, uploads_indexed = await _index_uploads(session, start_time, errors)

        stop = await _check_signals(start_time)
        if stop:
            return _build_result(stop, 0, 0, vendor_doc_count, uploads_indexed, start_time, errors)

    all_chunks = chunks + vendor_chunks + upload_chunks

    if not all_chunks:
        _reindex_progress["phase"] = "done"
        return _build_result("completed", 0, 0, 0, 0, start_time, errors)

    # --- Phase: embedding ---
    _reindex_progress["phase"] = "embedding"

    if not force:
        existing_hashes_result = await session.execute(
            select(KnowledgeEmbedding.content_hash)
        )
        existing_hashes = {row[0] for row in existing_hashes_result.fetchall()}

        new_chunks = [c for c in all_chunks if c.content_hash not in existing_hashes]
        new_hashes = {c.content_hash for c in all_chunks}
        stale_hashes = existing_hashes - new_hashes
        if stale_hashes:
            await session.execute(
                delete(KnowledgeEmbedding).where(
                    KnowledgeEmbedding.content_hash.in_(stale_hashes)
                )
            )
            logger.info("Removed stale embeddings", count=len(stale_hashes))
    else:
        await session.execute(delete(KnowledgeEmbedding))
        new_chunks = all_chunks

    batch_size = EMBEDDING_BATCH_SIZE
    total_batches = (len(new_chunks) + batch_size - 1) // batch_size if new_chunks else 0
    _reindex_progress["total_chunks"] = len(new_chunks)
    _reindex_progress["total_batches"] = total_batches

    if new_chunks:
        # Pipelined: embed next batch while committing current batch
        batches = [
            new_chunks[i : i + batch_size]
            for i in range(0, len(new_chunks), batch_size)
        ]

        # Pre-compute first batch embeddings
        pending_embeddings = await embed_texts([c.content for c in batches[0]])

        for batch_idx, batch in enumerate(batches):
            stop = await _check_signals(start_time)
            if stop:
                files_processed = len({c.source_file for c in all_chunks if c.source_type == "knowledge_file"})
                checklist_items = len([c for c in all_chunks if c.checklist_item is not None])
                return _build_result(stop, files_processed, checklist_items, vendor_doc_count, uploads_indexed, start_time, errors)

            embeddings = pending_embeddings

            # Start embedding next batch concurrently with DB write
            next_embed_task = None
            if batch_idx + 1 < len(batches):
                next_texts = [c.content for c in batches[batch_idx + 1]]
                next_embed_task = asyncio.create_task(embed_texts(next_texts))

            for chunk, embedding in zip(batch, embeddings):
                db_embedding = KnowledgeEmbedding(
                    source_file=chunk.source_file,
                    source_type=chunk.source_type,
                    section=chunk.section,
                    checklist_item=chunk.checklist_item,
                    priority=chunk.priority,
                    content=chunk.content,
                    content_hash=chunk.content_hash,
                    embedding=embedding,
                )
                session.add(db_embedding)

            await session.commit()
            session.expire_all()
            gc.collect()

            # Await next batch embeddings (should already be done or nearly done)
            if next_embed_task is not None:
                pending_embeddings = await next_embed_task

            batch_num = batch_idx + 1
            _reindex_progress["current_batch"] = batch_num
            _reindex_progress["chunks_processed"] = min(
                batch_num * batch_size, len(new_chunks)
            )

            if batch_num % 10 == 0:
                logger.info(
                    "Reindex progress",
                    batch=batch_num,
                    total_batches=total_batches,
                    processed=_reindex_progress["chunks_processed"],
                    total=len(new_chunks),
                )

    _reindex_progress["phase"] = "done"

    files_processed = len({c.source_file for c in all_chunks if c.source_type == "knowledge_file"})
    checklist_items = len([c for c in all_chunks if c.checklist_item is not None])

    return _build_result("completed", files_processed, checklist_items, vendor_doc_count, uploads_indexed, start_time, errors)


def _build_result(
    status: str,
    files_processed: int,
    checklist_items: int,
    vendor_docs: int,
    uploads_indexed: int,
    start_time: float,
    errors: list[str],
) -> dict:
    duration = round(time.time() - start_time, 2)
    logger.info(
        f"Reindex {status}",
        files_processed=files_processed,
        checklist_items=checklist_items,
        vendor_docs=vendor_docs,
        uploads_indexed=uploads_indexed,
        duration_seconds=duration,
    )
    return {
        "status": status,
        "files_processed": files_processed,
        "checklist_items_indexed": checklist_items,
        "vendor_docs_indexed": vendor_docs,
        "uploads_indexed": uploads_indexed,
        "duration_seconds": duration,
        "errors": errors,
    }


async def search_knowledge(
    session: AsyncSession,
    query: str,
    top_k: int = 10,
    min_score: float = 0.3,
    exclude_files: list[str] | None = None,
    priority_filter: str | None = None,
) -> list[dict]:
    """Search knowledge embeddings by cosine similarity.

    Returns a list of dicts with embedding fields plus a similarity score.
    """
    query_embedding = (await embed_texts([query]))[0]

    # Build the query using pgvector cosine distance
    # cosine_distance = 1 - cosine_similarity, so we compute 1 - distance for score
    distance_expr = KnowledgeEmbedding.embedding.cosine_distance(query_embedding)
    score_expr = (1 - distance_expr).label("score")

    stmt = (
        select(KnowledgeEmbedding, score_expr)
        .where((1 - distance_expr) >= min_score)
    )

    if exclude_files:
        stmt = stmt.where(KnowledgeEmbedding.source_file.notin_(exclude_files))

    if priority_filter:
        stmt = stmt.where(KnowledgeEmbedding.priority == priority_filter)

    stmt = stmt.order_by(distance_expr).limit(top_k)

    result = await session.execute(stmt)
    rows = result.all()

    results = []
    for embedding_row, score in rows:
        results.append({
            "id": str(embedding_row.id),
            "source_file": embedding_row.source_file,
            "source_type": embedding_row.source_type,
            "section": embedding_row.section,
            "checklist_item": embedding_row.checklist_item,
            "priority": embedding_row.priority,
            "content": embedding_row.content,
            "score": round(float(score), 4),
        })

    return results


async def get_suggestions_for_text(
    session: AsyncSession,
    text: str,
    exclude_files: list[str] | None = None,
    top_k: int = 5,
    min_score: float = 0.4,
) -> list[dict]:
    """Get inline suggestions for a given text (e.g., a question answer).

    Returns lightweight suggestion dicts suitable for inline API responses.
    """
    results = await search_knowledge(
        session=session,
        query=text,
        top_k=top_k,
        min_score=min_score,
        exclude_files=exclude_files,
    )

    return [
        {
            "source_file": r["source_file"],
            "checklist_item": r["checklist_item"] or r["content"][:200],
            "priority": r["priority"],
            "score": r["score"],
        }
        for r in results
    ]


async def get_index_status(session: AsyncSession) -> dict:
    """Get the current state of the embedding index."""
    total_result = await session.execute(
        select(func.count()).select_from(KnowledgeEmbedding)
    )
    total = total_result.scalar() or 0

    knowledge_count_result = await session.execute(
        select(func.count(func.distinct(KnowledgeEmbedding.source_file))).where(
            KnowledgeEmbedding.source_type == "knowledge_file"
        )
    )
    knowledge_count = knowledge_count_result.scalar() or 0

    vendor_count_result = await session.execute(
        select(func.count(func.distinct(KnowledgeEmbedding.source_file))).where(
            KnowledgeEmbedding.source_type == "vendor_doc"
        )
    )
    vendor_count = vendor_count_result.scalar() or 0

    upload_count_result = await session.execute(
        select(func.count(func.distinct(KnowledgeEmbedding.source_file))).where(
            KnowledgeEmbedding.source_type == "upload"
        )
    )
    upload_count = upload_count_result.scalar() or 0

    last_indexed_result = await session.execute(
        select(func.max(KnowledgeEmbedding.updated_at))
    )
    last_indexed = last_indexed_result.scalar()

    return {
        "indexed": total > 0,
        "total_embeddings": total,
        "knowledge_file_count": knowledge_count,
        "vendor_doc_count": vendor_count,
        "upload_count": upload_count,
        "last_indexed_at": last_indexed.isoformat() if last_indexed else None,
    }
