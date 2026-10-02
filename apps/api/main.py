"""FastAPI web service for the Agentic Market Research Assistant."""

from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from pydantic import BaseModel, Field

from apps.api.dashboard import get_dashboard_html
from src.contracts.analysis import AnalysisRequest
from src.contracts.report import DailyResearchReport
from src.finance_core.reporting.renderer import render_html, render_markdown
from src.orchestration.workflow import ResearchOrchestrator
from src.providers.indian_stocks import normalize_indian_symbol
from src.services_registry import AppServices, create_default_services

app = FastAPI(
    title="Agentic Market Research Assistant API",
    description="Multi-agent finance research service with MCP, sentiment, technical analytics, and point-in-time provenance",
    version="1.0.0",
)

# Services and Orchestrator instances for live and fixture modes
live_services: AppServices = create_default_services(mode="live")
live_orchestrator = ResearchOrchestrator(live_services)

fixture_services: AppServices = create_default_services(mode="fixture")
fixture_orchestrator = ResearchOrchestrator(fixture_services)


class RunRequestPayload(BaseModel):
    symbols: list[str] = Field(default=["RELIANCE"], min_length=1)
    analysis_timestamp: datetime | None = None
    price_lookback_days: int = 120
    news_lookback_hours: int = 48
    signal_horizon_bars: int = 5
    mode: str = "live"


@app.get("/", response_class=HTMLResponse)
async def root_dashboard():
    """Interactive Market Research Assistant web dashboard."""
    return HTMLResponse(content=get_dashboard_html())


@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint returning 204 to prevent browser console 404s."""
    return Response(status_code=204)


@app.get("/health")
async def health_check():
    m_health = await live_services.market_provider.get_health()
    n_health = await live_services.news_provider.get_health()
    return {
        "status": "online",
        "mode": "live",
        "timestamp": datetime.now(UTC).isoformat(),
        "providers": [m_health.model_dump(), n_health.model_dump()],
    }


@app.post("/research/run")
async def trigger_research_run(payload: RunRequestPayload):
    is_fixture = payload.mode.lower() == "fixture"
    orch = fixture_orchestrator if is_fixture else live_orchestrator

    if is_fixture:
        cutoff = payload.analysis_timestamp or datetime(2026, 9, 25, 16, 10, 0, tzinfo=UTC)
        target_symbols = payload.symbols
    else:
        # Up-to-date analysis cutoff using current real-time timestamp
        cutoff = payload.analysis_timestamp or datetime.now(UTC)
        target_symbols = []
        for s in payload.symbols:
            canon, _ = normalize_indian_symbol(s)
            target_symbols.append(canon)

    req = AnalysisRequest(
        symbols=target_symbols,
        analysis_timestamp=cutoff,
        timezone="Asia/Kolkata" if not is_fixture else "America/New_York",
        market="IN" if not is_fixture else "US",
        price_lookback_days=payload.price_lookback_days,
        news_lookback_hours=payload.news_lookback_hours,
        signal_horizon_bars=payload.signal_horizon_bars,
    )
    try:
        ctx = await orch.execute_run(req)
        reports = {}
        for sym, s_data in ctx.symbols_data.items():
            if s_data.report:
                rep_json = s_data.report.model_dump(mode="json")
                reports[sym] = rep_json
                # Index by variations so client can look up by any alias
                base_sym = sym.split(".")[0].replace("^", "")
                reports[base_sym] = rep_json
                reports[sym.upper()] = rep_json
                for orig in payload.symbols:
                    if orig.upper() == base_sym or orig.upper() == sym.upper():
                        reports[orig] = rep_json
                        reports[orig.upper()] = rep_json

        return {
            "run_id": ctx.run_id,
            "status": ctx.state.value,
            "reports": reports,
            "warnings": ctx.warnings,
            "errors": ctx.errors,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/research/reports/{run_id}/{symbol}")
async def get_report(run_id: str, symbol: str, format: str = "json"):
    # Check live repo first, then fixture repo
    run = live_services.repo.get_run(run_id) or fixture_services.repo.get_run(run_id)
    if not run:
        raise HTTPException(
            status_code=404, detail=f"Research run {run_id} not found"
        )

    # Check symbol variants
    clean = symbol.upper().strip()
    canon, _ = normalize_indian_symbol(clean)
    rep: DailyResearchReport | None = None

    for candidate in (clean, canon, clean.split(".")[0], f"{clean}.NS"):
        if candidate in run.reports:
            rep = run.reports[candidate]
            break

    if not rep:
        raise HTTPException(
            status_code=404, detail=f"Report for {symbol} in run {run_id} not found"
        )

    if format == "html":
        return HTMLResponse(content=render_html(rep))
    elif format == "markdown":
        return PlainTextResponse(content=render_markdown(rep))
    return rep.model_dump(mode="json")
