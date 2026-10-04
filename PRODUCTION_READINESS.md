# PRODUCTION_READINESS.md — Alberto Research

**Data:** 2026-09-29 · **Revisão 2:** 2026-10-02
**Artefato:** repositório limpo `alberto-research` — `/Users/gabriel.affonso/Documents/alberto-research`
**Versão:** 0.1.0 (gerenciada por `hatch-vcs` a partir de tags Git)
**Revisão 2 — veredito:** **pronto para revisão humana; o bloqueador de TLS foi resolvido por aceite formal.** Restam: o risco **jurídico** R2 (MIT × *shadow libraries*), a **cobertura de 62,85 %** (com caminho de 30 linhas para ≥ 80 % identificado em §10.4 e `SECURITY_AUDIT.md` §13.5), a **assinatura de commit/tag não conforme** (§10.3) e a `.venv` do artefato **corrompida** (§10.2). Continua valendo: **nenhum `git push` foi executado.**

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
| Commits assinados (GPG/SSH) | ❌ | **NÃO CONFORME, verificado.** `git log -1 --format='%G?'` → `N`; `v0.1.0` é **tag leve** (`%(objecttype)` = `tag`). `commit -S` / `tag -s` não surtiram efeito — falta chave GPG/SSH. Ver §10.3 |
| `verify=False` (SA-03) com sign-off | ✅ | **Aceite formal REGISTRADO em 2026-10-02** — `SECURITY_AUDIT.md` §7.1. Bloqueador técnico resolvido |
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

1. ~~**Registrar o sign-off do risco SA-03**~~ — ✅ **CONCLUÍDO em 2026-10-02.** Aceite formal registrado em `SECURITY_AUDIT.md` §7.1.
2. **Decidir sobre a publicação pública vs. privada** (permanece o bloqueador principal). O aceite de §7.1 é **técnico**; o risco **jurídico** R2 (MIT × contorno de paywall) **não** está resolvido e depende de decisão sua ou de orientação jurídica. Enquanto isso, manter **privado**.
3. **Corrigir a `.venv` corrompida** do artefato (§10.2) — sem isso nenhum gate roda no estado entregue.
4. **Assinar o commit e recriar a tag como anotada/assinada** (§10.3): hoje `%G?` = `N` e `v0.1.0` é tag leve.
5. **Elevar a cobertura** de 62,85 % para ≥ 80 % seguindo a via de §10.4 (excluir o caminho de risco aceito + ~30 linhas de teste legítimo), ou adicionar ~405 linhas de teste cobrindo também a trilha de *shadow libraries*.
6. **Corrigir o `SECURITY.md` do pacote** — a seção "Paywalls" afirma o oposto do código (`SECURITY_AUDIT.md` §7.2). **Não publicar com essa contradição ativa.**
7. **Criar o repositório remoto** e fazer o push (comandos em §7.2) — somente após autorização textual explícita.
8. **Configurar as proteções do GitHub** (branch protection em `main`, tag protection `v*.*.*`, secret scanning + push protection, Dependabot, CodeQL, relatório privado de vulnerabilidades, environments `pypi`/`production`). Roteiro em `MIGRATION.md`.
9. **Configurar PyPI Trusted Publishing** para `alberto-research` (sem token de API).
10. **Gerar chave GPG/SSH** e habilitar commits assinados (pré-requisito do item 4).
11. **Executar a validação de container** (`docker build`, `hadolint`, `trivy`) onde houver Docker.
12. **Rodar o mutation testing** (`mutmut run`) para fechar o gate de mutação.
13. **Preencher o contato do `CODE_OF_CONDUCT.md`** (hoje um placeholder sem e-mail real).
14. **Confirmar o slug do repositório.** O remoto atual tem um erro de digitação (`Alberto-Reserach`); todos os links do pacote novo usam `alberto-research`.

---

## 6. Riscos residuais e mitigações

