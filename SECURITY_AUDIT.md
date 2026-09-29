# SECURITY_AUDIT.md — Alberto Research

**Repositório auditado:** `https://github.com/gabriel-affonso/Alberto-Reserach.git` (monorepo `Alberto`, Git root `/Users/gabriel.affonso/Documents/Alberto`)
**Data da auditoria:** 2026-09-29
**Commit base:** `13d47ca` (`main`) — 37 commits, 108 arquivos rastreados, 12.149 LOC
**Artefato de destino:** novo repositório limpo `alberto-research` (extração de `src/alberto/research` + `src/alberto/db` + `src/alberto/enums.py`)

> Este relatório **não contém nenhum valor de segredo**. Onde aplicável são registrados apenas o hash do blob, o caminho e a localização, com o valor substituído por `<REDACTED>`.

---

## 1. Sumário executivo

O histórico completo do repositório **não contém credenciais vivas nem segredos verificáveis**. As quatro ferramentas de varredura independentes concordam:

| Verificação | Resultado |
|---|---|
| `gitleaks` 8.30.1 — histórico completo | **0 vazamentos** (39 commits, 514,96 KB) |
| `trufflehog` 3.97.9 — `--only-verified` | **0 verificados, 0 não verificados** (504 chunks, 522.629 bytes) |
| Varredura regex própria — 271 blobs de todas as revisões | **0 hits de segredo** |
| `detect-secrets` 1.5.0 — arquivos rastreados | 1 achado → **falso positivo** |
| `pip-audit` 2.10.1 — 15 pacotes | **0 vulnerabilidades** |
| `osv-scanner` 2.6.0 — 15 pacotes | **nenhum problema** |

Os riscos residuais relevantes **não são segredos**, e sim:

1. **Risco aceito pelo autor (Alta):** três chamadas `requests.get(..., verify=False)` na trilha opcional de *shadow libraries*, que desabilitam a validação TLS e permitem ataque *man-in-the-middle*. **Requer sign-off formal** — ver §7.
2. **Contradição documental (resolvida no repo novo):** o `SECURITY.md` do monorepo afirmava *"Alberto never bypasses publisher access controls or paywalls"* enquanto três dos quatro `projects/*.yaml` tinham `enable_scihub: true` e registravam os resolvedores `scihub_mcp → scihub → libgen → scihub_http`. Afirmação e código divergiam.
3. **PII em metadados de commit (Baixa):** o e-mail pessoal real aparece em 41 entradas de autoria. Não é conteúdo de arquivo, portanto não é detectado por `gitleaks`/`trufflehog`.

---

## 2. Escopo e método

- **Alvo primário:** histórico Git completo (todas as revisões e objetos), não apenas o `HEAD`.
- **Alvo secundário:** o pacote extraído `src/alberto_research` no novo repositório.
- **Método:** cada blob de cada revisão foi materializado (`git rev-list --objects --all` + `git cat-file`) e submetido a 13 padrões de segredo e 5 padrões de PII, em paralelo às ferramentas dedicadas.
- **Ferramentas executadas:** `gitleaks`, `trufflehog`, `detect-secrets`, `bandit`, `pip-audit`, `osv-scanner`, `ruff` (`S` — flake8-bandit), além de varredura regex própria.

### Ferramentas isoladas (nunca instaladas globalmente)

Todas foram provisionadas em `.tooling/` dentro do workspace, via `uv venv` e binários estáveis baixados para `.tooling/bin`, conforme a restrição de "nenhum pacote global no sistema".

| Ferramenta | Versão | Origem |
|---|---|---|
| gitleaks | 8.30.1 | release binária `darwin_arm64` |
| trufflehog | 3.97.9 | release binária `darwin_arm64` |
| osv-scanner | 2.6.0 | release binária `darwin_arm64` |
| detect-secrets | 1.5.0 | `uv pip` (venv isolada) |
| bandit | 1.9.4 | `uv pip` |
| pip-audit | 2.10.1 | `uv pip` |
| ruff / mypy / pytest | 0.16.9 / 2.3.1 / 9.1.1 | `uv pip` |

