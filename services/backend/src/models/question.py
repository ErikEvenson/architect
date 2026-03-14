import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import GUID, Base, TimestampMixin, UUIDMixin


class Question(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "questions"

    version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_text: Mapped[str] = mapped_column(nullable=False)
    answer_text: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="open", index=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False, server_default="requirements", index=True)

    version = relationship("Version", back_populates="questions")
