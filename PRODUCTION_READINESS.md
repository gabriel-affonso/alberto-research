# PRODUCTION_READINESS.md — Alberto Research

**Data:** 2026-09-29
**Artefato:** repositório limpo `alberto-research` (extraído do monorepo `Alberto`)
**Versão:** 0.1.0 (gerenciada por `hatch-vcs` a partir de tags Git)
**Veredito:** **pronto para revisão humana e para o primeiro push — não pronto para publicação pública autônoma.** Há dois bloqueadores que exigem decisão/ação do autor (§4.1 e §4.2).

---

## 1. Sumário executivo

O subsistema de pesquisa do monorepo foi extraído para um repositório independente, renomeado para o namespace `alberto_research`, isolado de todo o material pessoal (agente de viagens, automação de pagamento, revisão de literatura) e levado a **todos os quality gates verdes**:

| Gate | Comando | Resultado |
|---|---|---|
| Lint | `ruff check src tests` | ✅ **All checks passed** |
| Formatação | `ruff format --check src tests` | ✅ **49 files already formatted** |
| Tipos | `mypy` (`strict = true`) | ✅ **Success: no issues found in 35 source files** |
| Testes | `pytest` | ✅ **112 passed, 2 skipped** |
| Cobertura | `--cov-fail-under=60` | ✅ **62,88 %** (meta ideal de 80 % **não atingida**) |
| Segurança de código | `bandit -r src -ll -s B501,B113,B608` | ✅ exit 0 (3 skips documentados) |
| Segredos | `gitleaks` + `trufflehog` + `detect-secrets` | ✅ **0 segredos** no histórico completo |
| Dependências | `pip-audit` + `osv-scanner` | ✅ **0 vulnerabilidades** em 15 pacotes |

O histórico do monorepo **nunca conteve segredos** — conclusão corroborada por quatro métodos independentes. O que resta são decisões humanas e verificações que só podem ocorrer após o push (CI real, proteções de branch, publicação).

**Riscos residuais** e **ações do autor** estão detalhados em §4 e §5. O mais importante: o autor optou por **manter** a trilha de *shadow libraries* (com `verify=False`) sob licença **MIT** de intenção pública. Essa combinação é juridicamente inconsistente e **exige sign-off registrado antes de tornar o repositório público**.

---

## 2. Estado atual vs. estado desejado

| Dimensão | Antes (monorepo) | Depois (`alberto-research`) |
|---|---|---|
| Identidade | `alberto` (Proprietary, monorepo pessoal) | `alberto-research` (MIT, pacote isolado) |
| Layout | `src/alberto/research/*` | `src/alberto_research/*` (src-layout) |
| CLI | `alberto research …` (enterrado no monorepo) | `alberto-research {run,digest,feedback,notion,db,config}` |
| Empacotamento | `setuptools`, sem lockfile | `hatchling` + `hatch-vcs`, PEP 621, 2 lockfiles com hash |
| Migrations | em `migrations/` na raiz (fora do pacote) | **dentro do pacote** — `pip install` + `db migrate` funciona |
| Dependências | 2 declaradas sem uso, 4 usadas sem declaração | corretas; trilha sensível isolada no extra `legacy-resolvers` |
| Caminho do OpenClaw | `/home/alberto/.openclaw/bin/openclaw` fixo | resolvido por config → env → `PATH` |
| Testes | 0 CLI, logging não coberto | 112 testes, incl. CLI e logging |
| Tipos | não verificados | `mypy --strict` limpo |
| Segurança | sem varredura, `SECURITY.md` incorreto | 4 varreduras, SBOM, relatório de auditoria, `SECURITY.md` veraz |
| CI/CD | inexistente | 7 workflows + Dependabot + CodeQL + Scorecard |
| Docs | README monolítico | README pt-BR + en, 11 páginas MkDocs Material |
| Governança | `SECURITY.md` apenas | LICENSE, CONTRIBUTING (DCO), CoC 2.1, GOVERNANCE, ROADMAP, CHANGELOG, CITATION.cff |

---

## 3. Inventário do artefato

```
alberto-research/
├── .github/            7 workflows + dependabot + CODEOWNERS + PR/issue templates
├── docs/               11 páginas (pt-BR) + mkdocs.yml
├── examples/           basic.yaml, advanced.yaml, newsletter-only.yaml
├── sbom/               cyclonedx.json (CycloneDX 1.6, 30 componentes)
├── scripts/            check.sh, lock.sh (shellcheck limpos)
├── src/alberto_research/   35 módulos + migrations/*.sql + py.typed
├── tests/              112 testes (unit + integração, offline)
├── Dockerfile          multi-stage, não-root, healthcheck
├── requirements.lock       427 linhas, 385 pinos com hash
├── requirements-dev.lock  1567 linhas, 1354 pinos com hash
└── 11 arquivos de governança + pyproject.toml + .env.example + 4 configs de tooling
```

