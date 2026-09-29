# Configuração

Cada projeto de pesquisa é descrito por um único arquivo YAML. O comando
`alberto-research config validate PROJECT` carrega o arquivo, confere os campos
obrigatórios e verifica os tipos e intervalos antes de qualquer chamada de rede.

O carregamento aceita `PyYAML` quando instalado e, como alternativa, um
analisador YAML mínimo embutido — então o formato suportado é o subconjunto
usual de mappings, listas e escalares.

## Chaves de primeiro nível

| Chave | Tipo | Obrigatória | Padrão | Descrição |
| --- | --- | --- | --- | --- |
| `id` | string | Sim | — | Identificador único e não vazio do projeto. Usado como prefixo dos arquivos de digest e para separar projetos no banco. |
| `name` | string | Sim | — | Nome legível, exibido no cabeçalho do digest. |
| `research_question` | string | Sim | — | Pergunta de pesquisa não vazia. É o critério central da triagem e da leitura. |
| `priority_topics` | lista de strings | Sim | — | Tópicos que orientam a descoberta e aumentam a relevância atribuída pelo LLM. |
| `languages` | lista de strings | Sim | — | Idiomas aceitos (por exemplo `en`, `pt`). |
| `discovery_limits` | mapping | Sim | — | Limite de resultados por provedor. Veja a tabela abaixo. |
| `screening_threshold` | número entre 0 e 1 | Sim | — | Pontuação mínima para um candidato sobreviver à triagem. Abaixo disso, é descartado. |
| `deep_reading_threshold` | número entre 0 e 1 | Sim | — | Pontuação mínima para um candidato virar leitura profunda. Deve ser maior ou igual ao de triagem para ser útil. |
| `maximum_daily_deep_reads` | inteiro >= 0 | Sim | — | Teto de leituras profundas por execução diária. Use `0` para desligar a leitura. |
| `citation_chasing` | mapping | Sim | — | Configuração da busca de citações. Veja a tabela abaixo. |
| `digest` | mapping | Sim | — | Configuração do resumo diário. Veja a tabela abaixo. |
| `timezone` | string | Sim | — | Fuso IANA usado para o horário de entrega e para o recorte diário (por exemplo `Europe/Lisbon`). |
| `priority_authors` | lista de strings | Não | *(vazio)* | Autores de interesse especial. |
| `date_ranges` | mapping | Não | *(sem recorte)* | Janela temporal da descoberta, com as chaves `start` e `end`. |
| `inclusion_terms` | lista de strings | Não | *(vazio)* | Termos que favorecem a inclusão de um registro. |
| `exclusion_terms` | lista de strings | Não | *(vazio)* | Termos que descartam um registro. |
| `research_filters` | mapping | Não | *(sem filtros)* | Filtros adicionais. Veja a tabela abaixo. |
| `fulltext` | mapping | Não | *(somente acesso aberto)* | Cadeia de resolvedores e cache. Veja a tabela abaixo. |
| `notion` | mapping | Não | `enabled: false` | Arquivamento opcional no Notion. |
| `openclaw` | mapping | Não | *(resolução automática)* | Caminho do binário OpenClaw. Veja a tabela abaixo. |

## `discovery_limits`

| Chave | Tipo | Obrigatória | Padrão | Descrição |
| --- | --- | --- | --- | --- |
| `crossref` | inteiro | Não | *(definido no projeto)* | Número máximo de resultados retornados pelo Crossref. |
| `semantic_scholar` | inteiro | Não | *(definido no projeto)* | Número máximo de resultados retornados pelo Semantic Scholar. |

Os limites são por provedor; a quantidade efetiva de candidatos após a
descoberta é a soma dos provedores habilitados, menos duplicatas.

## `citation_chasing`

| Chave | Tipo | Obrigatória | Padrão | Descrição |
| --- | --- | --- | --- | --- |
| `enabled` | booleano | Sim, dentro do bloco | `false` | Liga ou desliga a busca de citações. |
| `max_depth` | inteiro | Sim, dentro do bloco | `0` | Profundidade máxima de encadeamento de referências. `0` desliga na prática. |
| `max_references_per_paper` | inteiro | Sim, dentro do bloco | `0` | Quantas referências seguir por artigo lido. |

## `digest`

