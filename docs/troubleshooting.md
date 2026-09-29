# Solução de problemas

Esta página reúne os erros mais comuns e como corrigi-los. Comece sempre por
confirmar a versão e o estado do banco:

```bash
alberto-research --version
alberto-research db migrate
alberto-research config validate examples/basic.yaml
```

## As migrações não foram aplicadas

**Sintoma:** erros de "no such table" ou consultas que falham logo no início de
`research run` ou `research digest`.

**Causa:** o banco existe, mas o esquema ainda não foi criado — típico de uma
instalação nova ou de um pacote recém-atualizado.

**Correção:** aplique as migrações pendentes:

```bash
alberto-research db migrate
```

Se você usa um banco não padrão, informe o mesmo caminho em todos os comandos:

```bash
alberto-research db migrate --db ./alberto-dev.sqlite3
```

!!! tip
    O comando é idempotente: a tabela de controle de migrações registra o que já
    foi aplicado, então repetir é seguro.

## Faltam chaves de API

**Sintoma:** descoberta vazia, resolvedor CORE ignorado, erros de autenticação no
Semantic Scholar ou no Unpaywall, ou falhas ao falar com Zotero e Notion.

**Causa:** as variáveis de ambiente esperadas não estão definidas no processo.

**Correção:** exporte as variáveis no mesmo shell (ou no mesmo serviço) que
executa o comando. As mais afetadas:

| Recurso | Variável |
| --- | --- |
| Semantic Scholar | `SEMANTIC_SCHOLAR_API_KEY` |
| CORE | `core_api_key` no projeto, ou `CORE_API_KEY` no ambiente |
| Unpaywall | `unpaywall_email` no projeto |
| Zotero | `ZOTERO_API_KEY`, `ZOTERO_LIBRARY_TYPE`, `ZOTERO_LIBRARY_ID` |
| Notion | `NOTION_API_KEY` e `NOTION_DATA_SOURCE_ID` ou `NOTION_DATABASE_ID` |

Sem a chave do CORE ou o endereço do Unpaywall, a cadeia continua nos outros
resolvedores — esses casos degradam, não quebram. Já o Notion, quando habilitado,
exige `NOTION_API_KEY` e um identificador de data source, e falha com mensagem
explícita se faltarem.

## `openclaw` não encontrado

**Sintoma:** erro de executável não encontrado ao rodar a triagem ou a leitura.

**Causa:** o binário não está no `PATH` e não foi indicado explicitamente.

**Correção:** informe o caminho de uma das duas formas. No YAML do projeto:

```yaml
openclaw:
  binary: /usr/local/bin/openclaw
```

Ou no ambiente:

```bash
export ALBERTO_OPENCLAW_BIN="/usr/local/bin/openclaw"
```

A ordem de resolução é `openclaw.binary`, depois `ALBERTO_OPENCLAW_BIN`, depois o
`PATH`. Confirme com:

```bash
command -v openclaw
```

Em containers, lembre-se de que o binário precisa existir **dentro** do container,
não apenas no host. Um `--timeout` curto demais também pode derrubar uma etapa de
LLM legítima e lenta; se as chamadas funcionam fora do fluxo mas falham nele,
reveja esse limite.

## Problemas de TLS ou proxy

**Sintoma:** erros de certificado SSL/TLS, `CERTIFICATE_VERIFY_FAILED`, timeouts
de conexão ou downloads que falham apenas na sua rede.

**Causa:** proxy corporativo, inspeção de TLS ou certificados raiz ausentes no
ambiente Python.

**Correção:**

- Configure o proxy pelas variáveis usuais do `requests`, como `HTTPS_PROXY` e
  `HTTP_PROXY`, e reinicie o comando.
- Instale os certificados raiz da sua organização no armazenamento de
  certificados do Python (`certifi`) em vez de desativar a verificação.
- Aumente `fulltext.download_timeout` se a rede for lenta.

