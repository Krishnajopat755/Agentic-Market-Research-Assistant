"""Multi-format report renderer for Markdown, HTML, and JSON representations."""

from src.contracts.report import DailyResearchReport


def render_markdown(report: DailyResearchReport) -> str:
    """Render comprehensive Markdown research report matching doc 17 template."""
    lines = []
    lines.append(f"# Daily Market Research Report: {report.symbol}")
    lines.append(
        f"**Run ID:** `{report.run_id}` | **Analysis Cutoff:** `{report.analysis_timestamp.isoformat()}` | **Generated At:** `{report.generated_at.isoformat()}`\n"
    )

    lines.append(f"## {report.headline}")
    lines.append(
        f"> **Market Research State:** `{report.market_state}` | **Signal Score:** `{report.signal_score:+.2f}` | **Confidence:** `{report.confidence:.1%}`\n"
    )

    lines.append("### Executive Summary")
    lines.append(f"{report.executive_summary}\n")

    # Market Snapshot Table
    lines.append("### Market Snapshot")
    s = report.snapshot
    lines.append("| Metric | Value | Freshness |")
    lines.append("|---|---|---|")
    lines.append(
        f"| **Close Price** | ${s.price:.2f} ({s.change:+.2f} / {s.change_percent:+.2f}%) | {s.freshness_seconds / 60:.1f} mins |"
    )
    lines.append(f"| **Day Range** | ${s.low:.2f} - ${s.high:.2f} | Open: ${s.open:.2f} |")
    lines.append(f"| **Volume** | {s.volume:,.0f} | Source: {s.source} |")
    lines.append(
        f"| **Status** | {'[STALE]' if s.is_stale else '[FRESH]'} | Entitlement: {report.snapshot.source} |\n"
    )

    # Technical Indicators Table
    lines.append("### Technical Indicators")
    t = report.technical
    lines.append("| Indicator | Value | Interpretation |")
    lines.append("|---|---|---|")
    lines.append(
        f"| **SMA (20 / 50)** | {t.sma_20 or 'N/A'} / {t.sma_50 or 'N/A'} | {'Price above SMAs' if (t.sma_20 and s.price > t.sma_20) else 'Price below SMAs'} |"
    )
    lines.append(
        f"| **RSI (14)** | {t.rsi_14 or 'N/A'} | {'Overbought (>70)' if (t.rsi_14 and t.rsi_14 > 70) else ('Oversold (<30)' if (t.rsi_14 and t.rsi_14 < 30) else 'Neutral (30-70)')} |"
    )
    lines.append(
        f"| **MACD / Signal** | {t.macd or 'N/A'} / {t.macd_signal or 'N/A'} | Hist: {t.macd_hist or 'N/A'} |"
    )
    lines.append(f"| **ATR (14)** | ${t.atr_14 or 'N/A'} | Volatility proxy |")
    lines.append(
        f"| **Realized Volatility (20d)** | {f'{t.realized_volatility_20:.1%}' if t.realized_volatility_20 else 'N/A'} | Annualized rolling |"
    )
    lines.append(
        f"| **Volume Z-Score** | {t.volume_zscore_20:+.2f} | {'Above average volume' if (t.volume_zscore_20 and t.volume_zscore_20 > 1.0) else 'Normal volume'} |\n"
    )

    # Sentiment Summary
    lines.append("### News & Sentiment Analysis")
    sent = report.sentiment
    lines.append(f"- **Article Count (deduplicated):** {sent.article_count}")
    lines.append(
        f"- **Mean Sentiment Score:** `{sent.mean_score:+.2f}` (Dispersion: `{sent.sentiment_dispersion:.2f}`)"
    )
    lines.append(
        f"- **Sentiment Breakdown:** Positive: `{sent.positive_share:.0%}` | Neutral: `{sent.neutral_share:.0%}` | Negative: `{sent.negative_share:.0%}`"
    )
    lines.append(f"- **Publishers:** {sent.source_diversity} distinct sources\n")

    if report.top_news:
        lines.append("#### Key News Headlines")
        for art in report.top_news[:5]:
            sent_badge = (
                f"[{art.sentiment.label.upper()}: {art.sentiment.score:+.2f}]"
                if art.sentiment
                else ""
            )
            lines.append(
                f"- [{art.title}]({art.article_url}) — *{art.publisher}* ({art.published_at.strftime('%Y-%m-%d %H:%M UTC')}) {sent_badge}"
            )
        lines.append("")

    # Quantitative Signal
    lines.append("### Quantitative Research Signal")
    sig = report.signal
    lines.append(f"- **Model:** `{sig.model_version}` ({sig.method})")
    lines.append(f"- **Horizon:** {sig.horizon_bars} daily bars")
    lines.append(
        f"- **State:** `{sig.state}` (Score: `{sig.score:+.2f}`, Confidence: `{sig.confidence:.1%}`)\n"
    )

    if sig.top_contributors:
        lines.append("#### Factor Contribution Breakdown")
        lines.append("| Factor | Weight | Value | Contribution | Direction |")
        lines.append("|---|---|---|---|---|")
        for c in sig.top_contributors:
            lines.append(
                f"| {c.name.capitalize()} | {c.weight:.2f} | {c.value:+.2f} | {c.contribution:+.3f} | {c.direction} |"
            )
        lines.append("")

    # Scenario Analysis
    if report.scenario_analysis:
        lines.append("### Scenario Analysis")
        for sc_name, sc_desc in report.scenario_analysis.items():
            lines.append(f"- **{sc_name.capitalize()}:** {sc_desc}")
        lines.append("")

    # Evidence Mapping
    if report.evidence:
        lines.append("### Evidence & Provenance Binding")
        lines.append("| Claim ID | Claim | Evidence Type | Reference |")
        lines.append("|---|---|---|---|")
        for ev in report.evidence:
            ref_str = (
                f"[{ev.evidence_ref}]({ev.source_url})" if ev.source_url else f"`{ev.evidence_ref}`"
            )
            lines.append(
                f"| `{ev.claim_id}` | {ev.claim_text} | `{ev.evidence_type}` | {ref_str} |"
            )
        lines.append("")

    # Limitations & Warnings
    if report.known_limitations or report.freshness_warnings:
        lines.append("### Limitations & Warnings")
        for lim in report.known_limitations:
            lines.append(f"- [WARN] {lim}")
        for warn in report.freshness_warnings:
            lines.append(f"- [WARN] {warn}")
        lines.append("")

    lines.append("---")
    lines.append(f"> **{report.regulatory_notice}**")

    return "\n".join(lines)


