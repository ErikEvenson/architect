import uuid

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import GUID, Base, TimestampMixin, UUIDMixin


class Artifact(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "artifacts"

    version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(20), nullable=False)
    detail_level: Mapped[str] = mapped_column(String(20), nullable=False, server_default="conceptual")
    engine: Mapped[str] = mapped_column(String(20), nullable=False)
    source_code: Mapped[str | None] = mapped_column(nullable=True)
    output_paths: Mapped[list] = mapped_column(JSON, nullable=False, server_default="[]")
    render_status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")
    render_error: Mapped[str | None] = mapped_column(nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    version = relationship("Version", back_populates="artifacts")