**Ferramentas indisponíveis (registradas):** `git-secrets`, `safety`, `Docker`, `hadolint`, `trivy`, `syft`, `cosign`. Justificativa e impacto em §10.

---

## 3. Tabela de achados

| ID | Ferramenta | Tipo | Arquivo | Linha | Commit | Blob SHA | Severidade | Ação |
|---|---|---|---|---|---|---|---|---|
| SA-01 | varredura própria (histórico) | PII — caminho absoluto de host | `src/alberto/research/workflow.py` | 500, 553 | `0c3af85` (2026-08-19) | `583048e35852156e1acac7e19e6fd6009ee567f9` | Baixa | **Corrigido** no repo novo |
| SA-02 | detect-secrets | Secret Keyword | `tests/test_fulltext.py` | 255 | — | — | Info | **Falso positivo** (§6.1) |
| SA-03 | bandit | B501 — `verify=False` (TLS) | `src/alberto_research/scihub_integration.py` | 42, 76, 96 | herdado | — | **Alta** (CVSS 3.1: 7.4) | **Risco aceito — requer sign-off** (§7) |
| SA-04 | bandit | B113 — requisição sem timeout | `src/alberto_research/fulltext.py` | 226, 265, 309, 359, 404, 742 | herdado | — | Média | **Falso positivo** (§6.2) |
| SA-05 | bandit | B608 — SQL por concatenação | `src/alberto_research/db/repositories.py` | 447, 477, 514, 587 | herdado | — | Média | **Falso positivo** (§6.3) |
| SA-06 | bandit | B404 / B603 — `subprocess` | `src/alberto_research/openclaw.py` | 6, 67 | herdado | — | Baixa | Mitigado e documentado (§6.4) |
| SA-07 | git metadata | PII — e-mail pessoal | 41 entradas de autoria | — | todo o histórico | — | Baixa | **Ação do autor** (§5) |
| SA-08 | auditoria de imports | Dependências não declaradas | `pyproject.toml` | — | `13d47ca` | — | Média | **Corrigido** no repo novo (§4) |
| SA-09 | revisão de código | Documentação de segurança divergente do código | `SECURITY.md` | 30 | `13d47ca` | — | Média | **Corrigido** no repo novo (§4) |
| SA-10 | revisão de código | Credenciais *placeholder* em código | `scihub_bot.py` | 12-13 | herdado | — | Info | Placeholder (`TG_API_ID='123456'`) — sem rotação necessária |

### Detalhe dos achados corrigidos

**SA-01 — Caminho absoluto de host.**
`workflow.py` invocava o binário do OpenClaw por caminho fixo `/home/alberto/.openclaw/bin/openclaw`. Além de quebrar portabilidade, um caminho fixo em diretório gravável por outro usuário é um vetor de *path hijacking*. **Resolvido** no repositório novo: substituído por `resolve_openclaw_binary()` / `openclaw_agent_command()` em `alberto_research/openclaw.py`, com precedência `openclaw.binary` (config do projeto) → `ALBERTO_OPENCLAW_BIN` → `PATH`. Verificado: `grep -rn '/home/alberto' src/` no repo novo não retorna nada.

**SA-08 — Dependências não declaradas.**
O `pyproject.toml` do monorepo declarava `retrying` e `pysocks` (nunca importados) e **omitia** quatro bibliotecas efetivamente importadas: `PyPDF2` (3 arquivos), `curl_cffi` (3), `telethon` (1), `python-dotenv` (1). Uma instalação limpa quebraria em runtime. **Resolvido** no repo novo: dependências reais declaradas em `dependencies`, e as quatro bibliotecas exclusivas da trilha de *shadow libraries* isoladas no extra opcional `legacy-resolvers`.