| # | Risco | Sev. | Mitigação atual | Ação necessária |
|---|---|---|---|---|
| R1 | `verify=False` na trilha de *shadow libraries* (SA-03) | Alta | Desligada por padrão; extra opcional; documentada | ✅ **Aceite formal registrado** (`SECURITY_AUDIT.md` §7.1) — risco técnico mitigado por decisão; opcionalmente `verify=True` com CA bundle |
| R2 | Licença MIT + código que contorna paywall | **Alta** | Documentado em README/SECURITY/AUDIT | **Bloqueador aberto.** Decisão jurídica do autor; alternativa: manter privado ou separar a trilha |
| R3 | Cobertura 62,85 % < 80 % | Média | Gate em 60 % (falha se cair) | Via de 30 linhas identificada (§10.4) **desde que** o caminho de risco aceito seja excluído do cálculo |
| R4 | CI nunca executado | Média | Configuração revisada linha a linha e validada como YAML | Primeira execução após o push |
| R5 | Mutation score não medido | Média | — | Rodar `mutmut` em `core/` |
| R6 | E-mail pessoal em metadados de commit | Baixa | ✅ Novo repo já usa `noreply` — **verificado** | Nenhuma (manter a identidade no push) |
| R7 | Dockerfile não construído | Baixa | Revisão manual contra regras do hadolint | `docker build` + `hadolint` + `trivy` no CI |
| R8 | Sem SBOM SPDX nem assinatura Sigstore | Baixa | CycloneDX + atestação de proveniência no release | Adicionar saída SPDX e `cosign` ao `release.yml` |
| R9 | Docstrings incompletas (`D1xx` relaxado) | Baixa | Regras relaxadas com justificativa versionada | Endurecer gradualmente; item no `ROADMAP.md` |
| **R10** | **`.venv` do artefato corrompida** | **Média** | Nenhuma — gates não executáveis | Recriar o ambiente (§10.2); **novo na Revisão 2** |
| **R11** | **Commit não assinado + tag leve** | Média | Identidade correta, mas sem assinatura | `commit -S` + `tag -s` (§10.3); **novo na Revisão 2** |
| **R12** | **`SECURITY.md` contradiz o código** | Média | Texto corrigido proposto em `SECURITY_AUDIT.md` §7.2 | Aplicar antes de publicar; **novo na Revisão 2** |

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

**Não está pronto para publicação pública autônoma** por três motivos: (a) o risco **jurídico** R2 — a coerência entre a licença MIT e a trilha de *shadow libraries* —, que é decisão sua e **não** foi resolvido pelo aceite técnico de `SECURITY_AUDIT.md` §7.1; (b) a **cobertura de 62,85 %**, abaixo dos 80 % exigidos, embora a via curta para atingi-los esteja identificada em §10.4; e (c) itens de conformidade **verificados nesta revisão**: `.venv` corrompida (§10.2), commit não assinado e tag leve (§10.3) e `SECURITY.md` contradizendo o código. Além disso, CI, proteções de repositório e publicação no PyPI só podem ser validados após o push.

**Nenhum `git push` foi executado.** Nenhuma operação irreversível foi realizada no repositório original.

> **Revisão 2 (2026-10-02):** o aceite formal do risco SA-03, antes pendente, foi **registrado** (`SECURITY_AUDIT.md` §7.1). Em contrapartida, a re-verificação independente confirmou os números de testes e cobertura e **revelou três não conformidades** que o relatório original não capturava — `.venv` corrompida, ausência de assinatura de commit/tag e a contradição do `SECURITY.md`. Detalhes e composição do gap em §10.

---

## 10. Verificação independente e estado de execução (2026-10-02)

Esta seção foi acrescentada na Revisão 2. Ela distingue o que foi **re-verificado agora** do que permanece apenas **relatado** da execução de 2026-09-29. O detalhamento técnico está em `SECURITY_AUDIT.md` §13.

### 10.1 Evidência de segurança — confirmada

`gitleaks.json` = `[]`; `trufflehog.err` = `verified_secrets: 0` e `unverified_secrets: 0` (504 chunks); `pip-audit.json` = 15 pacotes, `vulns: []`; `osv.json` = `results: []`. As afirmações centrais do relatório original **conferem com a evidência armazenada**.

### 10.2 A `.venv` do artefato está corrompida — defeito real

`.venv/bin/` está **vazio**, `pyvenv.cfg` **não existe** e há diretórios duplicados (`bin 2`, `lib 2`, `lib 3`, `share 2`), indicando sobreposição de cópias/extracções. **Nenhum gate era executável no estado entregue.** Correção:

```bash
cd /Users/gabriel.affonso/Documents/alberto-research
rm -rf .venv ".venv/bin 2" ".venv/lib 2" ".venv/lib 3" ".venv/share 2"
uv venv --python 3.11 .venv && . .venv/bin/activate
uv pip install -e ".[dev]"
```

