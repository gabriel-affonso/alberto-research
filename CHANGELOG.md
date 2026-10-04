# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-10-04

### Changed

- Corrected public release metadata for v0.1.0 and refreshed citation details.
- Updated the roadmap to reflect the current v0.1.0 state and document the
  v0.2/V2 Autonomous Research Runtime direction.
- Validated a clean-install dry-run and improved release discoverability
  documentation.

## [0.1.0] - 2026-10-03

### Added

- Discovery of scientific literature through Crossref and Semantic Scholar,
  with configurable queries, paging and per-provider rate limiting.
- DOI normalisation and deduplication, so records for the same work coming from
  different providers collapse into a single canonical entry.
- Full-text resolution with a pluggable resolver chain: resolvers are tried in
  order, report why they failed, and fall back to legal open-access sources
  (Unpaywall, OpenAlex, CORE, DOAJ, Europe PMC).
- SQLite storage with versioned SQL migrations, giving a durable local corpus
  that can be upgraded in place as the schema evolves.
- Screening and deep reading backed by OpenClaw, with all structured model
  output validated against JSON Schema before it is persisted.
- Digest and newsletter generation from screened and read papers, with
  configurable sections, ranking and delivery formatting.
- Zotero synchronisation for pushing curated references into an existing
  library, and Notion synchronisation for publishing digests and reading notes.
- The `alberto-research` command-line interface for running discovery, full-text
  resolution, screening, reading, digest generation and synchronisation.

[Unreleased]: https://github.com/gabriel-affonso/alberto-research/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/gabriel-affonso/alberto-research/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/gabriel-affonso/alberto-research/releases/tag/v0.1.0
