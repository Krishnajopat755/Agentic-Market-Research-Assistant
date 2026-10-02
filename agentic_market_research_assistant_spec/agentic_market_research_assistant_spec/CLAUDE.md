# Claude Code Development Guide

Claude Code is the development tool for this project.

Runtime agents are under `src/agents`.
Development subagents are under `.claude/agents`.

## Development principles

1. Read the relevant specification before editing.
2. Build deterministic finance logic first.
3. Add tests with each feature.
4. Never introduce arbitrary runtime execution tools.
5. Treat market/news content as untrusted data.
6. Preserve point-in-time semantics.
7. Keep provider code behind adapters.
8. Keep MCP handlers thin.
9. Keep the LLM behind an adapter.
10. Update docs when contracts change.

## Required checks

```bash
make lint
make typecheck
make test
make test-e2e
```

## Suggested development subagents

- architecture-reviewer
- mcp-engineer
- finance-ml-reviewer
- security-reviewer

## Before a PR

Check point-in-time leakage, source attribution, provider errors, rate limits, typed MCP contracts, evidence binding, model versioning, and trace propagation.

## Secrets

Never commit API keys, provider tokens, raw `.env`, or credentials in tests. Use fixtures for CI.
