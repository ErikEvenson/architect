import uuid

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import GUID, Base, TimestampMixin, UUIDMixin


class Upload(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "uploads"

    version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(
        String(255), nullable=False, server_default="application/octet-stream"
    )
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)

    version = relationship("Version", back_populates="uploads")