| Chave | Tipo | Obrigatória | Padrão | Descrição |
| --- | --- | --- | --- | --- |
| `enabled` | booleano | Sim, dentro do bloco | `false` | Liga ou desliga a geração do digest. |
| `delivery_time` | string `"HH:MM"` | Sim, dentro do bloco | — | Horário local de entrega, interpretado no `timezone` do projeto. |
| `max_items` | inteiro | Sim, dentro do bloco | — | Número máximo de itens no digest. |
| `save_local` | booleano | Sim, dentro do bloco | `false` | Grava o digest em Markdown no disco, além de entregar. |

## `research_filters`

| Chave | Tipo | Obrigatória | Padrão | Descrição |
| --- | --- | --- | --- | --- |
| `article_only` | booleano | Não | `false` | Mantém apenas registros classificados como artigo. |
| `skip_previously_read` | booleano | Não | `false` | Ignora registros que já foram processados em execuções anteriores. |
| `excluded_doi_prefixes` | lista de strings | Não | *(vazio)* | Prefixos de DOI descartados, por exemplo `"10.1007/"`. |

## `fulltext`

| Chave | Tipo | Obrigatória | Padrão | Descrição |
| --- | --- | --- | --- | --- |
| `enable_scihub` | booleano | Não | `false` | Liga o resolvedor Sci-Hub. **Requer o extra `legacy-resolvers`, desativa a verificação de certificado TLS e é de responsabilidade legal do operador.** |
| `enable_annas_archive` | booleano | Não | `false` | Liga o resolvedor Anna's Archive. Mesmas condições e ressalvas de `enable_scihub`. |
| `unpaywall_email` | string | Não | *(vazio)* | Endereço de contato enviado ao Unpaywall e usado no *polite pool* dos provedores. Use um endereço de função, como `research@example.com`. |
| `core_api_key` | string | Não | *(vazio)* | Chave da API do CORE. Sem ela, o resolvedor CORE não é usado. |
| `resolver_order` | lista de strings | Não | *(ordem interna do pacote)* | Ordem de tentativa dos resolvedores. Valores aceitos: `zotero`, `unpaywall`, `openalex`, `core`, `doaj`, `europepmc`, `provider_url`. |
| `download_timeout` | inteiro (segundos) | Não | `30` | Tempo máximo por download de PDF. |
| `cache_dir` | string | Não | `.cache/fulltext` | Diretório de cache dos PDFs baixados. |
| `max_fulltext_bytes` | inteiro (bytes) | Não | `52428800` (50 MiB), ou `ALBERTO_MAX_FULLTEXT_BYTES` | Tamanho máximo aceito por arquivo de texto completo. |

Resolvedores listados em `resolver_order` que não estiverem disponíveis são
ignorados; os demais são tentados na ordem declarada e, em seguida, na ordem
interna do pacote.

## `notion` e `openclaw`

| Chave | Tipo | Obrigatória | Padrão | Descrição |
| --- | --- | --- | --- | --- |
| `notion.enabled` | booleano | Não | `false` | Liga o envio para o Notion. Também pode ser ativado com `ALBERTO_NOTION_ENABLED=1`. |
| `openclaw.binary` | string | Não | *(vazio)* | Caminho absoluto do binário OpenClaw. Se vazio, usa `ALBERTO_OPENCLAW_BIN` e, por fim, `openclaw` no `PATH`. |

## Exemplo completo e comentado

O arquivo abaixo é uma versão anotada de `examples/basic.yaml` — o mesmo que a
documentação de [Uso](usage.md) executa.

