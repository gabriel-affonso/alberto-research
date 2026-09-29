# Perguntas frequentes

## Por que nenhum texto completo foi encontrado?

A resolução percorre a cadeia `fulltext.resolver_order` e para no primeiro
documento utilizável. Quando nenhum resolvedor devolve um PDF, as causas mais
comuns são:

- **O artigo não é de acesso aberto.** Sem versão OA em repositório, Unpaywall,
  OpenAlex, DOAJ, Europe PMC ou CORE, a cadeia legal simplesmente não tem o que
  baixar. Isso é esperado, não um defeito.
- **`unpaywall_email` está vazio.** O Unpaywall exige um endereço de contato e é
  ignorado sem ele.
- **`core_api_key` está vazio.** O resolvedor CORE não é usado sem chave.
- **Os filtros de DOI removeram o artigo.** Confira `research_filters.excluded_doi_prefixes`.
- **O download estourou os limites.** Reveja `download_timeout` e
  `max_fulltext_bytes` (e `ALBERTO_MAX_FULLTEXT_BYTES`).
- **A rede ou o proxy bloqueou o domínio.** Veja [Solução de problemas](troubleshooting.md).

A ausência de texto completo não impede a triagem: o candidato pode seguir para o
digest com base no resumo. O caminho padrão e documentado é apenas acesso aberto
legal.

## Qual endereço devo usar no "polite pool"?

Use um **endereço de função**, não pessoal:

```yaml
fulltext:
  unpaywall_email: "research@example.com"
```

Crossref e Unpaywall pedem um contato para identificar clientes educados e
priorizar o tráfego. Um endereço de função como `research@example.com` cumpre o
papel sem expor dados pessoais; se você tem um domínio institucional, use um
endereço de função dele. O mesmo endereço é incorporado ao
User-Agent das requisições quando `ALBERTO_USER_AGENT` não é definido.

## Quanto custam as chamadas de LLM?

Depende do provedor por trás do OpenClaw, mas o número de chamadas é previsível:

- **Triagem:** uma chamada por candidato que passa dos filtros e da deduplicação.
  O volume é aproximadamente a soma de `discovery_limits.crossref` e
  `discovery_limits.semantic_scholar`.
- **Leitura profunda:** uma chamada por artigo aprovado, limitada por
  `maximum_daily_deep_reads` e por `deep_reading_threshold`.
- **Síntese:** uma chamada por digest.

As formas mais eficazes de reduzir custo são baixar `discovery_limits`, subir
`screening_threshold` e reduzir `maximum_daily_deep_reads`. O modo `--dry-run`
não gasta chamadas de LLM, então use-o para calibrar antes de rodar de verdade.
`maximum_daily_deep_reads: 0` desliga a leitura e deixa apenas triagem e digest —
o projeto `examples/newsletter-only.yaml` faz exatamente isso.

## Consigo usar offline?

Parcialmente. As operações locais não precisam de rede:

```bash
alberto-research db migrate
alberto-research config validate examples/basic.yaml
alberto-research research digest --project examples/basic.yaml --output-dir ./digests
```

Se o digest já foi gerado e os dados estão no banco, ele pode ser regerado e salvo
sem rede. Já `research run` precisa de rede para descoberta e resolução de texto
completo, e as etapas de LLM precisam do OpenClaw. Com `--dry-run`, a descoberta
ainda acessa os provedores, mas nada é gravado.

## Onde fica o banco SQLite e como faço backup?

O caminho padrão é `$ALBERTO_HOME/alberto.sqlite3`, e `ALBERTO_HOME` tem como
padrão `~/.alberto`. Você pode sobrescrever com `ALBERTO_DB` ou com `--db` em cada
comando.

Como é um arquivo único, o backup é uma cópia:

```bash
alberto-research db migrate   # garante o esquema atualizado
cp "$HOME/.alberto/alberto.sqlite3" "$HOME/backups/alberto-$(date +%F).sqlite3"
```

Para um backup consistente enquanto o banco está em uso, prefira a ferramenta de
backup do SQLite ou pare as execuções antes de copiar. Guarde também o
`fulltext.cache_dir` se quiser preservar os PDFs baixados, e o diretório de saída
dos digests se quiser preservar o Markdown.

## Posso ter vários projetos no mesmo banco?

Sim — é o caso de uso esperado. Cada projeto tem um `id` único, e os dados ficam
separados por esse identificador. Vários arquivos YAML convivem no mesmo banco
padrão, e você escolhe qual executar com `--project`:

```bash
alberto-research research run --project examples/basic.yaml
alberto-research research run --project examples/advanced.yaml
```

Se preferir isolamento físico, use `--db` ou `ALBERTO_DB` para dar a cada projeto
seu próprio arquivo. Os comandos `notion backfill` aceitam `--project-id` para
restringir o escopo a um projeto.

## Por que a sincronização com o Notion é opcional?

Porque o SQLite já é a fonte de verdade. O Notion é uma comodidade de leitura e
arquivo, não um requisito do fluxo. Manter a integração opcional significa que:

- uma indisponibilidade ou mudança da API do Notion não interrompe descoberta,
  leitura ou entrega de e-mail;
- você não precisa de credenciais de terceiros para usar o sistema;
- quem prefere trabalhar só com Markdown local e Zotero não paga nenhum custo.

Se você não usa Notion, deixe `notion.enabled: false` e não configure
`NOTION_API_KEY` — a integração permanece inerte.

## Como mantenho o uso legal?

Seguindo o caminho padrão, que é apenas acesso aberto:

- Deixe `enable_scihub: false` e `enable_annas_archive: false` — que já é o padrão.
- Não instale o extra `legacy-resolvers`.
- Use a cadeia de resolvedores legais: Zotero, Unpaywall, OpenAlex, CORE, DOAJ,
  Europe PMC e URL do provedor.
- Use um endereço de função em `unpaywall_email` e respeite os limites dos
  provedores.
- Guarde localmente apenas o que você tem direito de guardar.

Se você ativar os resolvedores de bibliotecas sombra, **a responsabilidade legal
é exclusivamente sua**; eles exigem o extra `legacy-resolvers`, desativam a
verificação de certificado TLS e não são o caminho documentado. Leia
[Segurança](security.md) antes.

## Preciso revisar o que o LLM escreve?

Sim. A saída de leitura é validada por JSON Schema — estrutura, tipos e presença
de campos obrigatórios — mas validação de esquema garante forma, **não** verdade.
O digest é um ponto de partida para a sua leitura, e não um substituto dela. Use o
tipo de feedback `READ_PERSONALLY` para marcar o que você pretende conferir e
`INVESTIGATE_REFERENCES` para sinalizar artigos cujas referências merecem ser
seguidas.

## O que o feedback muda na prática?

O feedback fica registrado no banco e informa as execuções seguintes: itens
marcados como `IRRELEVANT` sinalizam que a triagem precisa ser mais estrita, e
itens `VERY_IMPORTANT` indicam temas que valem mais peso. Como o registro é
associado ao projeto, o histórico de cada linha de pesquisa evolui
independentemente. Veja [Uso](usage.md) para os cinco tipos disponíveis.

## Como atualizo o banco depois de atualizar o pacote?

Atualize o pacote (veja [Instalação](installation.md)) e rode:

```bash
alberto-research db migrate
```

As migrações SQL viajam dentro do pacote e são aplicadas de forma incremental; a
tabela de controle registra o que já foi aplicado, então o comando é seguro de
repetir.
