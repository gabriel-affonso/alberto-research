# Reprodutibilidade

Uma execução de pesquisa só é comparável a outra se o ambiente for o mesmo. Esta
página descreve como fixar dependências com hashes, como regenerar os arquivos,
qual matriz a integração contínua cobre e como verificar uma versão publicada.

## Por que fixar dependências

O `pyproject.toml` declara intervalos (`>=`, `<`) porque é isso que uma biblioteca
deve fazer. Para **reproduzir uma execução**, intervalos não bastam: duas
instalações em datas diferentes podem resolver versões diferentes das mesmas
dependências. O que garante reprodutibilidade é um lockfile com versões exatas e
**hashes criptográficos**, que detectam tanto uma troca de versão quanto a
substituição maliciosa de um artefato.

O repositório mantém dois lockfiles na raiz:

| Arquivo | Conteúdo |
| --- | --- |
| `requirements.lock` | Dependências de runtime. |
| `requirements-dev.lock` | Runtime mais o extra `dev` (lint, tipagem, testes, auditoria). |

O extra `legacy-resolvers` **não** entra em nenhum dos dois: os resolvedores de
bibliotecas sombra são exclusão deliberada do caminho reproduzível e padrão.

## Regenerando os lockfiles

O script do repositório encapsula o comando e garante nomes e flags consistentes:

```bash
scripts/lock.sh
```

Ele requer `uv` no `PATH` e executa, a partir da raiz do repositório:

```bash
uv pip compile pyproject.toml --generate-hashes -o requirements.lock
uv pip compile pyproject.toml --extra dev --generate-hashes -o requirements-dev.lock
```

Se preferir rodar o comando bruto diretamente — por exemplo, para atualizar apenas
uma dependência —, use exatamente a forma acima com `--generate-hashes`. A saída é
determinística para um dado `pyproject.toml`, então repetir sem mudar dependências
produz arquivos idênticos byte a byte.

O resultado é um arquivo no formato:

```text
requests==2.32.3 \
    --hash=sha256:0000000000000000000000000000000000000000000000000000000000000000 \
    --hash=sha256:1111111111111111111111111111111111111111111111111111111111111111
```

Regenere os lockfiles **deliberadamente**, revisando o diff antes de confirmar:
uma nova resolução é uma mudança de ambiente e merece um commit próprio. Não
regenerar em cada build; caso contrário, o arquivo deixa de ser um registro do que
foi testado.

## Instalando a partir de um lockfile

Para exigir que os hashes batam:

```bash
pip install --require-hashes -r requirements.lock
```

Com `uv`:

```bash
uv pip install --system -r requirements.lock
```

Se qualquer artefato baixado não corresponder ao hash registrado, a instalação
falha — que é exatamente o comportamento desejado.

## Matriz de integração contínua

O fluxo de CI em `.github/workflows/ci.yml` cobre, a cada `push` e `pull
request`:

| Trabalho | O que faz |
| --- | --- |
| `lint` | Instala o projeto com o extra `test`, mais `ruff` e `mypy`, e roda verificação de estilo, formatação e tipagem. |
| `test` | Instala com o extra `test` e roda `pytest` com cobertura de ramos, medindo a cobertura de `alberto_research`. |

A matriz de testes é fixada em cinco combinações:

| Sistema | Python |
| --- | --- |
| `ubuntu-latest` | 3.11, 3.12, 3.13 |
| `macos-latest` | 3.11 |
| `windows-latest` | 3.11 |

A cobertura completa de interpretadores fica no Linux; macOS e Windows rodam a
versão mínima suportada, onde quebras específicas de plataforma aparecem
primeiro. Os testes rodam com `--cov-branch` e um piso mínimo de cobertura
(`--cov-fail-under`), de modo que uma queda relevante falha o build em vez de
passar silenciosamente.

Também é possível disparar a execução manualmente pelo `workflow_dispatch`.

## Gerando um SBOM

Um SBOM (*Software Bill of Materials*) lista tudo o que entra na instalação — útil
para auditoria e resposta a vulnerabilidades.

