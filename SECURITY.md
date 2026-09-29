# Security Policy

Alberto Research processes hostile, untrusted input by design: bibliographic
metadata, full-text PDFs, abstracts, provider responses and email bodies are all
treated as attacker-controlled. This document explains how to report a
vulnerability, what we commit to, and what is intentionally outside our scope.

## Supported versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

Only the latest `0.1.x` release receives security fixes. Pre-release and
unreleased development snapshots are provided as-is and are not supported.

## Reporting a vulnerability

Please report suspected vulnerabilities through GitHub private vulnerability
reporting:

<https://github.com/gabriel-affonso/alberto-research/security/advisories/new>

This is the preferred channel because it keeps the report confidential, gives us
a private place to collaborate on a fix, and lets us publish a coordinated
advisory with credit. Please do **not** open a public issue for a security
problem, and please prefer private reporting over email.

A useful report includes:

- the affected version or commit;
- a minimal reproduction or proof of concept;
- the impact you believe the issue has;
- any suggested remediation;
- whether you intend to disclose publicly, and on what timeline.

Do not include live credentials, personal data, or third-party copyrighted
material in the report. Redact as needed.

## Response timeline

| Stage                          | Target                          |
| ------------------------------ | ------------------------------- |
| Acknowledge receipt            | within 72 hours                 |
| Triage and severity assessment | within 7 days                   |
| Fix or mitigation plan         | within 30 days                  |

Timelines are best-effort commitments from a small maintainer team. If a fix
requires coordinated upstream work, we will tell you and share the mitigation
plan at the 30-day mark rather than silently slipping.

We will keep you informed of progress, credit you in the advisory unless you ask
otherwise, and coordinate disclosure timing with you.

## Scope

In scope:

- the `alberto-research` Python package published from this repository,
  including its CLI, storage and migration layer, resolver chain, provider
  clients, schema validation and delivery plumbing;
- the packaged configuration templates and their safe defaults;
- anything that lets untrusted input (a paper, abstract, metadata record, HTTP
  response, PDF, or email) escape its intended trust boundary, execute code,
  read files it should not, reach the network from an unintended context, or
  corrupt persisted state.

Out of scope:

- **The OpenClaw runtime.** OpenClaw is a separate project. Configuration of the
  runtime, its agent isolation model, its credential handling and its deployment
  are not part of this package. Report those to the OpenClaw maintainers.
- **Third-party providers and services.** Availability, correctness, rate
  limiting, account terms and data handling of Crossref, Unpaywall, OpenAlex,
  CORE, DOAJ, Europe PMC, Semantic Scholar, Zotero, Notion, or any LLM provider
  are their responsibility, not ours.
- **Local operational data and host configuration.** Databases, downloaded
  full texts, tokens, API keys and workspace layout are operator-supplied state.
- Vulnerabilities that require an already-compromised host, an attacker who can
  write to the package's own source tree, or a deliberately misconfigured
  deployment that ignores the documented safe defaults.

## Threat model notes

The project is built around a small number of load-bearing assumptions. Reports
that demonstrate a bypass of one of them are high priority.

- **All external content is hostile.** Papers, abstracts, metadata records,
  provider JSON/XML, PDFs and email bodies are untrusted. They are parsed, not
  trusted. Text extracted from them is never interpreted as instructions, and
  never used to select tools, paths, URLs or credentials.
- **LLM output is untrusted until validated.** Structured model output is
  persisted only after it passes JSON Schema validation. A response that fails
  validation is rejected or quarantined, never written to the database as
  authoritative. Prompt injection through document content is expected and must
  not translate into privileged action.
- **Network egress is explicit.** Providers are contacted through their public
  APIs with operator-configured credentials. Untrusted content must not be able
  to direct a request to an arbitrary host.
- **Storage is parameterised.** Database access uses bound parameters and
  versioned SQL migrations; no untrusted value is interpolated into SQL.
- **Secrets stay out of the repo.** Credentials live in the environment or
  OpenClaw configuration, never in committed files or logs.

## Shadow-library resolvers

This section is deliberately explicit, because the feature is easy to
misunderstand and carries real legal risk.

- Optional resolvers that target **Sci-Hub**, **LibGen** and **Anna's Archive**
  exist in the source tree as legacy integrations.
- They are **DISABLED by default**. A default installation cannot reach them.
- Enabling them requires **both** installing the `legacy-resolvers` extra
  (`pip install "alberto-research[legacy-resolvers]"`) **and** setting
  `enable_scihub: true` explicitly, per project, in that project's
  configuration. There is no global switch and no implicit fallback to them.
- These resolvers **disable TLS certificate verification** — they call
  `requests.get(..., verify=False)` — so their traffic is not protected against
  interception. Do not treat any content retrieved this way as trustworthy.
- **Using them is the operator's sole legal responsibility.** Copyright and
  related law differ by jurisdiction, and the maintainers cannot evaluate your
  situation. The maintainers make **no warranty** of any kind about these
  resolvers, their availability, their legality in your jurisdiction, or the
  content they return, and accept no liability for their use.
- **The rest of the project does not bypass paywalls.** Outside of these
  explicitly opt-in legacy resolvers, full-text resolution uses only legal
  open-access sources: **Unpaywall**, **OpenAlex**, **CORE**, **DOAJ** and
  **Europe PMC**. When an article is not openly available, the project records
  it as unavailable rather than circumventing access controls.

If you find a path that reaches a shadow-library resolver without the
`legacy-resolvers` extra installed *and* `enable_scihub: true` set, treat it as a
security issue and report it privately using the process above.

## Safe configuration reminders

- Keep `enable_scihub: false` unless you have made an informed legal decision.
- Run the reader with the least privilege available: no finance data, no broad
  filesystem access, no email permissions, no destructive tools.
- Store API tokens in the environment or OpenClaw configuration, not in files
  that are committed or shared.
- Treat every downloaded document and every model response as untrusted input,
  because that is exactly what they are.