**Localização do pacote no monorepo original:** `src/alberto/research/`, `src/alberto/db/`, `src/alberto/enums.py`.

---

## 4. Checklist de produção

Legenda: ✅ feito e verificado · ⚠️ feito parcialmente / verificação pendente · ❌ não feito · N/A não aplicável.

### 4.1 Segurança

| Item | Estado | Evidência / justificativa |
|---|---|---|
| Nenhum segredo no histórico do novo repo | ✅ | `gitleaks` 8.30.1: 0 vazamentos (39 commits); `trufflehog` 3.97.9: 0 verificados **e** 0 não verificados (504 chunks); varredura própria: 271 blobs, 0 hits |
| `gitleaks`, `trufflehog`, `detect-secrets` limpos | ✅ | `detect-secrets`: 1 achado = **falso positivo** (`tests/test_fulltext.py:255`) — ver `SECURITY_AUDIT.md` §6.1 |
| Branch protection ativa | ❌ | Exige push e API do GitHub. Comandos prontos em `MIGRATION.md` |
| Secret scanning + push protection ativos | ❌ | Exige o repositório criado no GitHub |
| Dependabot ativo | ⚠️ | `.github/dependabot.yml` versionado; passa a valer após o push |
| CodeQL ativo | ⚠️ | Job `security` do `ci.yml`; primeira execução pendente |
| SBOM gerado e publicado | ⚠️ | `sbom/cyclonedx.json` gerado (CycloneDX 1.6, 30 componentes). **SPDX não gerado**; o `release.yml` publica CycloneDX como artefato |
| SLSA provenance no release | ⚠️ | `actions/attest-build-provenance@v2` configurado no `release.yml`; nunca executado |
| Assinatura Sigstore nos artefatos | ❌ | `cosign` indisponível no host; atestação via GitHub está configurada como substituto |
| Commits assinados (GPG/SSH) | ❌ | **Ação do autor** — requer chave GPG/SSH configurada no GitHub |
| `verify=False` (SA-03) com sign-off | ❌ | **Bloqueador.** Risco Alta aceito verbalmente, sign-off formal pendente |
| Rotação de credenciais | ✅ N/A | Nenhuma credencial encontrada; nada a rotacionar |
| PII em conteúdo de arquivo | ✅ | 0 e-mails reais, 0 CPF/CNPJ, 0 telefones; caminho absoluto `/home/alberto` corrigido |
| PII em metadados de commit | ❌ | **Ação do autor**: histórico do monorepo usa `<e-mail-pessoal-REDACTED>` (41 entradas) |

### 4.2 Qualidade

| Item | Estado | Evidência |
|---|---|---|
| Cobertura ≥ 80 % | ❌ | **62,88 %** (gate em 60 %). Gap de ~17 p.p. — ver §6 |
| `mypy --strict` sem erros | ✅ | `strict = true`; *Success: no issues found in 35 source files* |
| ruff/format/isort limpos | ✅ | `All checks passed!` / `49 files already formatted` |
| bandit sem findings medium/high | ⚠️ | Green **apenas com 3 skips documentados** (`B501` risco aceito; `B113`/`B608` falsos positivos) |
| pip-audit sem high/critical | ✅ | 15 pacotes, 0 vulnerabilidades |
| OSV sem vulnerabilidades | ✅ | 15 pacotes lidos, *No issues found* |
| Mutation score ≥ 60 % em `core/` | ❌ | `mutmut` 3.x falhou ao inicializar neste host; **nunca executado** |
| Docstrings em toda API pública | ❌ | Regras `D1xx` relaxadas de forma documentada em `pyproject.toml`; módulos e APIs públicas têm docstring, helpers privados não |

### 4.3 Documentação

| Item | Estado | Evidência |
|---|---|---|
| README pt-BR + en | ✅ | `README.md` (14,8 KB) + `README.en.md` (14,0 KB), 17 seções, aviso legal |
| `docs/` publicada em Pages | ⚠️ | 11 páginas + `mkdocs.yml` prontos; `mkdocs build` **não executado** (mkdocs indisponível no host) e deploy depende do push |
| `CITATION.cff` válido | ✅ | CFF 1.2.0; sem ORCID/DOI (não inventados) |
| `CHANGELOG.md` atualizado | ✅ | Keep a Changelog 1.1.0 + SemVer 2.0.0, com `[Unreleased]` e `[0.1.0]` |
| `.env.example` completo | ✅ | Todas as variáveis reais, cada uma comentada |
| `SECURITY_AUDIT.md` | ✅ | Completo, com tabela de achados, ação imediata, falsos positivos e riscos aceitos |

### 4.4 Empacotamento

