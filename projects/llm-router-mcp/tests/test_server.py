"""Unit tests for the tool functions. No network: requests.post is replaced with a fake."""
import asyncio

import pytest
import requests

import server


class FakeResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status
        self.ok = status < 400

    def json(self):
        if isinstance(self._data, Exception):
            raise self._data
        return self._data


@pytest.fixture
def fake_post(monkeypatch):
    """Make requests.post return a canned reply and record what it was called with."""
    calls = []

    def install(reply):
        def post(url, **kwargs):
            calls.append({"url": url, **kwargs})
            if isinstance(reply, Exception):
                raise reply
            return reply
        monkeypatch.setattr(server.requests, "post", post)
        return calls

    return install


@pytest.fixture(autouse=True)
def keys(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")


def test_local_llm_returns_response(fake_post):
    calls = fake_post(FakeResponse({"response": "hello"}))
    assert server.local_llm("llama3", "hi") == "hello"
    assert calls[0]["json"]["stream"] is False
    assert calls[0]["timeout"] == server.LOCAL_TIMEOUT


def test_anthropic_llm_returns_text(fake_post):
    calls = fake_post(FakeResponse({"content": [{"type": "text", "text": "hi there"}]}))
    assert server.anthropic_llm("claude-haiku-5-5", "hi") == "hi there"
    assert calls[0]["headers"]["x-api-key"] == "test-anthropic-key"
    assert calls[0]["timeout"] == server.API_TIMEOUT


def test_gemini_key_is_sent_in_header_not_url(fake_post):
    reply = {"candidates": [{"content": {"parts": [{"text": "bonjour"}]}}]}
    calls = fake_post(FakeResponse(reply))
    assert server.gemini_llm("gemini-2.5-flash", "hi") == "bonjour"
    assert "key=" not in calls[0]["url"]
    assert calls[0]["headers"]["x-goog-api-key"] == "test-gemini-key"


def test_missing_key_gives_clear_error(fake_post, monkeypatch):
    fake_post(FakeResponse({}))
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    with pytest.raises(server.ToolError, match="ANTHROPIC_API_KEY is not set"):
        server.anthropic_llm("claude-haiku-5-5", "hi")


def test_http_error_includes_provider_message(fake_post):
    fake_post(FakeResponse({"error": {"message": "invalid x-api-key"}}, status=401))
    with pytest.raises(server.ToolError, match=r"HTTP 401.*invalid x-api-key"):
        server.anthropic_llm("claude-haiku-5-5", "hi")


def test_timeout_gives_clear_error(fake_post):
    fake_post(requests.Timeout())
    with pytest.raises(server.ToolError, match="did not reply"):
        server.local_llm("llama3", "hi")


def test_ollama_not_running_gives_clear_error(fake_post):
    fake_post(requests.ConnectionError())
    with pytest.raises(server.ToolError, match="Could not connect to Ollama"):
        server.local_llm("llama3", "hi")


def test_non_json_reply_gives_clear_error(fake_post):
    fake_post(FakeResponse(ValueError("not json"), status=502))
    with pytest.raises(server.ToolError, match="non-JSON"):
        server.gemini_llm("gemini-2.5-flash", "hi")


def test_call_tool_turns_errors_into_text(fake_post):
    fake_post(requests.ConnectionError())
    result = asyncio.run(server.call_tool("local_llm", {"model": "llama3", "prompt": "hi"}))
    assert result[0].text.startswith("Error: Could not connect to Ollama")
