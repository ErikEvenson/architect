"""Tests for knowledge file parser.

Tests the markdown parsing logic that extracts checklist items and sections
from knowledge library files. No database or embedding model required.
"""

import tempfile
from pathlib import Path

import pytest

from src.services.knowledge_parser import (
    ParsedChunk,
    extract_vendor_doc_urls,
    parse_knowledge_directory,
    parse_knowledge_file,
    parse_vendor_doc_content,
)

SAMPLE_KNOWLEDGE_FILE = """\
# API Design

## Scope

This file covers API design decisions.

## Checklist

- [ ] **[Critical]** What API style is used and why? (REST, GraphQL, gRPC)
- [ ] **[Recommended]** Is there an API gateway? (Kong, AWS API Gateway)
- [ ] **[Critical]** What versioning strategy is used? (URL path /v1/)
- [ ] **[Optional]** How is API documentation generated?

## Why This Matters

APIs are contracts. Once published, they are difficult to change.

## Common Decisions (ADR Triggers)

- **API style selection** — REST vs GraphQL vs gRPC
- **Versioning strategy** — URL path vs header

## See Also

- [security.md](security.md) -- security controls
- [Example Vendor Doc](https://example.com/docs/api-best-practices)
"""


@pytest.fixture
def knowledge_dir(tmp_path):
    """Create a temporary knowledge directory with sample files."""
    general_dir = tmp_path / "general"
    general_dir.mkdir()
    (general_dir / "api-design.md").write_text(SAMPLE_KNOWLEDGE_FILE)

    providers_dir = tmp_path / "providers" / "aws"
    providers_dir.mkdir(parents=True)
    (providers_dir / "compute.md").write_text(
        "# AWS Compute\n\n## Scope\n\nEC2, Lambda, ECS.\n\n## Checklist\n\n"
        "- [ ] **[Critical]** Which compute service? (EC2, Lambda, ECS, EKS)\n"
        "- [ ] **[Recommended]** Is auto-scaling configured?\n\n"
        "## Why This Matters\n\nCompute is the foundation.\n"
    )

    # Files that should be skipped
    (tmp_path / "README.md").write_text("# Knowledge Library")
    (tmp_path / "CONTRIBUTING.md").write_text("# Contributing")
    (tmp_path / "WORKFLOW.md").write_text("# Workflow")
    (tmp_path / "references.md").write_text("# References")

    return tmp_path


class TestParseKnowledgeFile:
    def test_extracts_checklist_items(self, knowledge_dir):
        file_path = knowledge_dir / "general" / "api-design.md"
        chunks = parse_knowledge_file(file_path, knowledge_dir)

        checklist_chunks = [c for c in chunks if c.checklist_item is not None]
        assert len(checklist_chunks) == 4

    def test_extracts_priorities(self, knowledge_dir):
        file_path = knowledge_dir / "general" / "api-design.md"
        chunks = parse_knowledge_file(file_path, knowledge_dir)

        checklist_chunks = [c for c in chunks if c.checklist_item is not None]
        priorities = [c.priority for c in checklist_chunks]
        assert priorities == ["critical", "recommended", "critical", "optional"]

    def test_extracts_sections(self, knowledge_dir):
        file_path = knowledge_dir / "general" / "api-design.md"
        chunks = parse_knowledge_file(file_path, knowledge_dir)

        section_chunks = [c for c in chunks if c.checklist_item is None]
        section_names = [c.section for c in section_chunks]
        assert "Scope" in section_names
        assert "Why This Matters" in section_names
        assert "Common Decisions (ADR Triggers)" in section_names

    def test_skips_see_also_section(self, knowledge_dir):
        file_path = knowledge_dir / "general" / "api-design.md"
        chunks = parse_knowledge_file(file_path, knowledge_dir)

        section_chunks = [c for c in chunks if c.checklist_item is None]
        section_names = [c.section for c in section_chunks]
        assert "See Also" not in section_names

    def test_sets_source_file_relative_path(self, knowledge_dir):
        file_path = knowledge_dir / "general" / "api-design.md"
        chunks = parse_knowledge_file(file_path, knowledge_dir)

        for chunk in chunks:
            assert chunk.source_file == "general/api-design.md"

    def test_sets_source_type(self, knowledge_dir):
        file_path = knowledge_dir / "general" / "api-design.md"
        chunks = parse_knowledge_file(file_path, knowledge_dir)

        for chunk in chunks:
            assert chunk.source_type == "knowledge_file"

    def test_generates_content_hash(self, knowledge_dir):
        file_path = knowledge_dir / "general" / "api-design.md"
        chunks = parse_knowledge_file(file_path, knowledge_dir)

        for chunk in chunks:
            assert len(chunk.content_hash) == 64  # SHA-256 hex

    def test_content_hash_is_deterministic(self, knowledge_dir):
        file_path = knowledge_dir / "general" / "api-design.md"
        chunks1 = parse_knowledge_file(file_path, knowledge_dir)
        chunks2 = parse_knowledge_file(file_path, knowledge_dir)

        for c1, c2 in zip(chunks1, chunks2):
            assert c1.content_hash == c2.content_hash

    def test_checklist_item_text_excludes_priority_tag(self, knowledge_dir):
        file_path = knowledge_dir / "general" / "api-design.md"
        chunks = parse_knowledge_file(file_path, knowledge_dir)

        checklist_chunks = [c for c in chunks if c.checklist_item is not None]
        for chunk in checklist_chunks:
            assert "[Critical]" not in chunk.checklist_item
            assert "[Recommended]" not in chunk.checklist_item
            assert "[Optional]" not in chunk.checklist_item


