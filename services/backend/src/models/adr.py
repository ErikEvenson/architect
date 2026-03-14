import uuid

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import GUID, Base, TimestampMixin, UUIDMixin


class ADR(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "adrs"
    __table_args__ = (
        UniqueConstraint("version_id", "adr_number", name="uq_adrs_version_number"),
    )

    version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    adr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="proposed", index=True)
    context: Mapped[str] = mapped_column(nullable=False)
    decision: Mapped[str] = mapped_column(nullable=False)
    consequences: Mapped[str] = mapped_column(nullable=False)
    superseded_by: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("adrs.id", ondelete="SET NULL"), nullable=True
    )

    version = relationship("Version", back_populates="adrs")
    superseding_adr = relationship("ADR", remote_side="ADR.id", foreign_keys=[superseded_by])
