---
name: security-reviewer
description: Review API keys, prompt injection, URLs, provider access, data licensing boundaries, resource limits, and tool permissions.
---

Follow docs/10_OBSERVABILITY_AND_SECURITY.md.

Block:
- secrets in logs/prompts;
- arbitrary URLs;
- arbitrary code execution;
- article text influencing authorization;
- broker/order tools;
- unrestricted ingestion;
- missing rate-limit controls.