**SA-09 — Documentação divergente.**
O `SECURITY.md` original afirmava que o projeto nunca contorna paywalls, contradizendo o código. **Resolvido**: o novo `SECURITY.md` documenta explicitamente a existência, o desligamento por padrão, o requisito do extra `legacy-resolvers`, o `verify=False` e a responsabilidade legal exclusiva do operador.

---

## 4. Auditoria de dependências

Executada sobre `requirements.lock` (com hashes) do repositório novo, que é um superconjunto das dependências do monorepo.

```
pip-audit 2.10.1   → 15 pacotes auditados, 0 vulnerabilidades
osv-scanner 2.6.0  → 15 pacotes lidos ("found 15 packages"), No issues found
```

Nenhuma vulnerabilidade *high*/*critical* — o quality gate de dependências está satisfeito.

**Reprodutibilidade:** `requirements.lock` (427 linhas, 385 pinos com hash) e `requirements-dev.lock` (1567 linhas, 1354 pinos com hash), regeneráveis por `scripts/lock.sh`.

---

## 5. AÇÃO IMEDIATA — rotação de credenciais

**Nenhuma credencial precisa ser rotacionada.** Não há chave de API, token, senha ou chave privada em nenhuma revisão do histórico; as quatro ferramentas concordam e a varredura manual de 271 blobs confirma.

Itens que **dependem de ação humana**:

1. **E-mail pessoal em metadados de commit (SA-07).** O histórico usa `<e-mail-pessoal-REDACTED>` em 41 entradas de autoria. O novo repositório nasce com histórico limpo, mas **se o autor commitar com a mesma identidade, o endereço torna-se público de forma permanente**. Recomendação: configurar
   `git config user.email "gabriel.affonso@users.noreply.github.com"` **antes** do commit inicial, e habilitar *email privacy* no GitHub.
2. **Sign-off do risco SA-03.** Ver §7. Enquanto não houver aceite formal registrado, o repositório **não deve ser tornado público**.
3. **`scihub_session.session`.** O `.gitignore` já exclui o arquivo de sessão do Telethon. Confirmar que nenhuma sessão local foi commitada — verificado: nunca rastreado.

---

## 6. Falsos positivos

Nenhum destes exige mudança de código. As supressões correspondentes estão declaradas e justificadas em `pyproject.toml` (`[tool.bandit] skips`), `.pre-commit-config.yaml` e `.github/workflows/ci.yml`.

### 6.1 SA-02 — `detect-secrets`: "Secret Keyword" em `tests/test_fulltext.py:255`

O identificador do achado (`hashed_secret`) é mantido em `_audit/detect-secrets.json`.

O valor sinalizado é a string literal `"secret-key"`, usada como chave de API fictícia num teste que verifica se o cabeçalho `Authorization: Bearer <chave>` é montado corretamente pelo resolvedor CORE. Não é uma credencial: é um valor de teste, sem capacidade de autenticação, e o teste usa `example.test` como domínio. **Ação: nenhuma.**

### 6.2 SA-04 — `bandit` B113: "Call to requests without timeout" (6 ocorrências)

**As seis chamadas passam `timeout=`.** Verificado por inspeção das linhas 226, 265, 309, 359, 404 e 742 de `fulltext.py`: todas incluem `timeout=request_timeout(config)`.

Causa raiz do falso positivo: o plugin B113 usa `context.check_call_arg_value("timeout")`, que internamente chama `get_call_arg_value()`. Essa função devolve o valor **apenas para literais**; ao receber uma chamada de função (`request_timeout(config)`) devolve `None`, e o plugin interpreta `None` como "argumento ausente". O código é seguro; a ferramenta não consegue resolvê-lo estaticamente. **Ação: nenhuma.**

### 6.3 SA-05 — `bandit` B608: "Possible SQL injection" (4 ocorrências)

O padrão sinalizado é:

```python
project_filter = "" if project_id is None else "AND d.project_id=?"
params = () if project_id is None else (project_id,)
self.conn.execute(f"""... WHERE di.item_type = 'reading' {project_filter} ...""", params)
```

A única interpolação é a **constante literal** `project_filter`, escolhida entre duas strings fixas definidas no próprio código. O valor controlado pelo usuário (`project_id`) é sempre passado como *bound parameter* (`?` + tupla `params`). Não há entrada do usuário na string SQL. **Ação: nenhuma.**

### 6.4 SA-06 — `bandit` B404 / B603: `subprocess` em `openclaw.py`

O binário e os argumentos são construídos por `openclaw_agent_command()`, a partir de (a) `openclaw.binary` no YAML do projeto, (b) `ALBERTO_OPENCLAW_BIN` ou (c) busca no `PATH`. **Nunca** derivam de texto de artigo, resumo ou saída de LLM. A lista de argumentos é passada sem `shell=True`, portanto não há interpolação de shell. Documentado no código com justificativa e `# noqa: S603`. **Ação: nenhuma** (severidade Baixa, abaixo do limiar do gate `-ll`).

---

## 7. Riscos aceitos pelo autor (requer sign-off)

### SA-03 — Validação TLS desabilitada na trilha de *shadow libraries* — severidade Alta

**Localização:** `src/alberto_research/scihub_integration.py`, linhas 42, 76 e 96.
**Também presente em:** `providers/scihub_http.py`, `providers/tesble.py` e `libgen_integration.py` (que usam `curl_cffi` com impersonação de TLS de navegador e `User-Agent` falsificado).

```python
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
resp = requests.get(search_url, headers=headers, timeout=10, verify=False)  # <REDACTED: verify=False>
```

**Impacto:** desabilitar a verificação de certificado elimina a autenticidade do canal. Um atacante em posição de rede (DNS/ARP/BGP ou Wi-Fi hostil) pode interceptar e **alterar** o tráfego, inclusive o conteúdo do PDF que será processado pelo pipeline e enviado ao LLM. Como o projeto trata documentos externos como hostis, esse é exatamente o canal de entrada que a arquitetura tenta proteger — o bypass de TLS reabre a porta.
**CVSS 3.1:** `AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N` = **7.4 (Alta)**. Avaliação do autor do relatório; não é um vetor oficial NVD.

**Decisão registrada do autor (2026-09-29):** *"Manter como está e apenas documentar o risco"* — nenhuma alteração de código nesta trilha.

**Consequências que exigem decisão informada:**

1. O risco é **incompatível com a licença MIT em repositório público**, conforme decidido separadamente. Distribuir publicamente código cuja função é contornar controles de acesso a paywall, sob licença permissiva, expõe o autor a risco jurídico (direito autoral / DMCA) que a MIT não mitiga.
2. A trilha permanece **desligada por padrão** (`enable_scihub: false` nos três exemplos que acompanham o pacote) e exige o extra `legacy-resolvers` mais `enable_scihub: true` explícito. Isso limita — mas não elimina — a exposição.
3. **Enquanto este aceite não for registrado por escrito pelo autor, o repositório não deve ser publicado.** Item correspondente marcado como pendente em `PRODUCTION_READINESS.md` (§11.3).

**Mitigação recomendada (não aplicada, por decisão do autor):** trocar `verify=False` por `verify=True` com um `ca_bundle` configurável, ou isolar a trilha num pacote/plugin separado e não distribuído.

---

## 8. Cobertura de PII

| Padrão | Ocorrências no histórico | Avaliação |
|---|---|---|
| E-mail pessoal em conteúdo de arquivo | **0** | apenas `research@example.com` / `@example.test` em exemplos e testes |
| Caminho absoluto de host | 1 (`/home/alberto/…`, SA-01) | corrigido no repo novo |
| CPF / CNPJ | **0** | — |
| Telefone brasileiro | **0** | — |
| E-mail pessoal em metadados de commit | 41 entradas (SA-07) | ação do autor (§5) |
| Nome/identidade de usuário real em conteúdo | **0** | `openclaw/agents/*/USER.md` vazios |

O monorepo contém material pessoal que **não** deve integrar o artefato público e foi deliberadamente excluído da extração: o agente `alberto-travel` (incluindo `bin/fill-mbway-phone`, automação de pagamento MB Way) e `revisao_da_literatura.md` / `revisao_da_literatura_limpa.md` (88 KB de trabalho acadêmico pessoal). Confirmado ausente do repositório novo.

---

## 9. Modelo de ameaça do pacote extraído

| Vetor | Controle implementado |
|---|---|
| Prompt injection via artigo/resumo | Documentos tratados como dados; diretivas de ferramenta não são executadas |
| Saída de LLM malformada | `schemas.py` valida contra JSON Schema **antes** da persistência |
| Injeção SQL | *Bound parameters* em todas as consultas (ver §6.3) |
| Segredos em repositório | `gitleaks` + `trufflehog` em push, PR e diariamente; hook `gitleaks protect --staged` |
| Dependência comprometida | `pip-audit` + OSV + Dependabot + Dependency Review (`fail-on-severity: high`) |
| Cadeia de suprimentos do release | SBOM CycloneDX, atestação de proveniência (SLSA) e Trusted Publishing OIDC sem token |
| Execução de binário externo | Caminho resolvido por config/env/PATH, sem `shell=True`; nunca a partir de conteúdo não confiável |
| Acesso a caminhos arbitrários | Sem caminhos absolutos de host; `ALBERTO_HOME`/`XDG_STATE_HOME` configuráveis |

---

## 10. Limitações da auditoria

| Ferramenta | Situação | Impacto / mitigação |
|---|---|---|
| `git-secrets` | indisponível | Coberto por `gitleaks` + `trufflehog` + regex própria; sobreposição funcional alta |
| `safety` | indisponível (exige conta/API) | `pip-audit` + `osv-scanner` cobrem a mesma base (0 achados) |
| `Docker`, `hadolint`, `trivy` | sem Docker no host; binário hadolint ausente para macOS | `Dockerfile` revisado manualmente contra as regras do hadolint; **executar hadolint/trivy no CI** é item pendente |
| `syft`, `cosign` | indisponíveis | SBOM gerado com `cyclonedx-py` (CycloneDX 1.6, 30 componentes); SBOM SPDX e assinatura Sigstore ficam no workflow de release |
| `mutmut` | falhou ao inicializar | Mutation testing **não executado**; ver `PRODUCTION_READINESS.md` §11.2 |

Nenhuma dessas ausências altera a conclusão principal: **não há segredos no histórico**.

---

## 11. Comandos de verificação reproduzíveis

```bash
# Histórico completo — esperado: "no leaks found" / 0 findings
gitleaks detect --source . --log-opts="--all" --redact --verbose
trufflehog git file://. --only-verified
trufflehog git file://. --json | grep -c DetectorName   # esperado: 0

# Arquivos rastreados
git ls-files -z | xargs -0 detect-secrets scan

# PII
grep -rInE --exclude-dir=.git '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' .
grep -rInE --exclude-dir=.git '(/home/[a-z0-9_-]+/|/Users/[A-Za-z0-9_.-]+/)' .

# Código e dependências (no repositório novo)
bandit -c pyproject.toml -r src -ll
pip-audit -r requirements.lock
osv-scanner scan source --lockfile=requirements.lock

# Gates de qualidade
ruff check . && ruff format --check .
mypy
pytest
```

---

## 12. Conclusão

O histórico do repositório está **limpo de segredos** — resultado corroborado por quatro métodos independentes. Os achados remanescentes são: um falso positivo de ferramenta (SA-02), dois padrões de falso positivo com causa raiz identificada (SA-04, SA-05), um uso legítimo de `subprocess` (SA-06) e um risco **Alta** explicitamente aceito pelo autor (SA-03), cuja publicação exige decisão informada e sign-off registrado.

Os achados que dependiam de correção (SA-01, SA-08, SA-09) foram **corrigidos no repositório novo e verificados**.
