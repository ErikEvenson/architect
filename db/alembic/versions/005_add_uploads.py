"""Add uploads table

Revision ID: 005
Revises: 004
Create Date: 2026-03-16

"""
from typing import Sequence, Union

from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS uploads (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            version_id UUID NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
            original_filename VARCHAR(500) NOT NULL,
            stored_filename VARCHAR(500) NOT NULL,
            content_type VARCHAR(255) NOT NULL DEFAULT 'application/octet-stream',
            file_size BIGINT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS ix_uploads_version_id ON uploads(version_id);

        CREATE TRIGGER uploads_updated_at
            BEFORE UPDATE ON uploads
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS uploads CASCADE;")
