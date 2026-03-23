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
from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.knowledge_embedding import KnowledgeEmbedding
from src.services.knowledge_parser import (
    ParsedChunk,
    extract_vendor_doc_urls,
    parse_knowledge_directory,
    parse_vendor_doc_content,
)

logger = structlog.get_logger()

# Lazy-loaded ONNX session and tokenizer
_session = None
_tokenizer = None

MODEL_DIR = Path(os.environ.get("EMBEDDING_MODEL_DIR", "/app/model-cache/onnx"))


def get_model():
    """Lazy-load the ONNX Runtime session and tokenizer."""
    global _session, _tokenizer
    if _session is None:
        import onnxruntime as ort
        from tokenizers import Tokenizer

        model_path = MODEL_DIR / "model.onnx"
        tokenizer_path = MODEL_DIR / "tokenizer.json"

        _session = ort.InferenceSession(
            str(model_path),
            providers=["CPUExecutionProvider"],
        )
        _tokenizer = Tokenizer.from_file(str(tokenizer_path))
        _tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=128)
        _tokenizer.enable_truncation(max_length=128)
        logger.info("Loaded ONNX embedding model", model_dir=str(MODEL_DIR))
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


async def reindex_knowledge(
    session: AsyncSession,
    knowledge_dir: Path,
    include_vendor_docs: bool = True,
    force: bool = False,
) -> dict:
    """Re-index the knowledge library into vector embeddings.

    Returns a summary dict with counts and timing.
    """
    start_time = time.time()
    errors: list[str] = []

    # Parse all knowledge files
    chunks = parse_knowledge_directory(knowledge_dir)
    logger.info("Parsed knowledge files", chunk_count=len(chunks))

    # Fetch and parse vendor docs if requested
    vendor_chunks: list[ParsedChunk] = []
    vendor_doc_count = 0
    if include_vendor_docs:
        vendor_urls = extract_vendor_doc_urls(knowledge_dir)
        logger.info("Found vendor doc URLs", url_count=len(vendor_urls))

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            for url_info in vendor_urls:
                try:
                    resp = await client.get(url_info["url"])
                    if resp.status_code == 200:
                        content_type = resp.headers.get("content-type", "")
                        if "text" in content_type or "html" in content_type:
                            doc_chunks = parse_vendor_doc_content(
                                url=url_info["url"],
                                title=url_info["title"],
                                content=resp.text,
                            )
                            vendor_chunks.extend(doc_chunks)
                            vendor_doc_count += 1
                except Exception as e:
                    errors.append(f"Failed to fetch {url_info['url']}: {e}")
                    logger.warning(
                        "Failed to fetch vendor doc",
                        url=url_info["url"],
                        error=str(e),
                    )

    all_chunks = chunks + vendor_chunks

    if not all_chunks:
        return {
            "status": "completed",
            "files_processed": 0,
            "checklist_items_indexed": 0,
            "vendor_docs_indexed": 0,
            "duration_seconds": time.time() - start_time,
            "errors": errors,
        }

    if not force:
        # Check which chunks already exist by content_hash
        existing_hashes_result = await session.execute(
            select(KnowledgeEmbedding.content_hash)
        )
        existing_hashes = {row[0] for row in existing_hashes_result.fetchall()}

        new_chunks = [c for c in all_chunks if c.content_hash not in existing_hashes]
        # Remove embeddings whose hashes no longer exist
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
        # Force mode: delete all and re-embed everything
        await session.execute(delete(KnowledgeEmbedding))
        new_chunks = all_chunks

    if new_chunks:
        # Generate embeddings in small batches, committing each to limit memory
        batch_size = 32
        for i in range(0, len(new_chunks), batch_size):
            batch = new_chunks[i : i + batch_size]
            texts = [c.content for c in batch]
            embeddings = await embed_texts(texts)

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

            # Commit each batch and expire objects to free memory
            await session.commit()
            session.expire_all()
            del texts, embeddings, batch
            gc.collect()

            if (i // batch_size) % 10 == 0:
                logger.info(
                    "Reindex progress",
                    processed=min(i + batch_size, len(new_chunks)),
                    total=len(new_chunks),
                )

    duration = time.time() - start_time
    files_processed = len({c.source_file for c in all_chunks if c.source_type == "knowledge_file"})
    checklist_items = len([c for c in all_chunks if c.checklist_item is not None])

    logger.info(
        "Reindex completed",
        files_processed=files_processed,
        checklist_items=checklist_items,
        vendor_docs=vendor_doc_count,
        total_chunks=len(all_chunks),
        new_chunks=len(new_chunks),
        duration_seconds=round(duration, 2),
    )

    return {
        "status": "completed",
        "files_processed": files_processed,
        "checklist_items_indexed": checklist_items,
        "vendor_docs_indexed": vendor_doc_count,
        "duration_seconds": round(duration, 2),
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
        select(func.count()).select_from(KnowledgeEmbedding).where(
            KnowledgeEmbedding.source_type == "knowledge_file"
        )
    )
    knowledge_count = knowledge_count_result.scalar() or 0

    vendor_count_result = await session.execute(
        select(func.count()).select_from(KnowledgeEmbedding).where(
            KnowledgeEmbedding.source_type == "vendor_doc"
        )
    )
    vendor_count = vendor_count_result.scalar() or 0

    last_indexed_result = await session.execute(
        select(func.max(KnowledgeEmbedding.updated_at))
    )
    last_indexed = last_indexed_result.scalar()

    return {
        "indexed": total > 0,
        "total_embeddings": total,
        "knowledge_file_count": knowledge_count,
        "vendor_doc_count": vendor_count,
        "last_indexed_at": last_indexed.isoformat() if last_indexed else None,
    }