!!! danger "Não desative a verificação de TLS"
    Desativar a verificação de certificado expõe o tráfego a interceptação. Os
    únicos resolvedores que fazem isso são os de bibliotecas sombra, que são
    desligados por padrão, exigem o extra `legacy-resolvers` e são de
    responsabilidade legal do operador. Não é o caminho documentado.

## Limites de taxa (*rate limits*)

**Sintoma:** respostas HTTP 429, 403 ou avisos de requisições recusadas pelos
provedores.

**Causa:** volume de requisições acima do que o provedor tolera para clientes
anônimos ou com chave.

**Correção:**

- Defina `SEMANTIC_SCHOLAR_API_KEY` — clientes autenticados têm limites maiores.
- Reduza `discovery_limits.crossref` e `discovery_limits.semantic_scholar`.
- Defina um `unpaywall_email` de função para entrar no *polite pool*.
- Evite execuções sobrepostas: não agende duas passagens de `research run` no
  mesmo horário.
- Se o problema persistir, aguarde alguns minutos antes de repetir.

## Disco cheio ou banco bloqueado

**Sintoma:** erros de escrita, `database is locked` ou `disk I/O error`.

**Causa:** o cache de PDFs cresceu, ou duas execuções escrevem no mesmo SQLite ao
mesmo tempo.

**Correção:**

- Verifique o espaço disponível e limpe o cache antigo em `fulltext.cache_dir`
  (o padrão do exemplo é `.cache/fulltext`).
- Reduza `max_fulltext_bytes` para evitar PDFs gigantes.
- Não rode dois `research run` simultâneos contra o mesmo banco. Se precisar
  paralelizar, dê a cada processo um `--db` distinto.
- Encerre processos travados antes de tentar de novo; um `database is locked`
  persistente costuma indicar outro processo ainda segurando o arquivo.

## O digest veio vazio

**Sintoma:** `research digest` termina sem erro, mas não gera itens nem arquivo.

**Causa e correção, em ordem de probabilidade:**

1. **`digest.enabled` é `false`.** Ative no YAML do projeto.
2. **Não houve candidatos acima de `screening_threshold`.** Reduza o limiar ou
   amplie `priority_topics`, `inclusion_terms` e `discovery_limits`.
3. **`research run` nunca rodou contra aquele banco.** Confirme que `--db` aponta
   para o mesmo arquivo nos dois comandos.
4. **Os filtros removeram tudo.** Revise `research_filters`, `exclusion_terms` e
   `date_ranges`.
5. **`digest.max_items` é muito baixo** ou os itens já foram consumidos por uma
   execução anterior com `skip_previously_read`.
6. **`digest.save_local` é `false`** e não há provedor de e-mail configurado, então
   nada é gravado nem enviado.

Para inspecionar sem gastar LLM, comece pelo ensaio:

```bash
alberto-research research run --project examples/basic.yaml --dry-run
```

Se o ensaio lista candidatos mas o digest continua vazio, o problema está nos
limiares ou no estado do banco, não na descoberta.

## A configuração não valida

**Sintoma:** `config validate` retorna erro.

**Correção:** os erros são específicos. Causas frequentes:

- Campo obrigatório ausente — confira a lista em [Configuração](configuration.md).
- `screening_threshold` ou `deep_reading_threshold` fora de `0`–`1`.
- `maximum_daily_deep_reads` negativo.
- `priority_topics`, `languages`, `inclusion_terms` ou `exclusion_terms`
  declarados como escalar em vez de lista.
- Indentação inconsistente no YAML, especialmente dentro de blocos aninhados.

## Ainda preso?

Verifique também:

- [Perguntas frequentes](faq.md) — comportamento esperado, custo, offline, backup.
- [Integrações](integrations.md) — credenciais e nomes exatos das variáveis.
- [Segurança](security.md) — antes de considerar qualquer resolvedor opcional.
