"""Add coverage_items table

Revision ID: 003
Revises: 002
Create Date: 2026-03-14

"""
from typing import Sequence, Union

from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS coverage_items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            version_id UUID NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
            knowledge_file VARCHAR(255) NOT NULL,
            item_text TEXT NOT NULL,
            priority VARCHAR(20) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'addressed', 'deferred', 'na')),
            question_id UUID REFERENCES questions(id) ON DELETE SET NULL,
            reason TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS ix_coverage_items_version_id ON coverage_items(version_id);
        CREATE INDEX IF NOT EXISTS ix_coverage_items_status ON coverage_items(status);

        CREATE TRIGGER coverage_items_updated_at
            BEFORE UPDATE ON coverage_items
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS coverage_items CASCADE;")
