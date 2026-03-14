"""Move ADRs and questions from project to version level

Revision ID: 002
Revises: 001
Create Date: 2026-03-14

"""
from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing tables (user confirmed data can be deleted)
    op.execute("DROP TABLE IF EXISTS questions CASCADE;")
    op.execute("DROP TABLE IF EXISTS adrs CASCADE;")

    # Recreate ADRs with version_id instead of project_id
    op.execute("""
        CREATE TABLE IF NOT EXISTS adrs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            version_id UUID NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
            adr_number INTEGER NOT NULL,
            title VARCHAR(255) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'proposed'
                CHECK (status IN ('proposed', 'accepted', 'deprecated', 'superseded')),
            context TEXT NOT NULL,
            decision TEXT NOT NULL,
            consequences TEXT NOT NULL,
            superseded_by UUID REFERENCES adrs(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_adrs_version_number UNIQUE (version_id, adr_number)
        );
        CREATE INDEX IF NOT EXISTS ix_adrs_version_id ON adrs(version_id);
        CREATE INDEX IF NOT EXISTS ix_adrs_status ON adrs(status);

        CREATE TRIGGER adrs_updated_at
            BEFORE UPDATE ON adrs
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)

    # Recreate Questions with version_id instead of project_id
    op.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            version_id UUID NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
            question_text TEXT NOT NULL,
            answer_text TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'open'
                CHECK (status IN ('open', 'answered', 'deferred')),
            category VARCHAR(20) NOT NULL DEFAULT 'requirements'
                CHECK (category IN ('requirements', 'security', 'scaling', 'compliance', 'cost', 'operations')),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS ix_questions_version_id ON questions(version_id);
        CREATE INDEX IF NOT EXISTS ix_questions_version_status ON questions(version_id, status);
        CREATE INDEX IF NOT EXISTS ix_questions_category ON questions(category);

        CREATE TRIGGER questions_updated_at
            BEFORE UPDATE ON questions
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS questions CASCADE;")
    op.execute("DROP TABLE IF EXISTS adrs CASCADE;")
    # Would need to recreate with project_id — not implementing downgrade
