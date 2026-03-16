import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import GUID, Base, TimestampMixin, UUIDMixin


class Version(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "versions"
    __table_args__ = (
        UniqueConstraint("project_id", "version_number", name="uq_versions_project_version"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[str] = mapped_column(String(20), nullable=False)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="draft", index=True)
    notes: Mapped[str | None] = mapped_column(nullable=True)

    project = relationship("Project", back_populates="versions")
    artifacts = relationship("Artifact", back_populates="version", cascade="all, delete-orphan")
    adrs = relationship("ADR", back_populates="version", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="version", cascade="all, delete-orphan")
    coverage_items = relationship("CoverageItem", back_populates="version", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="version", cascade="all, delete-orphan")
