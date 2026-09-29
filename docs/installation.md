# Instalação

O `alberto-research` é distribuído como pacote Python com layout `src`,
`requires-python >= 3.11`, e fornece o script de console `alberto-research`
(equivalente a `python -m alberto_research`).

## Requisitos

- **Python 3.11 ou superior.** As versões 3.11, 3.12 e 3.13 são suportadas e
  testadas.
- **SQLite**, já incluído na biblioteca padrão do Python.
- Acesso de rede para descoberta e resolução de texto completo. O uso offline é
  possível para consultar o banco local (veja [Perguntas frequentes](faq.md)).
- Opcionalmente, o binário `openclaw` no `PATH` para as etapas de LLM.

## Escolhendo o caminho de instalação

### `pipx` — recomendado para uso como CLI

O `pipx` cria um ambiente virtual isolado por aplicação e coloca apenas o script
no `PATH`, evitando conflitos com outras dependências do sistema.

```bash
pipx install alberto-research
```

Para atualizar depois:

```bash
pipx upgrade alberto-research
```

### `uv tool install` — recomendado se você já usa `uv`

```bash
uv tool install alberto-research
```

Para atualizar:

```bash
uv tool upgrade alberto-research
```

### `pip install` — para uso como biblioteca

Use quando quiser importar `alberto_research` de outro programa Python ou dentro
de um ambiente virtual de projeto.

```bash
python -m venv .venv
source .venv/bin/activate
pip install alberto-research
```

Em Windows, a ativação do ambiente é:

```powershell
.venv\Scripts\Activate.ps1
```

## Extras opcionais

O pacote base contém tudo o que o fluxo padrão de acesso aberto precisa. Existem
extras declarados no `pyproject.toml`:

| Extra | Para que serve |
| --- | --- |
| `test` | Ferramentas para executar a suíte de testes. |
| `dev` | Ferramentas de lint, tipagem, auditoria e testes. |
| `docs` | Material for MkDocs, mkdocstrings e o plugin Mermaid. |
| `legacy-resolvers` | Resolvedores de bibliotecas sombra. **Desligados por padrão; uso por sua conta e risco legal.** |

Para instalar com um extra:

```bash
pipx install "alberto-research[legacy-resolvers]"
```

!!! danger "Sobre o extra `legacy-resolvers`"
    Esse extra habilita os resolvedores opcionais de Sci-Hub, Library Genesis e
    Anna's Archive. Eles ficam **desligados por padrão**, exigem
    `enable_scihub: true` no projeto, **desativam a verificação de certificado
    TLS** e são de **responsabilidade legal exclusiva do operador**. O caminho
    padrão e documentado é apenas acesso aberto legal. Leia
    [Segurança](security.md) antes de prosseguir.

## Verificando a instalação

Confirme a versão instalada:

```bash
alberto-research --version
```

Confirme que o módulo é importável e que o banco responde aplicando as migrações
pendentes:

```bash
python -c "import alberto_research; print(alberto_research.__name__)"
alberto-research db migrate
```

Valide um projeto de exemplo:

```bash
alberto-research config validate examples/basic.yaml
```

Se os três comandos terminarem sem erro, a instalação está funcional.

## Desinstalação

Com `pipx`:

```bash
pipx uninstall alberto-research
```

Com `uv`:

```bash
uv tool uninstall alberto-research
```

Com `pip`, dentro do ambiente virtual:

```bash
pip uninstall alberto-research
```

A desinstalação remove o pacote e o script de console, mas **não** apaga seus
dados operacionais. Para remover também o banco, o cache de PDFs e os digests
salvos, apague manualmente o diretório apontado por `ALBERTO_HOME` (por padrão
`~/.alberto`), além de `.cache/fulltext` e do diretório de saída de digests do
projeto. Veja [Perguntas frequentes](faq.md) para saber onde cada arquivo fica.

## Uso com Docker

O repositório traz um `Dockerfile` de runtime, mas **não publica uma imagem
oficial**. Construa a sua a partir do código:

```bash
docker build -t alberto-research:local .
```

O `Dockerfile` é multi-stage: o estágio de build compila as dependências em um
virtualenv isolado e o estágio final recebe apenas esse virtualenv, sem
compiladores nem cache do `pip`. A imagem final:

- parte de `python:3.12-slim-bookworm`;
- define `ALBERTO_HOME=/home/app`, o mesmo diretório de trabalho do processo;
- roda como usuário sem privilégios `app` (UID/GID 10001), não como `root`;
- tem `ENTRYPOINT ["alberto-research"]` e `CMD ["--help"]`;
- declara um `HEALTHCHECK` que executa `alberto-research --version`.

Como o ENTRYPOINT já é o script de console, passe os argumentos diretamente:

```bash
docker run --rm \
  -v "$PWD/examples:/work/examples:ro" \
  -v alberto-data:/home/app \
  alberto-research:local config validate /work/examples/basic.yaml
```

Para rodar o fluxo:

```bash
docker run --rm \
  -v "$PWD/examples:/work/examples:ro" \
  -v alberto-data:/home/app \
  -e SEMANTIC_SCHOLAR_API_KEY \
  -e SMTP_HOST -e SMTP_PORT -e SMTP_FROM -e SMTP_TO \
  alberto-research:local research run --project /work/examples/basic.yaml
```

Para usar um banco em volume próprio e um diretório de digests na máquina host:

```bash
docker run --rm \
  -v "$PWD/examples:/work/examples:ro" \
  -v alberto-data:/home/app \
  -v "$PWD/digests:/work/digests" \
  alberto-research:local research digest \
    --project /work/examples/basic.yaml \
    --output-dir /work/digests
```

Pontos de atenção ao usar containers:

- Monte um volume em `/home/app` (o valor de `ALBERTO_HOME`); sem isso, o banco
  SQLite é descartado a cada execução.
- Passe segredos por variáveis de ambiente do runtime, nunca os grave no
  `Dockerfile`.
- Para as etapas de LLM, o binário `openclaw` precisa existir **dentro** do
  container, ou aponte `ALBERTO_OPENCLAW_BIN` para um caminho disponível.
- O `Dockerfile` não instala o extra `legacy-resolvers`; os resolvedores de
  bibliotecas sombra permanecem indisponíveis, que é o padrão desejado.
