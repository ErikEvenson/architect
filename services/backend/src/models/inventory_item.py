import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import GUID, Base, TimestampMixin, UUIDMixin


class InventoryItem(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "inventory_items"

    version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_type: Mapped[str] = mapped_column(String(50), nullable=False, server_default="custom")
    data: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    version = relationship("Version", back_populates="inventory_items")