```yaml
# Identificação do projeto. `id` deve ser único no banco.
id: alberto-research-example
name: Alberto Research Example

# A pergunta que orienta triagem, leitura e síntese.
research_question: How do modular AI agent systems safely delegate untrusted research reading?

# Tópicos e autores que aumentam a prioridade de um candidato.
priority_topics:
  - AI agent orchestration
  - sandboxed document reading
  - prompt injection defenses
priority_authors:
  - Simon Willison

# Idiomas aceitos na descoberta.
languages:
  - en

# Recorte temporal aplicado aos provedores.
date_ranges:
  start: 2020-01-01
  end: 2026-12-31

# Termos que orientam a inclusão e a exclusão de registros.
inclusion_terms:
  - agent
  - sandbox
  - prompt injection
exclusion_terms:
  - finance

# Filtros adicionais de limpeza.
research_filters:
  article_only: true
  skip_previously_read: true
  excluded_doi_prefixes:
    - "10.4324/"
    - "10.1163/"
    - "10.5040/"
    - "10.1007/"

# Limite de resultados por provedor de descoberta.
discovery_limits:
  crossref: 5
  semantic_scholar: 5

# Limiares entre 0 e 1 e teto diário de leituras profundas.
screening_threshold: 0.55
deep_reading_threshold: 0.8
maximum_daily_deep_reads: 3

# Resolução de texto completo. O caminho padrão é acesso aberto legal.
fulltext:
  # Resolvedores de bibliotecas sombra: DESLIGADOS por padrão.
  # Ativá-los exige o extra `legacy-resolvers` e é sua responsabilidade legal.
  enable_scihub: false
  enable_annas_archive: false
  # Contato para o "polite pool" do CrossRef e do Unpaywall.
  # Use um endereço de função, nunca um e-mail pessoal.
  unpaywall_email: "research@example.com"
  core_api_key: ""
  resolver_order:
    - zotero
    - unpaywall
    - openalex
    - core
    - doaj
    - europepmc
    - provider_url
  download_timeout: 30
  cache_dir: ".cache/fulltext"

# Encadeamento de referências dos artigos lidos.
citation_chasing:
  enabled: true
  max_depth: 1
  max_references_per_paper: 5

# Resumo diário gerado e salvo localmente.
digest:
  enabled: true
  delivery_time: "08:00"
  max_items: 10
  save_local: true

# Ative depois de configurar NOTION_API_KEY e NOTION_DATA_SOURCE_ID.
notion:
  enabled: false

# Fuso usado no horário de entrega.
timezone: Europe/Lisbon
```

## Variáveis de ambiente

As variáveis abaixo complementam o YAML. Segredos devem vir do ambiente, nunca do
arquivo de projeto versionado.

| Variável | Para que serve |
| --- | --- |
| `ALBERTO_DB` | Caminho do banco SQLite. Tem precedência sobre o caminho padrão. |
| `ALBERTO_EMAIL_PROVIDER` | Seleciona o provedor de e-mail. Com o valor `smtp`, a entrega usa as variáveis `SMTP_*`. |
| `ALBERTO_HOME` | Diretório base dos dados operacionais. O banco padrão é `$ALBERTO_HOME/alberto.sqlite3`. |
| `ALBERTO_MAX_FULLTEXT_BYTES` | Limite global de bytes por texto completo, usado quando o projeto não define `max_fulltext_bytes`. |
| `ALBERTO_NOTION_ENABLED` | Com o valor `1`, liga o Notion mesmo que o projeto não declare `notion.enabled: true`. |
| `ALBERTO_OPENCLAW_BIN` | Caminho do binário OpenClaw, usado quando `openclaw.binary` está vazio. |
| `ALBERTO_USER_AGENT` | User-Agent das requisições HTTP de texto completo. |
| `SEMANTIC_SCHOLAR_API_KEY` | Chave da API do Semantic Scholar, enviada no cabeçalho de autenticação. |
| `SMTP_HOST` | Servidor SMTP de saída. |
| `SMTP_PORT` | Porta SMTP. Padrão `587`. |
| `SMTP_USERNAME` | Usuário SMTP, quando o servidor exige autenticação. |
| `SMTP_PASSWORD` | Senha SMTP, usada junto com `SMTP_USERNAME`. |
| `SMTP_FROM` | Remetente das mensagens. |
| `SMTP_TO` | Destinatário das mensagens. |
| `NOTION_API_KEY` | Token da integração do Notion. |
| `NOTION_DATABASE_ID` | Identificador do banco do Notion. |
| `NOTION_DATA_SOURCE_ID` | Identificador da *data source* do Notion; alternativa a `NOTION_DATABASE_ID`. |
| `ZOTERO_API_KEY` | Chave da API do Zotero. |
| `ZOTERO_LIBRARY_TYPE` | Tipo da biblioteca do Zotero. Padrão `user`. |
| `ZOTERO_LIBRARY_ID` | Identificador da biblioteca do Zotero. |
| `LOG_LEVEL` | Nível de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

!!! warning "Precedência"
    Para o caminho do binário OpenClaw, a ordem é: `openclaw.binary` no YAML,
    depois `ALBERTO_OPENCLAW_BIN`, depois o `openclaw` resolvido pelo `PATH`.

## Validando a configuração

Sempre valide antes de rodar:

```bash
alberto-research config validate examples/basic.yaml
```

Erros comuns incluem chave obrigatória ausente, `screening_threshold` fora do
intervalo `0`–`1`, `maximum_daily_deep_reads` negativo e listas declaradas como
escalares. Veja [Solução de problemas](troubleshooting.md).