| Item | Estado | Evidência |
|---|---|---|
| `pyproject.toml` PEP 621 | ✅ | `hatchling` + `hatch-vcs`, extras `test`/`dev`/`docs`/`legacy-resolvers` |
| Lockfiles com hash | ✅ | 385 + 1354 pinos com hash |
| `pip install alberto-research` | ✅ | Wheel construído e inspecionado: inclui `migrations/*.sql`, `py.typed`, `_version.py` |
| `pipx install` / `uv tool install` | ⚠️ | Caminho de instalação idêntico ao `pip`; não executado isoladamente |
| `alberto-research` CLI funcional | ✅ | `--version`, `db migrate`, `config validate`, `run`, `digest`, `feedback`, `notion` cobertos por teste |
| Dockerfile multi-stage | ⚠️ | Escrito e revisado manualmente; `docker build` **não executado** (sem Docker no host) |
| Hadolint OK | ❌ | Sem binário para macOS e sem Docker; revisão manual apenas |
| Trivy sem high/critical | ❌ | Indisponível no host |

### 4.5 Governança

| Item | Estado |
|---|---|
| LICENSE, SECURITY, CONTRIBUTING, CODE_OF_CONDUCT, GOVERNANCE | ✅ todos presentes |
| `CODEOWNERS` | ✅ `* @gabriel-affonso` + caminhos sensíveis |
| Templates de issue/PR | ✅ 3 issue forms + `pull_request_template.md` |
| DCO + Conventional Commits | ✅ documentados em `CONTRIBUTING.md` |
| `GOVERNANCE.md` (BDFL → meritocracia) | ✅ |
| `ROADMAP.md`, `ACKNOWLEDGMENTS.md`, `MIGRATION.md` | ✅ |

### 4.6 Operacional

| Item | Estado | Evidência |
|---|---|---|
| CI verde em 3 SOs × 3 versões | ⚠️ | Matrix 5 legs configurada (ubuntu 3.11/3.12/3.13 + macos 3.11 + windows 3.11); **nunca executada** — só roda após o push |
| Release automatizado por tag | ⚠️ | `release.yml` com Trusted Publishing OIDC + SBOM + atestação; não executado |
| Docs deploy automatizado | ⚠️ | `docs.yml` com `deploy-pages`; não executado |
| Monitoramento (Sentry/OTel) | ❌ | Fora do escopo desta entrega; listado no `ROADMAP.md` |
| Environments `pypi`/`production` com revisores | ❌ | Ação do autor no GitHub |

---

## 5. Ações pendentes do autor

Ordenadas por prioridade. **Nada foi enviado a nenhum remoto.**

1. **Registrar o sign-off do risco SA-03** (bloqueador de publicação). Confirmar por escrito a aceitação de manter `verify=False`; ciente de que isso é incompatível com a intenção de licença MIT em repositório público.
2. **Decidir sobre a publicação pública vs. privada.** Enquanto o item 1 não for resolvido, considerar repositório privado.
3. **Configurar a identidade Git** antes do commit inicial:
   `git config user.email "gabriel.affonso@users.noreply.github.com"` e habilitar *email privacy* no GitHub.
4. **Criar o repositório remoto** e fazer o push (comandos em §7.2) — somente após autorização textual explícita.
5. **Configurar as proteções do GitHub** (branch protection em `main`, tag protection `v*.*.*`, secret scanning + push protection, Dependabot, CodeQL, relatório privado de vulnerabilidades, environments `pypi`/`production`). Roteiro em `MIGRATION.md`.
6. **Configurar PyPI Trusted Publishing** para `alberto-research` (sem token de API).
7. **Gerar chave GPG/SSH** e habilitar commits assinados.
8. **Executar a validação de container** (`docker build`, `hadolint`, `trivy`) onde houver Docker.
9. **Rodar o mutation testing** (`mutmut run`) para fechar o gate de mutação.
10. **Elevar a cobertura** de 62,9 % para ≥ 80 % (ver §6).
11. **Preencher o contato do `CODE_OF_CONDUCT.md`** (hoje um placeholder sem e-mail real).
12. **Confirmar o slug do repositório.** O remoto atual tem um erro de digitação (`Alberto-Reserach`); todos os links do pacote novo usam `alberto-research`.

---

## 6. Riscos residuais e mitigações

