from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin, UUIDMixin

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # Fallback for environments without pgvector (e.g., SQLite tests)
    from sqlalchemy import LargeBinary as Vector  # type: ignore[assignment]


class KnowledgeEmbedding(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_embeddings"

    source_file: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="knowledge_file"
    )
    section: Mapped[str] = mapped_column(String(255), nullable=False)
    checklist_item: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=False)
