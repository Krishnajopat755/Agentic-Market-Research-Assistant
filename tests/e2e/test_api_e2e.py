"""FastAPI endpoint verification tests."""

from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_api_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "online"
    assert len(data["providers"]) == 2


def test_api_research_run_and_get_report():
    payload = {
        "symbols": ["AAPL"],
        "price_lookback_days": 120,
        "news_lookback_hours": 24,
        "mode": "fixture",
    }
    resp = client.post("/research/run", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "COMPLETED"
    run_id = data["run_id"]
    assert "AAPL" in data["reports"]

    # Test report retrieval endpoint
    rep_resp = client.get(f"/research/reports/{run_id}/AAPL?format=json")
    assert rep_resp.status_code == 200
    rep_data = rep_resp.json()
    assert rep_data["symbol"] == "AAPL"
    assert rep_data["market_state"] in ("BULLISH", "NEUTRAL", "BEARISH")

    # Test markdown report format
    md_resp = client.get(f"/research/reports/{run_id}/AAPL?format=markdown")
    assert md_resp.status_code == 200
    assert "# Daily Market Research Report: AAPL" in md_resp.text

    # Test html report format
    html_resp = client.get(f"/research/reports/{run_id}/AAPL?format=html")
    assert html_resp.status_code == 200
    assert "<!DOCTYPE html>" in html_resp.text
    assert "Market Research Report: AAPL" in html_resp.text


def test_api_root_dashboard():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Agentic Market Research Assistant" in resp.text
    assert "MCP ENGINE ONLINE" in resp.text


def test_api_favicon():
    resp = client.get("/favicon.ico")
    assert resp.status_code == 204
