"""Add pgvector extension and knowledge_embeddings table

Revision ID: 006
Revises: 005
Create Date: 2026-03-23

"""
from typing import Sequence, Union

from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;

        CREATE TABLE IF NOT EXISTS knowledge_embeddings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            source_file VARCHAR(500) NOT NULL,
            source_type VARCHAR(20) NOT NULL DEFAULT 'knowledge_file'
                CHECK (source_type IN ('knowledge_file', 'vendor_doc')),
            section VARCHAR(255) NOT NULL,
            checklist_item TEXT,
            priority VARCHAR(20)
                CHECK (priority IN ('critical', 'recommended', 'optional')),
            content TEXT NOT NULL,
            content_hash VARCHAR(64) NOT NULL,
            embedding vector(384) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE INDEX IF NOT EXISTS ix_knowledge_embeddings_source_file
            ON knowledge_embeddings(source_file);
        CREATE INDEX IF NOT EXISTS ix_knowledge_embeddings_source_type
            ON knowledge_embeddings(source_type);
        CREATE INDEX IF NOT EXISTS ix_knowledge_embeddings_priority
            ON knowledge_embeddings(priority);
        CREATE INDEX IF NOT EXISTS ix_knowledge_embeddings_content_hash
            ON knowledge_embeddings(content_hash);
        CREATE INDEX IF NOT EXISTS ix_knowledge_embeddings_vector
            ON knowledge_embeddings
            USING hnsw (embedding vector_cosine_ops);

        CREATE TRIGGER knowledge_embeddings_updated_at
            BEFORE UPDATE ON knowledge_embeddings
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)


def downgrade() -> None:
    op.execute("""
        DROP TABLE IF EXISTS knowledge_embeddings CASCADE;
        DROP EXTENSION IF EXISTS vector;
    """)