O próprio fluxo de release gera um, em formato CycloneDX JSON, a partir da árvore
do repositório, e o publica como artefato `sbom` junto das distribuições. Para
reproduzir localmente o mesmo inventário:

```bash
pip install cyclonedx-bom
cyclonedx-py environment --output-format json --outfile sbom/cyclonedx.json
```

Como alternativa, o `syft` produz o mesmo tipo de inventário:

```bash
syft dir:. -o cyclonedx-json=sbom/cyclonedx.json
```

Gere o SBOM do **ambiente resolvido** (com os lockfiles aplicados), não do
`pyproject.toml`, para que as versões exatas apareçam. Guarde o SBOM junto da
versão correspondente.

Complemente com uma auditoria de vulnerabilidades conhecidas:

```bash
pip-audit
```

## O que acontece quando uma tag é publicada

Ao empurrar uma tag no formato `v*.*.*`, o fluxo
`.github/workflows/release.yml` executa, em ordem:

1. **Build** — constrói o `sdist` e o *wheel* com `uv build` (a versão vem da tag,
   via `hatch-vcs`).
2. **SBOM** — gera `sbom/cyclonedx.json`.
3. **Publicação no PyPI** — usa *Trusted Publishing* por OIDC, sem token de API
   armazenado, protegido pelo ambiente `pypi` do repositório.
4. **Atestação de proveniência** — assina a proveniência das distribuições, o que
   permite verificar que elas saíram deste repositório e deste fluxo.
5. **Release no GitHub** — criado apenas depois da publicação no PyPI, com notas
   geradas e verificação da tag.

A documentação tem um fluxo próprio: `.github/workflows/docs.yml` instala o extra
`docs`, roda `mkdocs build --strict` — que transforma link quebrado ou entrada de
navegação ausente em erro de build — e publica em GitHub Pages.

## Verificando uma versão publicada

Para conferir que um release é o que diz ser:

1. **Instale em ambiente limpo, com hashes.**

   ```bash
   python -m venv /tmp/verify
   /tmp/verify/bin/pip install --require-hashes -r requirements.lock
   /tmp/verify/bin/pip install alberto-research
   ```

2. **Confirme a versão instalada.**

   ```bash
   /tmp/verify/bin/alberto-research --version
   ```

   O número deve ser exatamente o do release anunciado. O pacote deriva a versão
   das tags do Git; ao verificar a partir do código-fonte, use um clone completo,
   porque um clone superficial produz uma versão errada ou de fallback.

3. **Confirme que o pacote importa e o banco migra.**

   ```bash
   /tmp/verify/bin/python -c "import alberto_research"
   /tmp/verify/bin/alberto-research db migrate --db /tmp/verify/verify.sqlite3
   ```

4. **Verifique a proveniência da distribuição.** O fluxo de release atesta os
   artefatos, então o comando abaixo confirma a origem:

   ```bash
   gh attestation verify dist/alberto_research-<versao>-py3-none-any.whl \
     --repo gabriel-affonso/alberto-research
   ```

5. **Confira o conteúdo do artefato.** O *wheel* contém o pacote
   `alberto_research` e as migrações SQL empacotadas; o `sdist` inclui também
   `tests`, `docs`, `examples`, `README.md`, `LICENSE` e `CHANGELOG.md`.

6. **Rode a auditoria e compare com o SBOM do release.**

   ```bash
   pip install pip-audit
   pip-audit
   ```

   Compare o resultado com `sbom/cyclonedx.json` do release e com o
   `requirements.lock` correspondente à tag.

## Boas práticas para execuções comparáveis

- Registre a versão de `alberto-research`, o lockfile e o SBOM usados em cada
  rodada.
- Guarde o YAML do projeto junto do resultado; a configuração faz parte do
  experimento.
- Use o mesmo `timezone` e a mesma janela de `date_ranges` ao comparar dois
  digests.
- Lembre-se de que as etapas de LLM não são determinísticas por natureza: um
  mesmo insumo pode produzir saídas diferentes. A validação por JSON Schema
  garante a forma, não a repetição literal. Ao reportar resultados, trate a
  triagem e a leitura como julgamento assistido, não como medição.
