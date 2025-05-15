# test_app.py
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from bs4 import BeautifulSoup
from app import fetch_web_data, fetch_citations, analyze_metrics, get_answer

# Mock environment variables
@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")

# Mock aiohttp session
@pytest.fixture
def mock_aiohttp_session():
    session = AsyncMock()
    session.get.return_value.__aenter__.return_value.status = 200
    session.get.return_value.__aenter__.return_value.text = AsyncMock(
        return_value="""
        <html>
            <div class="result">Test result 1</div>
            <div class="snippet">Test snippet 1</div>
            <a href="https://example.com">Example</a>
        </html>
        """
    )
    return session

# Test fetch_web_data
@pytest.mark.asyncio
async def test_fetch_web_data(mock_aiohttp_session):
    with patch("aiohttp.ClientSession", return_value=mock_aiohttp_session):
        results = await fetch_web_data("test query")
        assert len(results) > 0
        assert "Test result 1" in results
        assert "Test snippet 1" in results

# Test fetch_web_data error handling
@pytest.mark.asyncio
async def test_fetch_web_data_error():
    with patch("aiohttp.ClientSession.get", side_effect=Exception("Network error")):
        with patch("streamlit.error") as mock_error:
            results = await fetch_web_data("test query")
            assert results == []
            mock_error.assert_called()

# Test fetch_citations
@pytest.mark.asyncio
async def test_fetch_citations(mock_aiohttp_session):
    with patch("aiohttp.ClientSession", return_value=mock_aiohttp_session):
        citations = await fetch_citations("test query")
        assert len(citations) == 1
        assert citations[0] == "https://example.com"

# Test fetch_citations error handling
@pytest.mark.asyncio
async def test_fetch_citations_error():
    with patch("aiohttp.ClientSession.get", side_effect=Exception("Network error")):
        with patch("streamlit.error") as mock_error:
            citations = await fetch_citations("test query")
            assert citations == []
            mock_error.assert_called()

# Test analyze_metrics
def test_analyze_metrics():
    answer = "This is a test answer"
    citations = ["https://example.com"]
    metrics = analyze_metrics(answer, citations)
    assert isinstance(metrics, dict)
    assert metrics["relevance"] == 0.85
    assert metrics["accuracy"] == 0.90
    assert metrics["precision"] == 0.75
    assert metrics["factuality"] == 0.80
    assert metrics["readability"] == 0.90
    assert metrics["engagement"] == 0.60
    assert metrics["authority"] == 0.85

# Test get_answer
@pytest.mark.asyncio
async def test_get_answer(mock_aiohttp_session):
    # Mock OpenAI client
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test answer [1]"
    mock_response.usage.total_tokens = 100
    with patch("aiohttp.ClientSession", return_value=mock_aiohttp_session), \
         patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        with patch("streamlit.error") as mock_error:
            answer, citations, metrics, telemetry = await get_answer("test query")
            assert answer == "Test answer [1]"
            assert len(citations) == 1
            assert citations[0] == "https://example.com"
            assert metrics["relevance"] == 0.85
            assert telemetry["total_tokens"] == 100
            assert telemetry["api_calls"] == 1
            mock_error.assert_not_called()

# Test get_answer with empty response
@pytest.mark.asyncio
async def test_get_answer_empty_response(mock_aiohttp_session):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = ""
    with patch("aiohttp.ClientSession", return_value=mock_aiohttp_session), \
         patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        with patch("streamlit.error") as mock_error:
            answer, citations, metrics, telemetry = await get_answer("test query")
            assert answer == ""
            assert citations == []
            assert metrics == {}
            assert telemetry == {}
            mock_error.assert_called_with("Error: Empty response from API")

# Test get_answer with API error
@pytest.mark.asyncio
async def test_get_answer_api_error(mock_aiohttp_session):
    with patch("aiohttp.ClientSession", return_value=mock_aiohttp_session), \
         patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.side_effect = Exception("API error")
        with patch("streamlit.error") as mock_error:
            answer, citations, metrics, telemetry = await get_answer("test query")
            assert answer == ""
            assert citations == []
            assert metrics == {}
            assert telemetry == {}
            mock_error.assert_called_with("Error: API error")

if __name__ == "__main__":
    pytest.main()