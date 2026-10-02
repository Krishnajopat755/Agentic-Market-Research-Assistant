# Acceptance Criteria

## Data
- [ ] symbols validated;
- [ ] event/availability/retrieval timestamps stored;
- [ ] stale data detected;
- [ ] attribution preserved;
- [ ] news dedup implemented;
- [ ] provider errors typed.

## Analytics
- [ ] SMA;
- [ ] EMA;
- [ ] RSI;
- [ ] MACD;
- [ ] ATR/volatility;
- [ ] volume analysis;
- [ ] sentiment;
- [ ] aggregate sentiment;
- [ ] research features;
- [ ] deterministic scorecard.

## ML
- [ ] baseline classifier;
- [ ] walk-forward evaluation;
- [ ] no shuffled time-series split;
- [ ] look-ahead-bias test;
- [ ] feature/model versioning;
- [ ] optional LSTM extension behind explicit config.

## Agents
- [ ] Market Data Agent;
- [ ] Sentiment & Technical Agent;
- [ ] Synthesis & Report Agent;
- [ ] dedicated prompts;
- [ ] structured outputs;
- [ ] bounded retries.

## MCP
- [ ] current protocol/SDK baseline;
- [ ] typed tools;
- [ ] role permissions;
- [ ] state permissions;
- [ ] idempotency;
- [ ] stdio;
- [ ] Streamable HTTP;
- [ ] no generic execution.

## Reports
- [ ] Markdown;
- [ ] HTML;
- [ ] JSON;
- [ ] evidence mapping;
- [ ] source URLs;
- [ ] freshness;
- [ ] signal version;
- [ ] caveats;
- [ ] research-use notice.

## Reliability
- [ ] rate-limit backoff;
- [ ] provider outage recovery;
- [ ] checkpoint/resume;
- [ ] cache;
- [ ] duplicate-call safety.

## Security
- [ ] API key redaction;
- [ ] prompt-injection fixture;
- [ ] no arbitrary URLs;
- [ ] no broker/order tools;
- [ ] server-side authorization.

## Portfolio
- [ ] fixture demo;
- [ ] live-provider demo;
- [ ] MCP tool trace;
- [ ] MLflow experiment;
- [ ] OpenTelemetry trace;
- [ ] polished sample report.
