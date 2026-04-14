"""Tests for the vendor doc fetcher — User-Agent, retry, per-host failure counts (#223)."""
import os
from unittest.mock import MagicMock

import httpx
import pytest

os.environ.setdefault("VENDOR_FETCH_BACKOFF_BASE", "0")

from src.services import embedding_service  # noqa: E402
from src.services.embedding_service import _fetch_vendor_url  # noqa: E402


def _ok(body: str = "<html>ok</html>") -> MagicMock:
    resp = MagicMock()
    resp.status_code = 200
    resp.text = body
    resp.headers = {"content-type": "text/html; charset=utf-8"}
    return resp


def _status(status: int, body: str = "") -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.text = body
    resp.headers = {"content-type": "text/html"}
    return resp


class _FakeClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    async def get(self, url):
        self.calls.append(url)
        r = self._responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def test_default_user_agent_is_browser_shaped():
    """Default User-Agent must not be the httpx default (vendors block it)."""
    ua = embedding_service.VENDOR_FETCH_USER_AGENT
    assert "Mozilla" in ua and "Chrome" in ua


@pytest.mark.asyncio
async def test_retries_on_transient_error_then_succeeds():
    client = _FakeClient([httpx.ConnectError("reset"), _ok()])
    outcome = await _fetch_vendor_url(client, {"url": "https://example.com/a", "title": "A"})
    assert outcome.chunks is not None
    assert outcome.error == ""
    assert len(client.calls) == 2


@pytest.mark.asyncio
async def test_retries_on_5xx_then_succeeds():
    client = _FakeClient([_status(503), _ok()])
    outcome = await _fetch_vendor_url(client, {"url": "https://example.com/a", "title": "A"})
    assert outcome.chunks is not None
    assert len(client.calls) == 2


@pytest.mark.asyncio
async def test_retries_on_empty_200_body():
    """Empty 200 body is the WAF-block signature — should retry."""
    client = _FakeClient([_status(200, ""), _ok()])
    outcome = await _fetch_vendor_url(client, {"url": "https://www.hpe.com/a", "title": "A"})
    assert outcome.chunks is not None
    assert len(client.calls) == 2


@pytest.mark.asyncio
async def test_does_not_retry_on_404():
    client = _FakeClient([_status(404)])
    outcome = await _fetch_vendor_url(
        client, {"url": "https://example.com/missing", "title": "X"}
    )
    assert outcome.chunks is None
    assert "404" in outcome.error
    assert len(client.calls) == 1


@pytest.mark.asyncio
async def test_records_host_on_persistent_failure():
    errors = [httpx.ConnectError("blocked")] * (embedding_service.VENDOR_FETCH_MAX_RETRIES + 1)
    client = _FakeClient(errors)
    outcome = await _fetch_vendor_url(client, {"url": "https://www.hpe.com/a", "title": "A"})
    assert outcome.chunks is None
    assert outcome.host == "www.hpe.com"
    assert len(client.calls) == embedding_service.VENDOR_FETCH_MAX_RETRIES + 1