class TestParseKnowledgeDirectory:
    def test_parses_all_knowledge_files(self, knowledge_dir):
        chunks = parse_knowledge_directory(knowledge_dir)

        source_files = {c.source_file for c in chunks}
        assert "general/api-design.md" in source_files
        assert "providers/aws/compute.md" in source_files

    def test_skips_non_knowledge_files(self, knowledge_dir):
        chunks = parse_knowledge_directory(knowledge_dir)

        source_files = {c.source_file for c in chunks}
        assert "README.md" not in source_files
        assert "CONTRIBUTING.md" not in source_files
        assert "WORKFLOW.md" not in source_files
        assert "references.md" not in source_files

    def test_returns_all_checklist_items(self, knowledge_dir):
        chunks = parse_knowledge_directory(knowledge_dir)

        checklist_chunks = [c for c in chunks if c.checklist_item is not None]
        # 4 from api-design.md + 2 from compute.md
        assert len(checklist_chunks) == 6


class TestExtractVendorDocUrls:
    def test_extracts_http_urls(self, knowledge_dir):
        urls = extract_vendor_doc_urls(knowledge_dir)

        extracted_urls = [u["url"] for u in urls]
        assert "https://example.com/docs/api-best-practices" in extracted_urls

    def test_excludes_relative_links(self, knowledge_dir):
        urls = extract_vendor_doc_urls(knowledge_dir)

        extracted_urls = [u["url"] for u in urls]
        # security.md is a relative link, should not be extracted
        for url in extracted_urls:
            assert url.startswith("http")

    def test_includes_source_file(self, knowledge_dir):
        urls = extract_vendor_doc_urls(knowledge_dir)

        for url_info in urls:
            assert "source_file" in url_info

    def test_deduplicates_urls(self, knowledge_dir):
        # Add a second file with the same URL
        (knowledge_dir / "general" / "duplicate.md").write_text(
            "# Duplicate\n\n## Scope\n\nTest.\n\n"
            "See [Example](https://example.com/docs/api-best-practices)\n"
        )
        urls = extract_vendor_doc_urls(knowledge_dir)

        url_list = [u["url"] for u in urls]
        assert url_list.count("https://example.com/docs/api-best-practices") == 1


class TestParseVendorDocContent:
    def test_chunks_by_paragraph(self):
        content = "\n\n".join([f"Paragraph {i} with enough content to exceed limits." for i in range(5)])
        chunks = parse_vendor_doc_content(
            url="https://example.com/docs",
            title="Example Doc",
            content=content,
            max_chunk_size=60,
        )

        assert len(chunks) >= 2
        for chunk in chunks:
            assert chunk.source_type == "vendor_doc"
            assert chunk.source_file == "https://example.com/docs"

    def test_respects_max_chunk_size(self):
        content = "\n\n".join([f"Paragraph {i} with some content." for i in range(20)])
        chunks = parse_vendor_doc_content(
            url="https://example.com",
            title="Test",
            content=content,
            max_chunk_size=100,
        )

        for chunk in chunks:
            # Each chunk should be close to max_chunk_size (may exceed by one paragraph)
            assert len(chunk.content) <= 200  # generous upper bound

    def test_sets_content_hash(self):
        content = "Test paragraph.\n\nAnother paragraph."
        chunks = parse_vendor_doc_content(
            url="https://example.com",
            title="Test",
            content=content,
        )

        for chunk in chunks:
            assert len(chunk.content_hash) == 64