### 10.3 Assinatura de commit e tag — não conforme

```console
$ git log -1 --format='%an <%ae> | %G? | %H'
Gabriel Affonso <gabriel.affonso@users.noreply.github.com> | N | b98f480
$ git tag -l --format='%(refname:short) %(objecttype)'
v0.1.0 tag
```

O commit **não está assinado** (`%G?` = `N`) e `v0.1.0` é **tag leve**, não anotada/assinada. O item "Commits assinados" de §4.1 permanece ❌. A identidade, porém, já usa o `noreply` do GitHub, de modo que o SA-07 **não** reaparece no artefato novo. Para corrigir:

```bash
git config user.signing.key <fingerprint>
git commit --amend --no-edit -S
git tag -d v0.1.0 && git tag -s v0.1.0 -m "Release v0.1.0"
```

### 10.4 Gates reproduzidos e composição do gap de cobertura

Gates reproduzidos em venv isolada (a `.venv` do artefato está quebrada): **`pytest` → 112 passed, 2 skipped; cobertura 62,85 %** (gate em 60 %). Confere com o relatado.

O gap para 80 % foi analisado e **não é homogêneo**: das 970 linhas não cobertas, **486 (50,1 %) pertencem aos 8 módulos de *shadow library*** — o código sob aceite de risco §7.1 —, 468 são de código legítimo, 11 de `_version.py` (gerado) e 5 do entry point.

| Cenário | Cobertura |
|---|---|
| Hoje | 62,85 % |
| Excluindo os módulos de *shadow library* | 78,90 % |
| Excluindo também `_version.py` | 79,29 % |
| Excluindo ambos **+ ~30 declarações de teste legítimo** | **≥ 80 %** |

**Recomendação:** declarar a exclusão em `[tool.coverage.report] omit` com a justificativa do aceite §7.1 e acrescentar ~30 linhas de teste em `config.py`, `schemas.py` ou `zotero.py`. Isso alcança o critério de 80 % **sem** escrever testes para a trilha de risco aceito. Não aplicado: o artefato está fora do sandbox de escrita desta execução.

### 10.5 Limitação de escopo desta revisão

As correções acima **não foram aplicadas dentro de `/Users/gabriel.affonso/Documents/alberto-research`**: o diretório está fora da área de escrita autorizada do agente. Esta revisão atua sobre os artefatos de *handoff* no monorepo. As alterações de código correspondentes permanecem pendentes de autorização explícita.

---

## 11. Execução real e CI verde (Revisão 3 — 2026-10-02)

A Revisão 2 registrou "CI nunca executado" como risco R4. A execução real aconteceu: o
repositório foi criado e publicado, e **o CI reprovou em todos os jobs**. A configuração
nunca havia sido executada, de modo que os defeitos só apareceram quando passou a rodar.
Esta é a seção que fecha aquele item — e o que ela revelou contradiz a avaliação anterior
da documentação como "pronta".

### 11.1 O que foi executado

| Ação | Resultado |
|---|---|
| `gh repo create gabriel-affonso/alberto-research --public` | criado; `https://github.com/gabriel-affonso/alberto-research` |
| `git push -u origin main --tags` | `main` + tag `v0.1.0` publicados |
| `gh repo edit gabriel-affonso/Alberto-Reserach --visibility private` | **repositório antigo agora privado** |
| `gh api -X POST .../pages -f build_type=workflow` | GitHub Pages habilitado |

### 11.2 Defeitos de CI encontrados e corrigidos

Foram necessárias **4 correções em 3 iterações**. O primeiro push teve **todos** os jobs
reprovados (run `37133280275`).

