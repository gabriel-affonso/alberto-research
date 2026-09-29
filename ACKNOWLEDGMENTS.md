# Acknowledgments

Alberto Research stands on a lot of other people's work. This file credits the
services and libraries the project depends on, and the people who contribute to
it.

## Upstream services and APIs

| Service | What we use it for |
| ------- | ------------------ |
| [Crossref](https://www.crossref.org/) | Authoritative DOI metadata and registration agency records. |
| [Unpaywall](https://unpaywall.org/) | Legal open-access locations for a DOI. |
| [OpenAlex](https://openalex.org/) | Open bibliographic graph: works, authors, venues, concepts. |
| [CORE](https://core.ac.uk/) | Aggregated open-access full texts from repositories. |
| [DOAJ](https://doaj.org/) | Directory of open-access journals and articles. |
| [Europe PMC](https://europepmc.org/) | Life-science literature, abstracts and open-access full text. |
| [Semantic Scholar](https://www.semanticscholar.org/) | Discovery, citation context and related-paper signals. |
| [Zotero](https://www.zotero.org/) | Reference library synchronisation. |
| [Notion](https://www.notion.so/) | Publishing digests and reading notes. |
| OpenClaw | Agent runtime that backs screening and deep reading. |

These services are independent projects with their own terms of service, rate
limits and data policies. Please respect them when running Alberto Research
against their APIs, and cite them as their maintainers ask.

## Python libraries

| Library | What we use it for |
| ------- | ------------------ |
| [requests](https://requests.readthedocs.io/) | HTTP access to provider APIs and open-access locations. |
| [pypdf](https://pypdf.readthedocs.io/) | Extracting text from PDF full texts. |
| [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) (`beautifulsoup4`) | Parsing HTML landing pages and metadata. |
| [jsonschema](https://python-jsonschema.readthedocs.io/) | Validating structured LLM output before it is persisted. |
| [PyYAML](https://pyyaml.org/) | Reading project configuration files. |
| [urllib3](https://urllib3.readthedocs.io/) | HTTP transport, retries and connection pooling. |

Additional development and test tooling — `pytest`, `hypothesis`, `mypy`,
`ruff`, `pre-commit`, `bandit`, `pip-audit`, `mutmut` — is credited to its
respective maintainers and is listed in `pyproject.toml`.

## Honourable mentions

- [Keep a Changelog](https://keepachangelog.com/) and
  [Semantic Versioning](https://semver.org/) for the conventions this project
  follows.
- [Contributor Covenant](https://www.contributor-covenant.org/) for the Code of
  Conduct this project adopts.
- [Conventional Commits](https://www.conventionalcommits.org/) and the
  [Developer Certificate of Origin](https://developercertificate.org/) for the
  contribution conventions.
- [all-contributors](https://allcontributors.org/) for the specification and bot
  used to recognise contributions.

## Contributors

Contributors are recognised with the
[all-contributors](https://allcontributors.org/) specification. The canonical
list lives in [`.all-contributorsrc`](.all-contributorsrc) and is rendered into
the README badge and table; contributions of every kind count, not only code.

To add someone, comment on an issue or pull request:

```
@all-contributors please add @username for code, doc, test
```

Thank you to everyone who has filed a bug, sharpened a docstring, reviewed a
pull request, or asked a question that made the project better.