| # | Risco | Sev. | Mitigação atual | Ação necessária |
|---|---|---|---|---|
| R1 | `verify=False` na trilha de *shadow libraries* (SA-03) | **Alta** | Desligada por padrão; extra opcional; documentada | **Sign-off + decisão de visibilidade**; opcionalmente `verify=True` com CA bundle |
| R2 | Licença MIT + código que contorna paywall | **Alta** | Documentado em README/SECURITY/AUDIT | Decisão jurídica do autor; alternativa: manter privado ou separar a trilha |
| R3 | Cobertura 62,9 % < 80 % | Média | Gate em 60 % (falha se cair) | Adicionar testes; priorizar `schemas.py`, `zotero.py`, `providers/*` |
| R4 | CI nunca executado | Média | Configuração revisada linha a linha e validada como YAML | Primeira execução após o push |
| R5 | Mutation score não medido | Média | — | Rodar `mutmut` em `core/` |
| R6 | E-mail pessoal em metadados de commit | Baixa | Novo repo nasce limpo | Usar `noreply` do GitHub |
| R7 | Dockerfile não construído | Baixa | Revisão manual contra regras do hadolint | `docker build` + `hadolint` + `trivy` no CI |
| R8 | Sem SBOM SPDX nem assinatura Sigstore | Baixa | CycloneDX + atestação de proveniência no release | Adicionar saída SPDX e `cosign` ao `release.yml` |
| R9 | Docstrings incompletas (`D1xx` relaxado) | Baixa | Regras relaxadas com justificativa versionada | Endurecer gradualmente; item no `ROADMAP.md` |

---

## 7. Comandos de verificação e migração

### 7.1 Verificação local (todos os gates)

```bash
cd alberto-research
python3.11 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"

ruff check . && ruff format --check .
mypy                                  # strict = true
pytest                                # 112 passed, cobertura ≥ 60 %
bandit -c pyproject.toml -r src -ll
pip-audit -r requirements.lock
osv-scanner scan source --lockfile=requirements.lock
gitleaks detect --source . --log-opts="--all" --redact
trufflehog git file://. --only-verified
python -m build && twine check dist/*
```

### 7.2 Migração e push (somente após autorização textual explícita)

Passo a passo completo e reversível em `MIGRATION.md`. Resumo:

```bash
# 1. Validar o artefato e a ausência de segredos
gitleaks detect --source . --log-opts="--all" --redact --verbose
trufflehog filesystem . --only-verified

# 2. Identidade pública (evita expor e-mail pessoal)
git config user.name  "Gabriel Affonso"
git config user.email "gabriel.affonso@users.noreply.github.com"

# 3. Commit inicial assinado + tag
git add -A
git commit -S -m "chore: initial commit — Alberto Research v0.1.0"
git tag -s v0.1.0 -m "Release v0.1.0"

# 4. PUSH — requer confirmação textual do autor
# git remote add origin git@github.com:gabriel-affonso/alberto-research.git
# git push -u origin main --tags
```

### 7.3 Configuração do GitHub (após o push)

```bash
gh api -X PUT repos/:owner/alberto-research/branches/main/protection \
  -F required_status_checks.strict=true \
  -F 'required_status_checks.contexts[]=lint' \
  -F 'required_status_checks.contexts[]=test (ubuntu-latest, 3.11)' \
  -F enforce_admins=true \
  -F required_pull_request_reviews.required_approving_review_count=1 \
  -F restrictions= \
  -F allow_force_pushes=false -F allow_deletions=false

gh api -X PATCH repos/:owner/alberto-research \
  -F security_and_analysis.secret_scanning.status=enabled \
  -F security_and_analysis.secret_scanning_push_protection.status=enabled
```

---

## 8. Manutenção mensal estimada

| Atividade | Esforço/mês |
|---|---|
| Triagem de PRs do Dependabot (pip, actions, docker) | 1–2 h |
| Triagem de alertas do CodeQL/Scorecard | 0,5–1 h |
| Revisão de issues e PRs de contribuição | 1–2 h |
| Atualização de lockfiles (`scripts/lock.sh`) e release | 0,5 h |
| **Total** | **≈ 3–5,5 h/mês** |

O custo é baixo porque as verificações são automatizadas. Os picos ocorrem com quebras de API de provedores externos (Crossref, Unpaywall, OpenAlex) ou com o fim de vida de versões do Python (a matrix 3.11–3.13 exige revisão anual).

---

## 9. Conclusão

O repositório `alberto-research` está **tecnicamente pronto**: lint, formatação, `mypy --strict`, testes, cobertura mínima, bandit, auditoria de dependências e varredura de segredos — todos verdes e reproduzíveis localmente. A extração removeu com sucesso todo o material pessoal e corrigiu três defeitos reais herdados (caminho fixo de host, dependências não declaradas, documentação de segurança incorreta).

**Não está pronto para publicação pública autônoma** por dois motivos que são decisões humanas, não técnicas: o sign-off do risco alto de TLS (§4.1/§5.1) e a coerência entre a licença MIT e a trilha de *shadow libraries* (§6, R2). Além disso, CI, proteções de repositório e publicação no PyPI só podem ser validados após o push.

**Nenhum `git push` foi executado.** Nenhuma operação irreversível foi realizada no repositório original.
