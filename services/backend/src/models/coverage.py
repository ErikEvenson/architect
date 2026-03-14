import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import GUID, Base, TimestampMixin, UUIDMixin


class CoverageItem(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "coverage_items"

    version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    knowledge_file: Mapped[str] = mapped_column(String(255), nullable=False)
    item_text: Mapped[str] = mapped_column(nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)  # Critical, Recommended, Optional
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="pending"
    )  # pending, addressed, deferred, na
    question_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("questions.id", ondelete="SET NULL"), nullable=True
    )
    reason: Mapped[str | None] = mapped_column(nullable=True)  # reason for deferred/na

    version = relationship("Version", back_populates="coverage_items")
