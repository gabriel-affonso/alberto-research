# Roadmap

This roadmap describes intended direction, not commitments. Priorities can shift
as the project learns. Items are ordered by quarter; anything not finished rolls
into the next quarter rather than being silently dropped.

**Where we are now:** `0.1.0` provides discovery, DOI normalisation,
deduplication, full-text resolution with a pluggable resolver chain, SQLite
storage with versioned migrations, OpenClaw-backed screening and deep reading
with JSON-Schema-validated output, digest generation, and Zotero/Notion
synchronisation.

**Guiding constraints for everything below:** external content is hostile input;
LLM output is persisted only after JSON Schema validation; deterministic work
stays in Python; optional shadow-library resolvers stay disabled by default.

## 2026

| Quarter | Milestone | Description | Status |
| ------- | --------- | ----------- | ------ |
| Q1 2026 | Resolver plugin API | Promote the internal resolver chain to a documented, versioned plugin API. Third-party resolvers register via entry points, declare capabilities (OA location, licence, media type) and are isolated behind a stable contract. Ships with a conformance test kit and a template resolver. | Planned |
| Q1 2026 | Incremental full-text cache | Cache resolved full texts and extracted text on disk keyed by DOI plus content hash, with per-source invalidation, size/age limits and a safe purge command. Re-runs stop re-downloading unchanged documents. | Planned |
| Q2 2026 | Contradiction detection | Extract claims and findings as structured, schema-validated records and surface conflicting claims across a corpus. Every contradiction report cites the supporting passages and records the model, prompt and schema version used to derive it. | Planned |
| Q2 2026 | Multi-language digests | Generate digests and newsletters in languages other than English, with per-language templates, terminology handling, and deterministic fallbacks when a translation model is unavailable. | Planned |
| Q3 2026 | OpenTelemetry tracing | Emit traces, metrics and structured logs for discovery, resolution, screening, reading and delivery. Provider calls, retries, cache hits and schema-validation failures become observable, with sensitive content redacted by default. | Planned |
| Q3 2026 | SBOM and attestation hardening | Generate a CycloneDX SBOM for every release, sign artifacts and provenance attestations, and wire dependency and container scanning into CI as a release gate. | Planned |
| Q4 2026 | Hardening and 0.2.0 | Consolidate the year's work into `0.2.0`: close remaining gaps in the plugin API and cache, stabilise public interfaces, improve operator documentation, and cut a release with signed SBOM and provenance attestations. | Planned |

## Themes across the year

- **Trust boundaries.** Keep the hostile-input model and the JSON-Schema
  validation boundary explicit as new providers, resolvers and LLM tasks are
  added.
- **Observability.** An operator should be able to answer "why did this paper
  not appear in the digest?" without reading source code.
- **Reproducibility.** Record enough provenance — versions, prompts, schemas,
  source URLs — that a digest can be explained and audited after the fact.
- **Legal clarity.** Keep the open-access-only path the default and the
  shadow-library resolvers explicitly opt-in, documented and the operator's
  responsibility. See [SECURITY.md](SECURITY.md).

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
