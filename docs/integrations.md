# Integrações

Todas as integrações são **opcionais**. O núcleo do sistema funciona apenas com o
SQLite local; Zotero, Notion e e-mail apenas movem os resultados para onde você já
trabalha.

## Zotero

O Zotero tem dois papéis:

1. **Fonte de texto completo.** O resolvedor `zotero` é o primeiro da cadeia
   padrão: se você já tem o PDF na biblioteca, nenhuma requisição externa é feita.
2. **Arquivo de leituras.** As leituras concluídas podem ser enviadas para a
   biblioteca.

### Configuração

| Item | Como definir |
| --- | --- |
| Chave da API | `ZOTERO_API_KEY` no ambiente. |
| Tipo de biblioteca | `ZOTERO_LIBRARY_TYPE`; o padrão é `user`. |
| Identificador da biblioteca | `ZOTERO_LIBRARY_ID`. |

Gere a chave em `https://www.zotero.org/settings/keys` (chaves com permissão de
leitura já bastam para o resolvedor; escrita é necessária para arquivar) e
descubra o `library_id` na mesma página de configurações.

```bash
export ZOTERO_API_KEY="sua-chave"
export ZOTERO_LIBRARY_TYPE="user"
export ZOTERO_LIBRARY_ID="0000000"
```

Verifique se o resolvedor está ativo consultando a ordem do projeto:

```bash
alberto-research config validate examples/basic.yaml
```

Se o Zotero não estiver configurado, o resolvedor é ignorado e a cadeia segue para
`unpaywall`.

## Notion

O Notion funciona como arquivo de leituras estruturado. A integração cria um banco
com as propriedades esperadas e depois preenche as páginas.

### 1. Criar a integração

1. Acesse `https://www.notion.so/my-integrations` e crie uma integração interna.
2. Copie o token e exporte como `NOTION_API_KEY`.
3. Compartilhe a página pai desejada com a integração — sem esse
   compartilhamento, a API não enxerga a página.

### 2. Criar o banco de arquivamento

```bash
alberto-research notion setup \
  --parent-page-id 00000000000000000000000000000000 \
  --title "Alberto Research Library"
```

O `--parent-page-id` é obrigatório; `--title` tem como padrão
`Alberto Research Library`. O comando imprime o identificador do banco criado.

### 3. Apontar a data source

Exporte o identificador retornado como `NOTION_DATA_SOURCE_ID`. Como alternativa,
`NOTION_DATABASE_ID` também é aceito. A integração exige **um dos dois**; sem
nenhum, ela falha com uma mensagem explícita.

```bash
export NOTION_DATA_SOURCE_ID="00000000-0000-0000-0000-000000000000"
```

### 4. Habilitar

O envio fica desligado a menos que uma destas condições seja verdadeira:

- o projeto declara `notion.enabled: true`; ou
- o ambiente define `ALBERTO_NOTION_ENABLED=1`.

A ativação por ambiente é útil em containers, onde editar o YAML não é prático.

### 5. Backfill

Para enviar o que já está no SQLite:

```bash
alberto-research notion backfill --project-id alberto-research-example
```

Sem `--project-id`, todos os projetos são considerados. Use `--db` para apontar a
outro banco:

```bash
alberto-research notion backfill --db ./alberto-dev.sqlite3 --project-id alberto-research-example
```

O backfill é seguro de repetir: registros já arquivados não geram duplicatas.

## Entrega de e-mail

A entrega é acionada quando `ALBERTO_EMAIL_PROVIDER` tem o valor `smtp`. Sem essa
variável, o digest ainda é salvo localmente (se `digest.save_local` for `true`),
mas não é enviado.

| Variável | Obrigatória | Descrição |
| --- | --- | --- |
| `ALBERTO_EMAIL_PROVIDER` | Sim, com o valor `smtp` | Seleciona o provedor de e-mail. |
| `SMTP_HOST` | Sim | Servidor SMTP de saída. |
| `SMTP_PORT` | Não | Porta do servidor. Padrão `587`. |
| `SMTP_USERNAME` | Não | Usuário para autenticação; necessária em servidores autenticados. |
| `SMTP_PASSWORD` | Não | Senha usada junto com `SMTP_USERNAME`. |
| `SMTP_FROM` | Sim | Endereço do remetente. |
| `SMTP_TO` | Sim | Endereço do destinatário. |

Exemplo de configuração:

```bash
export ALBERTO_EMAIL_PROVIDER="smtp"
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USERNAME="research@example.com"
export SMTP_PASSWORD="senha-de-aplicativo"
export SMTP_FROM="research@example.com"
export SMTP_TO="research@example.com"
```

A autenticação só é tentada quando `SMTP_USERNAME` está definida; nesse caso,
`SMTP_PASSWORD` precisa estar correta, ou a entrega falha com erro de autenticação.

## OpenClaw

As etapas de LLM são executadas pelo binário OpenClaw, que recebe um arquivo de
mensagem e devolve JSON. O `alberto-research` não chama a API de um modelo
diretamente.

### Resolução do binário

A ordem é:

1. `openclaw.binary` no YAML do projeto;
2. `ALBERTO_OPENCLAW_BIN` no ambiente;
3. `openclaw` resolvido pelo `PATH`.

```yaml
openclaw:
  binary: /usr/local/bin/openclaw
```

Se nenhuma das opções resolver para um executável, o fluxo falha com um erro de
binário não encontrado — veja [Solução de problemas](troubleshooting.md).

### Invocação

Para cada etapa, o binário é chamado no formato:

```bash
openclaw agent --agent <nome> --message-file <arquivo> --json
```

O prompt é escrito em um arquivo temporário e passado por `--message-file`; a
saída precisa ser JSON, e um tempo limite pode ser imposto com `--timeout`.

### Agentes

| Agente | Papel |
| --- | --- |
| `alberto-research` | Agente de triagem: julga a relevância dos candidatos contra a pergunta de pesquisa. |
| `research-reader` | Agente de leitura: extrai a saída estruturada do texto completo. Roda isolado e **não** deve receber finanças, acesso amplo ao sistema de arquivos, e-mail, ferramentas destrutivas, cookies de navegador ou segredos não relacionados. |

Esses nomes são os padrões do pacote. Mantenha o agente de leitura restrito: ele
processa conteúdo externo hostil por definição. Veja [Segurança](security.md).
