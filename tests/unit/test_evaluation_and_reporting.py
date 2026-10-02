"""Unit tests for walk-forward evaluation and reporting renderers."""

import json
from datetime import datetime, timezone

from src.contracts.market import MarketObservation
from src.contracts.report import DailyResearchReport
from src.finance_core.evaluation.walk_forward import run_walk_forward_evaluation
from src.finance_core.reporting.renderer import render_html, render_markdown, render_report


def test_walk_forward_evaluation():
    with open("fixtures/market/AAPL_daily.json", "r", encoding="utf-8") as f:
        bars = [MarketObservation(**item) for item in json.load(f)]

    res = run_walk_forward_evaluation(bars, horizon_bars=5, min_train_bars=40, test_window_bars=10)

    assert res.model_name == "logistic_regression"
    assert res.train_splits_count > 0
    assert res.total_test_samples > 0
    assert 0.0 <= res.accuracy <= 1.0
    assert 0.0 <= res.balanced_accuracy <= 1.0
    assert res.lookahead_bias_passed is True


def test_report_renderers():
    with open("fixtures/market/AAPL_daily.json", "r", encoding="utf-8") as f:
        bars = [MarketObservation(**item) for item in json.load(f)]

    from src.finance_core.features.builder import build_research_features
    from src.finance_core.indicators.technical import compute_technical_indicators
    from src.finance_core.market_data.normalization import build_market_snapshot
    from src.finance_core.sentiment.aggregator import aggregate_sentiment
    from src.finance_core.signal.scorecard import compute_scorecard_signal

    cutoff = datetime(2026, 9, 25, 16, 10, tzinfo=timezone.utc)
    snap = build_market_snapshot("AAPL", bars, as_of=cutoff)
    tech = compute_technical_indicators("AAPL", bars, as_of=cutoff)
    sent = aggregate_sentiment("AAPL", [], as_of=cutoff)
    feats = build_research_features("AAPL", as_of=cutoff, technical=tech, sentiment=sent)
    sig = compute_scorecard_signal(feats)

    rep = DailyResearchReport(
        run_id="test-run-rep",
        symbol="AAPL",
        analysis_timestamp=cutoff,
        market_state=sig.state,
        signal_score=sig.score,
        confidence=sig.confidence,
        headline="Apple Reports Solid Q4 Results",
        executive_summary="Executive summary for test.",
        snapshot=snap,
        technical=tech,
        sentiment=sent,
        signal=sig,
    )

    md = render_markdown(rep)
    assert "# Daily Market Research Report: AAPL" in md
    assert "Executive Summary" in md

    html = render_html(rep)
    assert "<!DOCTYPE html>" in html
    assert "AAPL Market Research" in html

    json_str = render_report(rep, format_type="json")
    data = json.loads(json_str)
    assert data["symbol"] == "AAPL"
