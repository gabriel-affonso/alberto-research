# Roadmap

This roadmap describes intended direction, not binding commitments.

## Current — v0.1.0

Alberto Research currently provides:

- Literature discovery through Crossref and Semantic Scholar.
- DOI normalisation and deduplication.
- A legal open-access full-text resolver chain.
- LLM screening and deep reading, with JSON Schema validation before structured
  output is persisted.
- SQLite persistence, digest/newsletter generation, and Zotero, Notion and
  SMTP/email integrations.
- CI, security scanning, and reproducibility infrastructure.

The existing trust boundaries remain foundational: external content is hostile
input, deterministic work stays in Python, and structured LLM output is only
persisted after JSON Schema validation.

**Guiding constraints for everything below:** external content is hostile input;
LLM output is persisted only after JSON Schema validation; deterministic work
stays in Python; optional shadow-library resolvers stay disabled by default.

- **Legal clarity.** Keep the open-access-only path the default and the
  shadow-library resolvers explicitly opt-in, documented and the operator's
  responsibility. See [SECURITY.md](SECURITY.md).

## v0.2 / V2 — Autonomous Research Runtime

The principal architectural direction for v0.2/V2 is to remove OpenClaw as a
structural dependency for pipeline execution. Alberto Research should be able to
run as an independent application through its own abstraction for LLM task
execution:

```text
Alberto Research
        ↓
Internal Agent / Runtime Abstraction
        ↓
Configurable LLM Providers
```

OpenClaw may remain available as an optional integration, adapter, compatible
backend, or execution provider; it should not be an architectural requirement
for Alberto Research to function.

Potential v0.2/V2 work includes:

- Provider abstraction for LLM execution, with configurable OpenAI, Anthropic,
  OpenAI-compatible, and local-model providers.
- Native task orchestration and an optional OpenClaw adapter.
- Prompt, schema, and model/version provenance.
- Improved observability.
- Incremental full-text caching.
- A resolver plugin API.

This is a documented direction only; the autonomous runtime is not implemented
in v0.1.0.

## Future / 2027

Possible longer-term work includes:

- Contradiction detection and corpus-level synthesis.
- Multi-language digests and enhanced provenance.
- OpenTelemetry support and a plugin ecosystem.
- Larger-scale systematic-review workflows.
- Reproducible research reports.

## Out of scope

- Any change that makes shadow-library resolvers reachable by default.
- Bypassing paywalls or access controls anywhere outside the explicitly opt-in
  legacy resolvers.
- Bundling credentials, datasets, or operational data with the package.
- Operating production infrastructure for users.

## How to influence the roadmap

Open an issue describing the problem you have and the outcome you want, or
comment on an existing roadmap issue. Proposals that include a concrete use case,
a sketch of the approach, and an offer to help carry more weight. Decisions are
made per [GOVERNANCE.md](GOVERNANCE.md).
