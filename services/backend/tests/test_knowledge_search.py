"""Tests for knowledge search API endpoints.

Tests the API layer with mocked embedding service since SQLite
doesn't support pgvector. The parser tests (test_knowledge_parser.py)
cover the actual parsing logic.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import API

SAMPLE_SEARCH_RESULTS = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "source_file": "general/api-design.md",
        "source_type": "knowledge_file",
        "section": "Checklist",
        "checklist_item": "What API style is used?",
        "priority": "critical",
        "content": "What API style is used?",
        "score": 0.85,
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "source_file": "general/security.md",
        "source_type": "knowledge_file",
        "section": "Checklist",
        "checklist_item": "How is API authentication handled?",
        "priority": "critical",
        "content": "How is API authentication handled?",
        "score": 0.72,
    },
]

SAMPLE_INDEX_STATUS = {
    "indexed": True,
    "total_embeddings": 500,
    "knowledge_file_count": 450,
    "vendor_doc_count": 50,
    "upload_count": 0,
    "last_indexed_at": "2026-03-23T12:00:00+00:00",
}

SAMPLE_REINDEX_RESULT = {
    "status": "completed",
    "files_processed": 10,
    "checklist_items_indexed": 100,
    "vendor_docs_indexed": 5,
    "uploads_indexed": 0,
    "duration_seconds": 3.14,
    "errors": [],
}

IDLE_TASK_STATE = {
    "running": False,
    "paused": False,
    "started_at": None,
    "timeout": None,
    "last_result": None,
    "last_error": None,
    "progress": None,
}


class TestKnowledgeSearchEndpoint:
    @pytest.mark.asyncio
    @patch("src.api.knowledge.embedding_service")
    async def test_search_returns_results(self, mock_service, client):
        mock_service.get_index_status = AsyncMock(return_value=SAMPLE_INDEX_STATUS)
        mock_service.search_knowledge = AsyncMock(return_value=SAMPLE_SEARCH_RESULTS)

        resp = await client.post(
            f"{API}/knowledge/search",
            json={"query": "API authentication"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "API authentication"
        assert data["total_results"] == 2
        assert len(data["results"]) == 2
        assert data["results"][0]["score"] == 0.85
        assert data["results"][0]["priority"] == "critical"

    @pytest.mark.asyncio
    @patch("src.api.knowledge.embedding_service")
    async def test_search_with_filters(self, mock_service, client):
        mock_service.get_index_status = AsyncMock(return_value=SAMPLE_INDEX_STATUS)
        mock_service.search_knowledge = AsyncMock(return_value=[SAMPLE_SEARCH_RESULTS[0]])

        resp = await client.post(
            f"{API}/knowledge/search",
            json={
                "query": "API design",
                "top_k": 5,
                "min_score": 0.5,
                "exclude_files": ["general/api-design.md"],
                "priority_filter": "critical",
            },
        )

        assert resp.status_code == 200
        mock_service.search_knowledge.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.api.knowledge.embedding_service")
    async def test_search_returns_400_when_not_indexed(self, mock_service, client):
        mock_service.get_index_status = AsyncMock(
            return_value={**SAMPLE_INDEX_STATUS, "indexed": False, "total_embeddings": 0}
        )

        resp = await client.post(
            f"{API}/knowledge/search",
            json={"query": "test"},
        )

        assert resp.status_code == 400
        assert "not indexed" in resp.json()["detail"].lower()


class TestReindexEndpoint:
    @pytest.mark.asyncio
    @patch("src.api.knowledge.embedding_service")
    async def test_reindex_default(self, mock_service, client):
        # Reindex is fire-and-forget; the POST schedules a background task
        # and returns immediately. Result is observed via the status endpoint.
        mock_service.get_reindex_task_state.return_value = IDLE_TASK_STATE
        mock_service.reindex_knowledge = AsyncMock(return_value=SAMPLE_REINDEX_RESULT)

        resp = await client.post(f"{API}/knowledge/reindex")

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "started"

    @pytest.mark.asyncio
    @patch("src.api.knowledge.embedding_service")
    async def test_reindex_with_options(self, mock_service, client):
        mock_service.get_reindex_task_state.return_value = IDLE_TASK_STATE
        mock_service.reindex_knowledge = AsyncMock(return_value=SAMPLE_REINDEX_RESULT)

        resp = await client.post(
            f"{API}/knowledge/reindex",
            json={"include_vendor_docs": False, "force": True},
        )

        assert resp.status_code == 200
        assert resp.json()["status"] == "started"

    @pytest.mark.asyncio
    @patch("src.api.knowledge.embedding_service")
    async def test_reindex_rejected_when_already_running(self, mock_service, client):
        running_state = {**IDLE_TASK_STATE, "running": True, "started_at": 1000.0}
        mock_service.get_reindex_task_state.return_value = running_state

        resp = await client.post(f"{API}/knowledge/reindex")

        assert resp.status_code == 409
        assert "already in progress" in resp.json()["detail"].lower()


class TestReindexStatusEndpoint:
    @pytest.mark.asyncio
    @patch("src.api.knowledge.embedding_service")
    async def test_status_when_indexed(self, mock_service, client):
        mock_service.get_index_status = AsyncMock(return_value=SAMPLE_INDEX_STATUS)
        mock_service.get_reindex_task_state.return_value = IDLE_TASK_STATE

        resp = await client.get(f"{API}/knowledge/reindex/status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["indexed"] is True
        assert data["total_embeddings"] == 500
        assert data["reindexing"] is False

    @pytest.mark.asyncio
    @patch("src.api.knowledge.embedding_service")
    async def test_status_when_not_indexed(self, mock_service, client):
        mock_service.get_index_status = AsyncMock(return_value={
            "indexed": False,
            "total_embeddings": 0,
            "knowledge_file_count": 0,
            "vendor_doc_count": 0,
            "upload_count": 0,
            "last_indexed_at": None,
        })
        mock_service.get_reindex_task_state.return_value = IDLE_TASK_STATE

        resp = await client.get(f"{API}/knowledge/reindex/status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["indexed"] is False
        assert data["total_embeddings"] == 0
        assert data["reindexing"] is False


class TestQuestionSuggestions:
    @pytest.mark.asyncio
    @patch("src.api.questions.embedding_service")
    async def test_suggestions_included_when_answer_provided(
        self, mock_service, client, sample_version
    ):
        mock_service.get_index_status = AsyncMock(return_value=SAMPLE_INDEX_STATUS)
        mock_service.get_suggestions_for_text = AsyncMock(return_value=[
            {
                "source_file": "general/security.md",
                "checklist_item": "How is API authentication handled?",
                "priority": "critical",
                "score": 0.78,
            },
        ])

        version_id = sample_version["id"]

        # Create a question
        resp = await client.post(
            f"{API}/versions/{version_id}/questions",
            json={"question_text": "What auth mechanism?"},
        )
        assert resp.status_code == 201
        question_id = resp.json()["id"]

        # Answer the question — should trigger suggestions
        resp = await client.patch(
            f"{API}/versions/{version_id}/questions/{question_id}",
            json={"answer_text": "We use OAuth 2.0", "status": "answered"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) == 1
        assert data["suggestions"][0]["source_file"] == "general/security.md"

    @pytest.mark.asyncio
    @patch("src.api.questions.embedding_service")
    async def test_no_suggestions_when_not_indexed(
        self, mock_service, client, sample_version
    ):
        mock_service.get_index_status = AsyncMock(return_value={
            **SAMPLE_INDEX_STATUS, "indexed": False
        })

        version_id = sample_version["id"]

        resp = await client.post(
            f"{API}/versions/{version_id}/questions",
            json={"question_text": "Test question?"},
        )
        assert resp.status_code == 201
        question_id = resp.json()["id"]

        resp = await client.patch(
            f"{API}/versions/{version_id}/questions/{question_id}",
            json={"answer_text": "Test answer", "status": "answered"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["suggestions"] == []

    @pytest.mark.asyncio
    async def test_no_suggestions_field_without_answer(self, client, sample_version):
        version_id = sample_version["id"]

        resp = await client.post(
            f"{API}/versions/{version_id}/questions",
            json={"question_text": "Unanswered question?"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["suggestions"] == []
