# Portfolio Demo

## 1. Three-minute story

Problem: daily research is fragmented across market data, news, sentiment, indicators, and reporting.

Solution: an orchestrator coordinates three specialized agents through a finance MCP server.

Differentiator: agents cannot directly manipulate datasets or execute arbitrary code; MCP exposes narrow tools, while the analytics core performs deterministic calculations.

## 2. Demo sequence

```bash
docker compose up -d
make demo-aapl
```

Show:
- run ID;
- analysis timestamp;
- provider/freshness metadata;
- agent handoffs;
- MCP Inspector tool list;
- MLflow model/evaluation;
- OpenTelemetry trace;
- generated report.

Demonstrate a denied call:
```text
synthesis agent -> fetch_market_news
=> TOOL_NOT_AUTHORIZED
```

Demonstrate provider failure fixture:
- retry;
- backoff;
- recovery;
- trace.

Demonstrate point-in-time test:
- add future news;
- verify earlier signal is unchanged.

## 3. Screenshots

Capture:
1. architecture;
2. MCP Inspector;
3. trace;
4. MLflow;
5. report;
6. leakage test.

## 4. Resume bullets

Only use after the features exist.

Detailed:
> Built a multi-agent market research assistant with specialized market-data, sentiment/technical, and synthesis agents; exposed finance analytics through typed MCP tools, implemented point-in-time evaluation and look-ahead-bias controls, and added MLflow lineage, OpenTelemetry tracing, provider-failure recovery, and evidence-linked reporting.

Compact:
> Built an MCP-based multi-agent finance research system combining market/news APIs, sentiment, technical indicators, and reproducible time-series signal modeling.

## 5. Interview questions

- Why MCP rather than direct SDK imports?
- How is point-in-time correctness enforced?
- How are rate limits handled?
- How do you deduplicate news?
- Why can't synthesis retrieve news directly?
- How is stale data represented?
- Why is LSTM an extension rather than the first component?
- How is confidence calculated?
- How would a second data provider be added?
