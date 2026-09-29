# Contributing to Alberto Research

Thanks for taking the time to contribute. This document describes how we work,
what we expect from a change, and how to get a development environment running.

By participating you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).
For security issues, do not open a public issue — follow [SECURITY.md](SECURITY.md).

## Workflow: GitHub Flow

We use [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow):

1. Fork the repository (or create a branch if you have write access).
2. Branch off `main`.
3. Make focused commits.
4. Open a pull request against `main`.
5. Respond to review, keep the branch current with `main`.
6. Squash or rebase as needed; `main` stays releasable at all times.

`main` is protected and always green. Nothing lands on `main` without a pull
request and review, including maintainer changes.

## Commit messages: Conventional Commits 1.0.0

Every commit must follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Allowed types:

| Type       | Use for                                                        |
| ---------- | -------------------------------------------------------------- |
| `feat`     | a new user-facing feature                                      |
| `fix`      | a bug fix                                                      |
| `docs`     | documentation only                                             |
| `style`    | formatting, whitespace, no behaviour change                    |
| `refactor` | restructuring without behaviour change                         |
| `perf`     | performance improvement                                        |
| `test`     | adding or correcting tests                                     |
| `build`    | build system or dependency changes                             |
| `ci`       | continuous integration configuration                           |
| `chore`    | maintenance that does not fit the above                        |
| `revert`   | reverting a previous commit                                    |

Breaking changes use `!` after the type/scope (for example
`feat(api)!: drop the v0 resolver`) and a `BREAKING CHANGE:` footer. Write commit
messages in English, in the imperative mood, with a subject line of 72
characters or fewer.

## Developer Certificate of Origin (DCO)

Every commit must be signed off under the
[Developer Certificate of Origin](https://developercertificate.org). Signing off
means you certify that you wrote the change, or otherwise have the right to
submit it under the project's license.

Add the sign-off automatically:

```bash
git commit -s -m "fix(providers): handle empty Crossref author list"
```

This appends a trailer to your commit message:

```
Signed-off-by: Your Name <the address configured in git config user.email>
```

Use your real name and a reachable address. Commits without a matching
sign-off cannot be merged. If you forget, amend with:

```bash
git commit --amend -s --no-edit
```

## Branch naming

Use a short, typed, kebab-case branch name:

```
<type>/<short-topic>
```

Examples: `feat/resolver-plugin-api`, `fix/doi-normalisation`,
`docs/security-policy`, `chore/bump-ruff`. Prefix with your handle only when it
helps disambiguate, for example `feat/ga-contradictions`.

## Local setup

Python 3.11 or newer is required.

```bash
uv venv --python 3.11 && uv pip install -e ".[dev]"
```

Then install the git hooks:

```bash
pre-commit install
```

## Quality gates

Run the full gate suite before opening a pull request:

```bash
pre-commit run --all-files
```

Under the hood this runs, at minimum:

```bash
ruff check .
ruff format --check .
mypy
pytest
```

All four must pass. `ruff check` covers lint and import order, `ruff format
--check` covers formatting, `mypy` runs in strict-ish mode against
`src/alberto_research`, and `pytest` runs the test suite. Fix the cause rather
than suppressing a check; if a suppression is genuinely correct, scope it as
narrowly as possible and explain why in the pull request.

## Pull request requirements

Before requesting review, make sure your pull request:

- [ ] is focused on one change and linked to the issue it addresses;
- [ ] adds or updates tests for the behaviour it changes — bug fixes should
      include a regression test that fails without the fix;
- [ ] passes `ruff check .` and `ruff format --check .`;
- [ ] passes `mypy`;
- [ ] passes `pytest`;
- [ ] adds an entry under `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md),
      using the appropriate `### Added` / `### Changed` / `### Fixed` /
      `### Removed` / `### Security` heading;
- [ ] contains only sign-off'd commits;
- [ ] contains no credentials, tokens, personal data, or local operational data;
- [ ] updates documentation when behaviour or configuration changes.

Persistent schema changes also require a versioned SQL migration. Add one; do
not edit a migration that has already shipped.

Large or non-obvious changes should be discussed in an issue before you write
much code, so we can agree on the approach early.

## Code style

- Follow **PEP 8** (style), **PEP 257** (docstrings) and **PEP 484** (type
  hints). Public functions and methods are fully type-annotated.
- Maximum line length is **100 columns**.
- Docstrings are **Google style**, on modules, public classes, and public
  functions.
- Code comments, docstrings, and commit messages are written in **English**.
- Prefer explicit, readable code over clever code. Keep deterministic work
  deterministic and keep LLM work behind explicit contracts.
- Treat all external content as hostile input, and persist structured LLM output
  only after JSON Schema validation.
- Do not add a dependency without discussing it first.

## Reporting bugs and requesting features

Use the issue templates. Include the version, the command you ran, what you
expected, and what happened. For resolver or provider problems, include the DOI
or the sanitised request/response pair — never an API key.

## License

By contributing, you agree that your contributions are licensed under the
project's MIT License, and you confirm this with the DCO sign-off on each commit.
