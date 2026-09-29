# Referência da API

Esta referência é **gerada automaticamente** a partir das docstrings do código por
meio do [mkdocstrings](https://mkdocstrings.github.io/). O estilo de docstring
configurado é o Google, e o código-fonte de cada membro é exibido junto da
assinatura.

Os blocos abaixo correspondem aos módulos públicos do pacote `alberto_research`.
Para o uso pela linha de comando, veja [Uso](usage.md); para a visão geral dos
módulos, veja [Arquitetura](architecture.md).

## Configuração

Carregamento, validação e campos obrigatórios do YAML de projeto.

::: alberto_research.config
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## Fluxo de trabalho

Orquestração do fluxo completo: descoberta, deduplicação, filtros, resolução de
texto completo, triagem, leitura e busca de citações.

::: alberto_research.workflow
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## Texto completo

Cadeia de resolvedores, cache de PDFs e limites de download.

::: alberto_research.fulltext
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## Esquemas

Contratos JSON Schema usados para validar a saída do LLM antes de ela ser
persistida.

::: alberto_research.schemas
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## Leitura

Construção de prompts, normalização da resposta do modelo e template de saída
estruturada.

::: alberto_research.reader
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## Provedores

Clientes dos provedores de descoberta e dos resolvedores externos.

::: alberto_research.providers
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## Banco de dados

Conexão SQLite, migrações e repositórios de acesso a dados.

::: alberto_research.db
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## Linha de comando

Definição dos subcomandos e ponto de entrada do script `alberto-research`.

::: alberto_research.cli
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## Digest

Montagem do corpo do digest e gravação do Markdown local.

::: alberto_research.digest
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## Entrega

Envio do digest pelos canais configurados, incluindo SMTP.

::: alberto_research.delivery
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## Zotero

Integração opcional com a API do Zotero.

::: alberto_research.zotero
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## Notion

Integração opcional com a API do Notion, criação do banco e backfill.

::: alberto_research.notion
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## OpenClaw

Resolução do binário, montagem da linha de comando e leitura da resposta JSON.

::: alberto_research.openclaw
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## Feedback

Registro do retorno do leitor sobre os itens do digest.

::: alberto_research.feedback
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false

## Deduplicação

Normalização de identificadores e deduplicação de registros.

::: alberto_research.dedupe
    options:
      members_order: source
      show_root_heading: true
      show_root_full_path: false
