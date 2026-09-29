<!--
Thanks for contributing! Keep this checklist in the description and tick items
off as you go. Delete rows that genuinely do not apply.
-->

## Summary

<!-- What does this change and why? Link the issue it closes, if any. -->

Closes #

## Type of change

- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change
- [ ] Documentation only
- [ ] CI/CD or tooling only

## Checklist

### Tests
- [ ] Tests added or updated for the behaviour changed
- [ ] No test relies on network access, real credentials or the disabled
      `legacy-resolvers` extra

### Local checks
- [ ] `ruff check .` passes
- [ ] `ruff format --check .` passes
- [ ] `mypy` passes
- [ ] `pytest` passes (coverage did not drop)

### Documentation and metadata
- [ ] `CHANGELOG.md` updated under an "Unreleased" heading
- [ ] Docs updated (`docs/**`, `README.md`) if user-visible behaviour changed
- [ ] Public API changes reflected in type hints and docstrings
- [ ] Schema changes ship with a migration

### Security and hygiene
- [ ] No secrets, tokens, personal paths or credentials committed
- [ ] No new HIGH/CRITICAL bandit or pip-audit findings (or they are
      documented as accepted risk in `SECURITY_AUDIT.md`)
- [ ] External input is still treated as hostile and validated against schema

### Sign-off
- [ ] Commits are DCO signed off (`git commit -s`)