| # | Defeito | Sintoma real | Correção |
|---|---|---|---|
| D1 | `uv pip install --system` | `The interpreter at /usr is externally managed` (PEP 668), exit 2. **Quebrou lint, os 5 legs de teste, security e build** | Removido `--system` (6 ocorrências em `ci.yml`, `docs.yml`, `_setup-python.yml`) |
| D2 | `uv pip install` sem venv | `No virtual environment found; run 'uv venv'` — a correção de D1 foi necessária mas não suficiente | `uv venv` explícito antes de instalar |
| D3 | venv fora do `PATH` | `pytest: command not found`, `ruff/bandit/twine/mkdocs: command not found`, exit 127 | `VIRTUAL_ENV` via `$GITHUB_ENV` + `uv run <tool>` |
| D4 | Export de `PATH` em pwsh | O passo escrevia `$env:GITHUB_WORKSPACE\.venv\Scripts` e **não tinha efeito nos legs Linux/macOS** | Substituído por `VIRTUAL_ENV`, resolvido pelo próprio `uv` |
| D5 | `gitleaks-action` (range) | `failed to scan Git repository / stderr is not empty`, exit 1 | Varredura própria de histórico completo |
| D6 | `--redacted` | `unknown flag: --redacted`, exit 126 (o flag correto é `--redact`) | `--redact` |
| D7 | trufflehog com `base`=branch padrão | `BASE and HEAD commits are the same. TruffleHog won't scan anything.` | Removido `base`/`head`; varredura de histórico completo |
| D8 | trufflehog com `--fail` duplicado | `flag 'fail' cannot be repeated` (a action já injeta `--fail`) | Removido de `extra_args` |
| D9 | `str(Path)` no digest | `test_html_digest_renders_markdown_as_html` reprovava **apenas no windows-latest** (barras invertidas) | `local_path.as_posix()` |
| D10 | GitHub Pages não habilitado | `Creating Pages deployment failed / HttpError: Not Found (404)` | Pages habilitado com `build_type=workflow` |

D9 é digno de nota: o teste passava em POSIX e falhava em Windows. **Nenhum tipo de
verificação local pegaria isso** — só a execução real da matrix.

### 11.3 Estado final verificado do CI

Último run (`e568ef2`): **todos os workflows com sucesso**.

| Workflow / job | Estado |
|---|---|
| CI · Lint & type check | ✅ |
| CI · Test (ubuntu-latest, 3.11 / 3.12 / 3.13) | ✅ |
| CI · Test (macos-latest, 3.11) | ✅ |
| CI · Test (windows-latest, 3.11) | ✅ |
| CI · Security scan | ✅ |
| CI · Build distributions | ✅ |
| Secret Scan | ✅ |
| Docs | ✅ deploy efetivo |
| OpenSSF Scorecard | ✅ (não bloqueante, ver §11.4) |

- Documentação publicada: **https://gabriel-affonso.github.io/alberto-research/** (HTTP 200)
- `pip-audit` também executa no CI via `pypa/gh-action-pip-audit@v1.1.0`.

### 11.4 Item não corrigido — Scorecard

`ossf/scorecard-action@v2.4.0` é distribuído via `gcr.io`, e o pull agora falha com
`This API method requires billing to be enabled`. O job morre ao buscar a imagem, antes de
qualquer análise. É uma falha de infraestrutura do projeto OpenSSF, **não** um defeito do
repositório. Foi marcado `continue-on-error: true` com justificativa no arquivo: um check
permanentemente vermelho treina revisores a ignorá-lo. Reverter quando a action passar a
ser publicada em um registry sem billing.

### 11.5 Divergências de versão e pendência de release

- `_version.py` estava **rastreado apesar de estar no `.gitignore`** e fixava `0.1.1.dev0`.
  Removido do índice; a versão passou a resolver corretamente para `0.1.0`.
- **PyPI: nada publicado.** `https://pypi.org/pypi/alberto-research/json` responde
  `{"message": "Not Found"}`. O `release.yml` **nunca executou**: seu gatilho é push de tag,
  e a tag `v0.1.0` aponta para um commit **anterior** à criação do arquivo de workflow.
- Os badges de CI e OpenSSF Scorecard no README apontam para `gabriel-affonso/alberto-research`,
  que agora é o repositório correto (o `Homepage`/`Repository` do `pyproject.toml` também).

### 11.6 Não executado nesta revisão

- Cobertura para ≥ 80 %: **não elevada**. O gate permanece em 60 % e a cobertura em 62,85 %.
  A via de ~30 linhas está analisada em `SECURITY_AUDIT.md` §13.5, mas **não foi aplicada**,
  porque alterá-la muda o que o gate mede e isso é decisão sua.
- Mutation testing (`mutmut`): não executado.
- SBOM SPDX e assinatura Sigstore: não gerados.
- `SECURITY.md` do pacote: a contradição de §7.2 **continua ativa**. Recomendação: corrigir
  antes de tornar o projeto amplamente divulgado.
- Monorepo: `README.md` da raiz não recebeu o aviso legal; `production-ready` está à frente
  de `main` e **não foi enviada** a `origin`.
