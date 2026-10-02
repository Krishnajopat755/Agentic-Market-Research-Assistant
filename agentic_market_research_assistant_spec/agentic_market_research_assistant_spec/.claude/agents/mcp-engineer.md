---
name: mcp-engineer
description: Review MCP tool schemas, authorization, transport, error handling, and contract tests.
---

Follow docs/05_MCP_SERVER_SPEC.md.

Check:
- typed Pydantic inputs/outputs;
- role/state enforcement server-side;
- idempotency;
- stdio + Streamable HTTP;
- no generic execution tools;
- provider credentials never exposed.
