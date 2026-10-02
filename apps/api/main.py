"""FastAPI web service for the Agentic Market Research Assistant."""

from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.contracts.analysis import AnalysisRequest
from src.contracts.report import DailyResearchReport
from src.finance_core.reporting.renderer import render_html, render_markdown
from src.orchestration.workflow import ResearchOrchestrator
from src.services_registry import AppServices, create_default_services

app = FastAPI(
    title="Agentic Market Research Assistant API",
    description="Multi-agent finance research service with MCP, sentiment, technical analytics, and point-in-time provenance",
    version="1.0.0",
)

# Global services instance
services: AppServices = create_default_services(mode="fixture")
orchestrator = ResearchOrchestrator(services)


class RunRequestPayload(BaseModel):
    symbols: list[str] = Field(default=["AAPL"], min_length=1)
    analysis_timestamp: datetime | None = None
    price_lookback_days: int = 120
    news_lookback_hours: int = 24
    signal_horizon_bars: int = 5
    mode: str = "fixture"


@app.get("/health")
async def health_check():
    m_health = await services.market_provider.get_health()
    n_health = await services.news_provider.get_health()
    return {
        "status": "online",
        "timestamp": datetime.now(UTC).isoformat(),
        "providers": [m_health.model_dump(), n_health.model_dump()],
    }


@app.post("/research/run")
async def trigger_research_run(payload: RunRequestPayload):
    cutoff = payload.analysis_timestamp or datetime(2026, 9, 25, 16, 10, 0, tzinfo=UTC)
    req = AnalysisRequest(
        symbols=payload.symbols,
        analysis_timestamp=cutoff,
        price_lookback_days=payload.price_lookback_days,
        news_lookback_hours=payload.news_lookback_hours,
        signal_horizon_bars=payload.signal_horizon_bars,
    )
    try:
        ctx = await orchestrator.execute_run(req)
        reports = {}
        for sym, s_data in ctx.symbols_data.items():
            if s_data.report:
                reports[sym] = s_data.report.model_dump(mode="json")
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
    run = services.repo.get_run(run_id)
    if not run or symbol.upper() not in run.reports:
        raise HTTPException(
            status_code=404, detail=f"Report for {symbol} in run {run_id} not found"
        )

    rep: DailyResearchReport = run.reports[symbol.upper()]
    if format == "html":
        return render_html(rep)
    elif format == "markdown":
        return render_markdown(rep)
    return rep.model_dump(mode="json")
