"""Command-line interface for the Agentic Market Research Assistant."""

import asyncio
import sys
from datetime import UTC, datetime

import typer
from rich.console import Console
from rich.table import Table

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.contracts.analysis import AnalysisRequest
from src.finance_core.reporting.renderer import render_markdown
from src.orchestration.workflow import ResearchOrchestrator
from src.services_registry import create_default_services

app = typer.Typer(help="Agentic Market Research Assistant CLI")
console = Console()


@app.command()
def demo_aapl(
    format_type: str = typer.Option(
        "markdown", "--format", "-f", help="Output format: markdown, html, json"
    ),
):
    """Run full demonstration workflow for AAPL using offline fixtures."""
    console.print(
        "[bold cyan]Starting Agentic Market Research Assistant Demo (AAPL)...[/bold cyan]"
    )

    request = AnalysisRequest(
        symbols=["AAPL"],
        analysis_timestamp=datetime(2026, 9, 25, 16, 10, 0, tzinfo=UTC),
        price_lookback_days=120,
        news_lookback_hours=24,
        signal_horizon_bars=5,
    )

    services = create_default_services(mode="fixture")
    orchestrator = ResearchOrchestrator(services)

    async def _run():
        return await orchestrator.execute_run(request)

    ctx = asyncio.run(_run())

    sym_state = ctx.symbols_data.get("AAPL")
    if sym_state and sym_state.report:
        rep = sym_state.report
        console.print(f"\n[bold green]Report Generated for {rep.symbol}![/bold green]")

        # Print summary table
        table = Table(title=f"Research Summary: {rep.symbol}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Market State", rep.market_state)
        table.add_row("Signal Score", f"{rep.signal_score:+.2f}")
        table.add_row("Confidence", f"{rep.confidence:.1%}")
        table.add_row("Snapshot Price", f"${rep.snapshot.price:.2f}")
        table.add_row("Headline", rep.headline)
        console.print(table)

        # Output report
        rendered = render_markdown(rep)
        console.print("\n[bold yellow]Full Markdown Report Preview:[/bold yellow]\n")
        console.print(rendered)
    else:
        console.print("[bold red]Run completed but no report was generated.[/bold red]")


@app.command()
def run(
    symbols: list[str] = typer.Option(["AAPL"], "--symbol", "-s", help="Symbols to analyze"),
    mode: str = typer.Option("fixture", "--mode", "-m", help="Mode: fixture or live"),
    lookback_days: int = typer.Option(120, "--lookback", "-l", help="Price lookback in days"),
):
    """Execute research run for custom symbol list."""
    console.print(f"[bold cyan]Running research for {symbols} in {mode} mode...[/bold cyan]")

    request = AnalysisRequest(
        symbols=symbols,
        analysis_timestamp=datetime(2026, 9, 25, 16, 10, 0, tzinfo=UTC),
        price_lookback_days=lookback_days,
        news_lookback_hours=24,
    )

    services = create_default_services(mode=mode)
    orchestrator = ResearchOrchestrator(services)

    async def _run():
        return await orchestrator.execute_run(request)

    ctx = asyncio.run(_run())
    console.print(
        f"[bold green]Completed run {ctx.run_id} with state {ctx.state.value}.[/bold green]"
    )


if __name__ == "__main__":
    app()