def render_html(report: DailyResearchReport) -> str:
    """Render rich modern HTML report with executive dashboard styling."""
    md = render_markdown(report)
    state_color = (
        "#10b981"
        if report.market_state == "BULLISH"
        else ("#ef4444" if report.market_state == "BEARISH" else "#f59e0b")
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Market Research Report: {report.symbol}</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --text: #f8fafc;
      --muted: #94a3b8;
      --border: #334155;
      --accent: #38bdf8;
      --state-color: {state_color};
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      margin: 0;
      padding: 30px;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
      background: var(--card-bg);
      padding: 36px;
      border-radius: 12px;
      border: 1px solid var(--border);
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid var(--border);
      padding-bottom: 20px;
      margin-bottom: 24px;
    }}
    .badge {{
      display: inline-block;
      padding: 6px 16px;
      font-weight: 700;
      font-size: 1.1rem;
      border-radius: 9999px;
      background-color: var(--state-color);
      color: #0f172a;
    }}
    h1, h2, h3 {{ color: var(--text); }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
    }}
    th, td {{
      padding: 10px 14px;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }}
    th {{ background: #0f172a; color: var(--accent); }}
    .notice {{
      background: #172554;
      border-left: 4px solid var(--accent);
      padding: 14px 18px;
      font-size: 0.9rem;
      color: #cbd5e1;
      margin-top: 30px;
      border-radius: 4px;
    }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <h1 style="margin:0;">{report.symbol} Market Research</h1>
        <small style="color:var(--muted);">Analysis Cutoff: {report.analysis_timestamp.isoformat()}</small>
      </div>
      <div>
        <span class="badge">{report.market_state} ({report.signal_score:+.2f})</span>
      </div>
    </div>
    <div style="font-size:1.15rem; font-weight:600; margin-bottom:12px;">{report.headline}</div>
    <p>{report.executive_summary}</p>
    <hr style="border:0; border-top:1px solid var(--border); margin:24px 0;">
    <div>
      <pre style="white-space:pre-wrap; font-family:inherit;">{md}</pre>
    </div>
    <div class="notice">
      {report.regulatory_notice}
    </div>
  </div>
</body>
</html>"""
    return html


def render_report(report: DailyResearchReport, format_type: str = "markdown") -> str:
    """Entrypoint for report rendering."""
    fmt = format_type.lower()
    if fmt == "html":
        return render_html(report)
    elif fmt == "json":
        return report.model_dump_json(indent=2)
    else:
        return render_markdown(report)
