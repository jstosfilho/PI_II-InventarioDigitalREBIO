# Publicar o Inventário REBIO na Vercel

**Primeira publicação?** Use o [guia para iniciantes, com cliques, comandos e resultados esperados](PUBLICAR_VERCEL_PARA_INICIANTES.md). Este documento mantém a referência técnica da configuração.

Atualizado em 15/10/2026. Configuração preparada; nenhuma conta, banco em nuvem ou publicação foi criada nesta etapa.

## O que será publicado

Flask na Vercel e PostgreSQL externo para contas, registros e histórico. O SQLite continua disponível no VS Code quando `DATABASE_URL` não está configurada. Não usar SQLite em `/tmp`: esse diretório não preserva um banco compartilhado entre instâncias.

Arquivos preparados: `app.py`, `vercel.json`, `pyproject.toml`, `.vercelignore`, `inventario/database.py`, `inventario/schema_postgres.sql`, `tools/build_vercel.py` e `tools/setup_cloud.py`. O build copia CSS e JavaScript para `public/static`; não conecta nem inicializa o banco. A Vercel executa Flask diretamente como função, sem Waitress ou Docker neste fluxo.

Referências: [Flask na Vercel](https://vercel.com/docs/frameworks/backend/flask) e [persistência de SQLite](https://vercel.com/kb/guide/is-sqlite-supported-in-vercel).

## 1. Criar as contas e o banco

1. Criar uma conta na [Vercel](https://vercel.com/signup).
2. Criar uma conta e um projeto PostgreSQL no [Neon](https://console.neon.tech/). É uma opção para este roteiro; outro PostgreSQL acessível por rede também pode ser utilizado. Conferir condições e limites do plano no momento da criação.
3. No painel do banco, abrir **Connect** e obter a URL PostgreSQL. Para a aplicação, preferir a URL com pooling e manter as opções TLS fornecidas pelo provedor, como `sslmode=require`.
4. Guardar a URL em local privado. Não colocá-la no Git, no chat ou nos arquivos públicos.

O driver utiliza conexões por requisição e desativa prepared statements automáticos para compatibilidade com poolers transacionais. Referências: [conectar ao Neon](https://neon.com/docs/get-started/connect-neon), [pooling](https://neon.com/docs/connect/connection-pooling) e [transações no Psycopg](https://www.psycopg.org/psycopg3/docs/basic/transactions.html).

## 2. Preparar o banco e o gestor pelo VS Code

Abrir a pasta `C:\UNIVESP\PI_II` no VS Code. No terminal PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tools/setup_cloud.py
```

O assistente solicita a URL do banco com entrada oculta, o login do gestor e a senha com confirmação. Ele cria as tabelas se estiverem ausentes e a conta solicitada. Não grava a URL ou a senha em arquivos. Usar a URL direta do provedor para essa inicialização caso o pooler não permita DDL.

Se já existir o login, as tabelas são preservadas e a senha não é substituída. Para criar outro usuário, executar o assistente com outro login; para outros perfis, usar o comando Flask `create-user` em um ambiente com `DATABASE_URL` configurada com segurança.

**Este roteiro começa um banco novo.** Contas, registros e histórico do SQLite local não são copiados automaticamente. A exportação GeoJSON não contém contas ou histórico completo. Se houver acervo real a transferir, realizar uma migração separada e conferida antes de trocar o ambiente usado pela equipe.

## 3. Vincular o projeto à Vercel

É possível publicar diretamente desta pasta, sem criar um repositório GitHub agora. É necessário ter Node.js/npm instalados.

```powershell
npx.cmd vercel@latest login
npx.cmd vercel@latest link
```

No `link`, escolher a conta desejada, criar um projeto novo e usar a pasta atual (`./`). Pode adotar o nome `inventario-rebio` se estiver disponível. Quando forem apresentadas configurações de framework/build, usar **Flask** e os padrões do projeto. Não definir uma pasta de saída de frontend nem usar `flask run` como Build Command.

O arquivo `.vercel/project.json` criado pelo vínculo é local e está ignorado no Git. `.vercelignore` exclui banco local, segredos, materiais do grupo e arquivos de revisão do envio por CLI. Não publicar uma pasta `public` contendo documentos ou dados privados; o build deste projeto gera apenas os assets da interface.

## 4. Configurar as variáveis no painel

No projeto Vercel, abrir **Settings → Environment Variables** e cadastrar:

| Nome | Valor |
| --- | --- |
| `DATABASE_URL` | URL PostgreSQL do banco de produção, preferencialmente com pooling e TLS |
| `REBIO_SECRET_KEY` | Segredo aleatório forte, com pelo menos 32 caracteres |
| `REBIO_SECURE_COOKIE` | `1` |

Para gerar o segredo localmente:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Copiar o valor apenas para o painel. `VERCEL=1` é fornecido pela plataforma; não precisa cadastrá-lo. Não configurar `REBIO_DATABASE`, `PORT` ou caminhos de arquivo do SQLite na Vercel.

Configurar as variáveis de produção para **Production**. Para testar em **Preview**, usar outro banco ou branch de banco e outro segredo; isso evita que cadastros ou exclusões de testes atinjam o inventário de produção. As variáveis são aplicadas em novos deployments, portanto publicar novamente após alterá-las.

## 5. Publicar

Após preparar o banco e configurar as variáveis:

```powershell
npx.cmd vercel@latest --prod
```

O comando retorna a URL de publicação. Abrir a URL e testar login, cadastro, edição, filtros, histórico e exportação com um registro claramente identificado como teste. Sair e entrar novamente e conferir se o registro persiste. Excluir somente esse registro de teste.

O endpoint `/health` verifica a resposta da aplicação, mas não garante conexão com o banco. É necessário testar login e persistência. O mapa depende de internet e do provedor externo de tiles, com atribuição e Referer preservados.

Referências dos comandos: [deploy](https://vercel.com/docs/cli/deploy) e [variáveis de ambiente](https://vercel.com/docs/cli/env).

## Limites desta publicação

- A Vercel limita o corpo de requisições e respostas de funções a 4,5 MB. A aplicação aceita arquivos GPX/KML de até **4 MiB** na Vercel, com margem para multipart; localmente mantém **15 MiB**. O limite aparece na interface.
- Criação e edição possuem limite de 4 MiB de JSON na Vercel. Geometrias muito grandes precisam ser simplificadas antes do envio, mesmo quando o GPX original cabe no limite.
- Listagem, histórico e exportação ainda não têm paginação. Um acervo grande pode exceder o limite de resposta; filtros reduzem listagem/exportação, mas paginação e exportação por lotes serão necessárias para escalar.
- O PostgreSQL preserva o modelo existente, com GeoJSON e snapshots em texto. PostGIS não foi adicionado.
- Backup e recuperação devem ser configurados no provedor PostgreSQL. O procedimento de copiar o arquivo SQLite aplica-se apenas ao ambiente local.
- O acesso aos dados continua autenticado. Antes do uso institucional, concluir a validação dos perfis, a avaliação manual de acessibilidade e a proteção contra tentativas repetidas de login já listadas no plano de implantação.

Referência: [limites das funções Vercel](https://vercel.com/docs/functions/limitations).

## Problemas frequentes

| Sintoma | Verificar |
| --- | --- |
| Erro solicitando `DATABASE_URL` | Variável cadastrada no ambiente do deployment e publicação refeita |
| Erro solicitando `REBIO_SECRET_KEY` | Segredo presente e com pelo menos 32 caracteres |
| Erro de tabela inexistente no login | Executar o assistente de inicialização no mesmo banco configurado na Vercel |
| Conexão recusada ou timeout | URL, TLS, disponibilidade e políticas de acesso do provedor |
| CSS ou JavaScript não carrega | Build `python tools/build_vercel.py` executado e arquivos em `public/static` |
| Erro 413 | Arquivo, geometria ou resposta acima do limite da plataforma |
| Login volta à tela inicial | Cookies permitidos, acesso HTTPS e segredo estável entre deployments |

## Testes locais

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes PostgreSQL são opcionais e exigem `REBIO_TEST_DATABASE_URL` apontando para um banco de testes. Cada caso cria e remove um schema próprio; nunca usar esse parâmetro com o acervo de produção. A validação local não substitui testar o deployment real na conta da Vercel.
