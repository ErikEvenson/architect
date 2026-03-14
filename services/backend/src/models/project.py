import uuid

from sqlalchemy import JSON, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import GUID, Base, TimestampMixin, UUIDMixin


class Project(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("client_id", "slug", name="uq_projects_client_slug"),
    )

    client_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    cloud_providers: Mapped[list] = mapped_column(JSON, nullable=False, server_default="[]")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="draft", index=True)

    client = relationship("Client", back_populates="projects")
    versions = relationship("Version", back_populates="project", cascade="all, delete-orphan")
