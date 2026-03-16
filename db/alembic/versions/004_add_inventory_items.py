"""Add inventory_items table

Revision ID: 004
Revises: 003
Create Date: 2026-03-15

"""
from typing import Sequence, Union

from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS inventory_items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            version_id UUID NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            data_type VARCHAR(50) NOT NULL DEFAULT 'custom',
            data TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS ix_inventory_items_version_id ON inventory_items(version_id);
        CREATE INDEX IF NOT EXISTS ix_inventory_items_version_type ON inventory_items(version_id, data_type);

        CREATE TRIGGER inventory_items_updated_at
            BEFORE UPDATE ON inventory_items
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS inventory_items CASCADE;")
