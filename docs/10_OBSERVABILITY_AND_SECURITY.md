# Observability and Security

## 1. Trace model

```text
research_run:<run_id>
  orchestrator
    agent:market_data
      mcp.fetch_market_snapshot
      provider.request
    agent:sentiment_technical
      mcp.compute_sentiment
      mcp.compute_technical_indicators
      mcp.run_signal_model
    agent:synthesis_report
      mcp.validate_report_claims
      mcp.render_daily_report
```

## 2. Trace attributes

- run.id
- symbol
- analysis_timestamp
- agent.name
- workflow.state
- tool.name
- provider.name
- provider.request_id
- data.event_time
- data.retrieved_at
- data.freshness_seconds
- model.name
- model.version
- latency_ms
- retry.count

Never attach API keys or unrestricted raw article bodies to traces.

## 3. Logs

JSON logs with timestamp, level, service, run_id, trace_id, agent, state, tool, provider, symbol, event, duration, error_code.

## 4. Operational metrics

- requests by provider;
- latency/error rate;
- rate-limit events;
- cache hit ratio;
- articles fetched/deduplicated;
- sentiment latency;
- report time;
- LLM token/cost usage;
- stale-data runs;
- failed runs.

## 5. Threat model

### API key leakage
Use environment/secret manager and redaction. Never expose secrets to agents.

### Prompt injection in news
News title/description/content is untrusted data. Article text must not alter tool permissions or workflow state.

### Arbitrary remote fetch
Provider adapters use allowlisted base URLs. Runtime agents cannot submit arbitrary URLs.

### Rate-limit abuse
Server-side concurrency and retry budgets.

### Data licensing
Do not store/re-distribute full article bodies where licensing prohibits it. Prefer metadata/hashes/source links and permitted excerpts.

### Test leakage
Role/state authorization blocks future data from historical training/evaluation contexts.

### Broker execution
No trading/order APIs in v1.

## 6. Authorization

Remote MCP should use authenticated clients and least-privilege scopes.

Suggested scopes:
```text
research:market
research:news
research:analytics
research:report
```

## 7. Report safety

Every report includes analysis timestamp, data freshness, signal version, methodology, limitations, and a non-personalized research notice.

## 8. Audit ledger

Persist data retrieval, provider errors, agent decisions, tool calls, signal generation, report publication, config changes, and model versions as append-only audit events.
