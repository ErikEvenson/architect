import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func, types
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class GUID(types.TypeDecorator):
    """Platform-independent UUID type. Uses PostgreSQL UUID, stores as String(36) on SQLite."""

    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid.UUID):
                return value
            return uuid.UUID(str(value))
        return value

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID

            return dialect.type_descriptor(UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
