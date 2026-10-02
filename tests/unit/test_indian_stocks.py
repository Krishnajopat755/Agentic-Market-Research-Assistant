"""Unit tests for Indian equities normalization, resolution, and dynamic synthesis."""

import pytest
from src.providers.indian_stocks import normalize_indian_symbol, get_equity_metadata
from src.llm.mock_adapter import MockLLMAdapter
from src.agents.base import SynthesisReportAgentOutput
from src.llm.base import LLMMessage


def test_normalize_indian_symbol():
    # Plain symbol
    sym, ticker = normalize_indian_symbol("RELIANCE")
    assert sym == "RELIANCE.NS"
    assert ticker == "RELIANCE.NS"

    # Lowercase
    sym, ticker = normalize_indian_symbol("tcs")
    assert sym == "TCS.NS"
    assert ticker == "TCS.NS"

    # Suffix preserved
    sym, ticker = normalize_indian_symbol("HDFCBANK.BO")
    assert sym == "HDFCBANK.BO"

    # Index aliases
    sym, ticker = normalize_indian_symbol("NIFTY")
    assert sym == "^NSEI"

    sym, ticker = normalize_indian_symbol("SENSEX")
    assert sym == "^BSESN"


def test_get_equity_metadata():
    rel = get_equity_metadata("RELIANCE.NS")
    assert "Reliance" in rel["name"]
    assert rel["currency_symbol"] == "₹"
    assert rel["currency"] == "INR"

    tcs = get_equity_metadata("TCS")
    assert "Tata Consultancy" in tcs["name"]
    assert tcs["currency_symbol"] == "₹"

    nifty = get_equity_metadata("^NSEI")
    assert "NIFTY" in nifty["name"]
    assert nifty["currency_symbol"] == "₹"


@pytest.mark.asyncio
async def test_mock_llm_adapter_dynamic_for_indian_stocks():
    adapter = MockLLMAdapter()

    # Test RELIANCE
    prompt_reliance = (
        "Analyze research findings for RELIANCE as of 2026-10-01T10:00:00Z.\n"
        "Company: Reliance Industries Limited (Energy & Retail)\n"
        "Market State: BULLISH (Score: +0.35, Confidence: 78.0%)\n"
        "Latest Price: ₹1167.70, 5d Return: +2.1%\n"
        "RSI: 58.5, SMA20: 1140.0\n"
        "Mean Sentiment: +0.40 over 6 articles.\n"
    )

    resp = await adapter.complete(
        messages=[
            LLMMessage(role="system", content="Synthesize report."),
            LLMMessage(role="user", content=prompt_reliance),
        ],
        response_schema=SynthesisReportAgentOutput,
        trace_context={"symbol": "RELIANCE"},
    )

    out = SynthesisReportAgentOutput(**resp.structured_output)
    assert "Reliance" in out.headline
    assert "Apple" not in out.headline
    assert "Apple" not in out.executive_summary
    assert "RELIANCE" in out.executive_summary or "Reliance" in out.executive_summary
    assert out.market_state == "BULLISH"
    assert out.signal_score == 0.35

    # Test TCS
    prompt_tcs = (
        "Analyze research findings for TCS as of 2026-10-01T10:00:00Z.\n"
        "Company: Tata Consultancy Services Limited (IT)\n"
        "Market State: BEARISH (Score: -0.25, Confidence: 70.0%)\n"
        "Latest Price: ₹2075.00, 5d Return: -1.8%\n"
        "RSI: 42.0, SMA20: 2110.0\n"
        "Mean Sentiment: -0.15 over 4 articles.\n"
    )

    resp_tcs = await adapter.complete(
        messages=[
            LLMMessage(role="system", content="Synthesize report."),
            LLMMessage(role="user", content=prompt_tcs),
        ],
        response_schema=SynthesisReportAgentOutput,
        trace_context={"symbol": "TCS"},
    )

    out_tcs = SynthesisReportAgentOutput(**resp_tcs.structured_output)
    assert "Tata" in out_tcs.headline or "TCS" in out_tcs.headline
    assert "Apple" not in out_tcs.headline
    assert "Apple" not in out_tcs.executive_summary
    assert out_tcs.market_state == "BEARISH"
