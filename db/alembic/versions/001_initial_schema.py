"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-13

"""
from typing import Sequence, Union

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Updated-at trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Clients
    op.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            slug VARCHAR(255) NOT NULL,
            logo_path VARCHAR(500),
            metadata JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE UNIQUE INDEX IF NOT EXISTS ix_clients_slug ON clients(slug);
        CREATE INDEX IF NOT EXISTS ix_clients_name ON clients(name);

        CREATE TRIGGER clients_updated_at
            BEFORE UPDATE ON clients
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)

    # Projects
    op.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            slug VARCHAR(255) NOT NULL,
            description TEXT,
            cloud_providers JSONB NOT NULL DEFAULT '[]',
            status VARCHAR(20) NOT NULL DEFAULT 'draft'
                CHECK (status IN ('draft', 'active', 'archived')),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_projects_client_slug UNIQUE (client_id, slug)
        );
        CREATE INDEX IF NOT EXISTS ix_projects_client_id ON projects(client_id);
        CREATE INDEX IF NOT EXISTS ix_projects_status ON projects(status);

        CREATE TRIGGER projects_updated_at
            BEFORE UPDATE ON projects
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)

    # Versions
    op.execute("""
        CREATE TABLE IF NOT EXISTS versions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            version_number VARCHAR(20) NOT NULL,
            label VARCHAR(255),
            status VARCHAR(20) NOT NULL DEFAULT 'draft'
                CHECK (status IN ('draft', 'review', 'approved', 'superseded')),
            notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_versions_project_version UNIQUE (project_id, version_number)
        );
        CREATE INDEX IF NOT EXISTS ix_versions_project_id ON versions(project_id);
        CREATE INDEX IF NOT EXISTS ix_versions_status ON versions(status);

        CREATE TRIGGER versions_updated_at
            BEFORE UPDATE ON versions
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)

    # Artifacts
    op.execute("""
        CREATE TABLE IF NOT EXISTS artifacts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            version_id UUID NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            artifact_type VARCHAR(20) NOT NULL
                CHECK (artifact_type IN ('diagram', 'document', 'pdf_report')),
            detail_level VARCHAR(20) NOT NULL DEFAULT 'conceptual'
                CHECK (detail_level IN ('conceptual', 'logical', 'detailed', 'deployment')),
            engine VARCHAR(20) NOT NULL
                CHECK (engine IN ('diagrams_py', 'd2', 'markdown', 'weasyprint')),
            source_code TEXT,
            output_paths JSONB NOT NULL DEFAULT '[]',
            render_status VARCHAR(20) NOT NULL DEFAULT 'pending'
                CHECK (render_status IN ('pending', 'rendering', 'success', 'error')),
            render_error TEXT,
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS ix_artifacts_version_id ON artifacts(version_id);
        CREATE INDEX IF NOT EXISTS ix_artifacts_version_type ON artifacts(version_id, artifact_type);
        CREATE INDEX IF NOT EXISTS ix_artifacts_version_sort ON artifacts(version_id, sort_order);

        CREATE TRIGGER artifacts_updated_at
            BEFORE UPDATE ON artifacts
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)

    # ADRs
    op.execute("""
        CREATE TABLE IF NOT EXISTS adrs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
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
            CONSTRAINT uq_adrs_project_number UNIQUE (project_id, adr_number)
        );
        CREATE INDEX IF NOT EXISTS ix_adrs_project_id ON adrs(project_id);
        CREATE INDEX IF NOT EXISTS ix_adrs_status ON adrs(status);

        CREATE TRIGGER adrs_updated_at
            BEFORE UPDATE ON adrs
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)

    # Questions
    op.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            question_text TEXT NOT NULL,
            answer_text TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'open'
                CHECK (status IN ('open', 'answered', 'deferred')),
            category VARCHAR(20) NOT NULL DEFAULT 'requirements'
                CHECK (category IN ('requirements', 'security', 'scaling', 'compliance', 'cost', 'operations')),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS ix_questions_project_id ON questions(project_id);
        CREATE INDEX IF NOT EXISTS ix_questions_project_status ON questions(project_id, status);
        CREATE INDEX IF NOT EXISTS ix_questions_category ON questions(category);

        CREATE TRIGGER questions_updated_at
            BEFORE UPDATE ON questions
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS questions CASCADE;")
    op.execute("DROP TABLE IF EXISTS adrs CASCADE;")
    op.execute("DROP TABLE IF EXISTS artifacts CASCADE;")
    op.execute("DROP TABLE IF EXISTS versions CASCADE;")
    op.execute("DROP TABLE IF EXISTS projects CASCADE;")
    op.execute("DROP TABLE IF EXISTS clients CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at();")
