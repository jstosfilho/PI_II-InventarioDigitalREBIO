# Publicar o projeto na internet: guia para iniciantes

Atualizado em 16/10/2026. Este guia usa a configuração já preparada na pasta `C:\UNIVESP\PI_II`. As etapas abaixo serão executadas por você; escrever este guia não cria contas nem publica o sistema.

## Antes de começar

Você vai usar três lugares:

| Lugar | Para que serve |
| --- | --- |
| VS Code no seu computador | Abrir o projeto e executar os comandos |
| Site do Neon | Guardar usuários, cadastros e histórico em um banco na internet |
| Site da Vercel | Hospedar o sistema e fornecer o endereço para acessá-lo |

O sistema local usa SQLite, um arquivo no computador. A versão publicada usará PostgreSQL no Neon. **Os cadastros e as contas locais não aparecem automaticamente no site publicado.** Este procedimento prepara um banco novo. Se você já tiver dados reais a transferir, essa transferência precisa de uma etapa própria.

Não é necessário criar um repositório GitHub para seguir este caminho. Você precisa de acesso à internet, um e-mail e permissão para instalar programas no computador, se algum estiver faltando. Confira os planos apresentados pelos serviços antes de contratar; o roteiro não exige escolher uma modalidade paga.

Siga as etapas na ordem. Execute um comando de cada vez e espere terminar. Não copie a palavra `powershell`, as marcações do bloco de código ou o texto `PS C:\...>` que aparece no terminal.

## 1. Abrir a pasta certa no VS Code

1. Abra o VS Code.
2. Clique em **Arquivo → Abrir Pasta**. Se estiver em inglês: **File → Open Folder**.
3. Escolha `C:\UNIVESP\PI_II` e confirme.
4. No lado esquerdo, confira se aparecem `inventario`, `tools`, `requirements.txt` e `vercel.json`.
5. Clique em **Terminal → Novo Terminal**, ou **Terminal → New Terminal**.
6. Na área que abrir na parte inferior, use um terminal **PowerShell**. Se outro estiver selecionado, abra a seta ao lado do botão `+` e escolha PowerShell.

Digite e pressione Enter:

```powershell
Set-Location 'C:\UNIVESP\PI_II'
```

Confira a pasta atual:

```powershell
Get-Location
```

**Resultado esperado:** aparecer `C:\UNIVESP\PI_II`. Se aparecer outra pasta, repita o primeiro comando.

Se o terminal estiver ocupado executando o servidor local, crie outro terminal pelo botão `+`. Não precisa fechar o servidor para seguir este roteiro.

## 2. Conferir Python e Node.js

Primeiro execute:

```powershell
.\.venv\Scripts\python.exe --version
```

**Resultado esperado:** `Python 3.12.x`. O `x` representa o número da atualização instalada. O ambiente `.venv` já foi preparado neste projeto.

Se aparecer que o caminho não existe, será necessário recriar o ambiente. Com Python 3.12 instalado, execute:

```powershell
py -3.12 -m venv .venv
```

Se `py` não for reconhecido ou Python 3.12 não estiver instalado, obtenha o instalador pelo [site oficial do Python](https://www.python.org/downloads/windows/), instale a versão 3.12 e reabra o VS Code antes de repetir. A configuração atual da publicação declara Python 3.12.

Agora execute, separadamente:

```powershell
node --version
```

```powershell
npm.cmd --version
```

**Resultado esperado:** cada comando mostra um número de versão. Se algum não for reconhecido, instale a versão **LTS** do [Node.js](https://nodejs.org/en/download), mantendo a instalação do npm. Feche e abra novamente o VS Code e repita a conferência. Node.js é usado pelas ferramentas de publicação; o servidor do projeto continua sendo Python.

Os comandos com `.cmd` evitam depender da permissão de execução de scripts PowerShell. Não é preciso ativar a `.venv` nem mudar a política de segurança do Windows.

## 3. Instalar as dependências do projeto

No mesmo terminal, execute:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Espere voltar a aparecer a linha onde você pode digitar comandos.

**Resultado esperado:** mensagens como `Successfully installed` ou `Requirement already satisfied`. A segunda significa que o pacote já estava instalado. Um aviso de atualização do pip, sozinho, não indica falha.

Se aparecer erro de conexão, confira a internet e tente novamente. Se aparecer que `requirements.txt` não existe, volte à etapa 1: provavelmente o terminal está em outra pasta.

## 4. Criar o banco no Neon

1. Abra [console.neon.tech](https://console.neon.tech/) no navegador.
2. Crie sua conta ou entre na conta existente. Conclua eventual confirmação de e-mail.
3. Procure a opção para criar um projeto, como **New Project** ou **Create Project**.
4. Use um nome identificável, por exemplo `inventario-rebio`.
5. Escolha uma região disponível adequada ao local onde o sistema será usado. Se não souber qual escolher, mantenha a sugestão inicial e anote a região escolhida.
6. Conclua a criação e abra o projeto.
7. Procure **Connect**. Essa opção mostra como conectar ao banco.
8. Copie a **connection string**, ou **URL de conexão PostgreSQL**. Ela deve começar com `postgresql://` ou `postgres://`.

Os nomes dos botões podem variar. A documentação do Neon descreve o [painel de projetos](https://neon.com/docs/get-started/signing-up) e a [obtenção da conexão](https://neon.com/docs/get-started/connect-neon).

Exemplo **fictício**, apenas para reconhecer o formato:

```text
postgresql://USUARIO:SENHA@SERVIDOR/BANCO?sslmode=require
```

**Não copie esse exemplo para configurar o projeto.** Use o valor completo fornecido pelo seu painel, preservando as opções no final. Para cadastrar na Vercel, copie apenas a URL, sem um comando `psql` antes dela e sem aspas em volta. O assistente do terminal também aceita o formato `psql 'URL'`, aspas ao redor da URL e `DATABASE_URL=URL`, removendo esses envoltórios automaticamente.

Para a aplicação na Vercel, prefira a conexão com **pooling** ativado, quando oferecida. Guarde a URL de forma privada: ela contém credenciais de acesso ao banco. Não envie essa informação no chat nem a coloque nos arquivos do projeto.

**Resultado esperado:** projeto Neon criado e URL de conexão disponível para a próxima etapa.

## 5. Criar as tabelas e seu login no sistema

Volte ao terminal do VS Code e execute:

```powershell
.\.venv\Scripts\python.exe tools/setup_cloud.py
```

O programa fará estas solicitações:

| O que aparece | O que você faz |
| --- | --- |
| `Cole DATABASE_URL do PostgreSQL (entrada oculta):` | Cole a URL real copiada do Neon e pressione Enter |
| `Login do gestor a criar:` | Digite o login desejado, por exemplo `jorge`, e pressione Enter |
| `Password:` | Digite uma senha de pelo menos 10 caracteres e pressione Enter |
| `Repeat for confirmation:` | Digite a mesma senha novamente e pressione Enter |

**É normal não aparecerem letras nem asteriscos ao colar a URL ou digitar a senha.** Isso protege a informação. No terminal integrado, tente Ctrl+V para colar; se necessário, use a opção Colar do menu de contexto. Não cole a URL no lugar do login.

Se a colagem oculta resultar em conexão inválida, primeiro cole o comando abaixo no terminal **sem pressionar Enter**:

```powershell
.\.venv\Scripts\python.exe tools/setup_cloud.py --clipboard
```

Agora volte ao Neon e copie a connection string. Retorne ao terminal e pressione Enter para executar o comando que já está digitado. Não cole a conexão e não copie outro texto nesse intervalo: copiar o comando depois da conexão substituiria o conteúdo da área de transferência.

Essa opção lê diretamente o texto copiado no Windows, sem exibi-lo nem gravá-lo. Depois de validar o formato, o assistente pede o login e a senha do gestor normalmente.

Guarde seu login e sua senha: são eles que você usará para entrar no inventário. Eles são diferentes da conta do Neon e da conta da Vercel.

**Resultado esperado:** aparecerem mensagens equivalentes a:

```text
Banco inicializado (registros existentes preservados).
Usuário criado.
Banco e gestor preparados. Cadastre DATABASE_URL no painel da Vercel.
```

Se aparecer **Usuário já existe**, o login já foi cadastrado e a senha não foi trocada. Se você conhece a senha, pode continuar. Se precisar recuperar acesso, não apague o banco para tentar resolver.

Se aparecer **Não foi possível preparar o banco**, confira se copiou a URL inteira, se o projeto Neon está disponível e se há acesso à internet. Se usou a URL com pooling, tente a conexão direta oferecida no mesmo painel para esta inicialização. Depois, a aplicação pode utilizar a URL com pooling do mesmo banco.

## 6. Criar sua conta na Vercel

1. Abra [vercel.com/signup](https://vercel.com/signup).
2. Crie a conta usando um método de acesso disponível.
3. Conclua a confirmação solicitada pelo serviço.
4. Mantenha a conta aberta no navegador.

**Resultado esperado:** você consegue acessar o painel da Vercel. Não é necessário importar um repositório nesta etapa: vamos vincular a pasta pelo terminal.

## 7. Conectar o terminal à sua conta Vercel

No VS Code, execute:

```powershell
npx.cmd vercel@latest login
```

Se o npm perguntar se pode instalar a ferramenta Vercel, digite `y` e pressione Enter. Essa instalação disponibiliza a ferramenta de publicação.

Siga as instruções de autenticação exibidas no terminal: pode ser necessário abrir um endereço no navegador, confirmar sua conta e autorizar o acesso. Se aparecer um código temporário, use-o somente na página indicada pelo comando.

**Resultado esperado:** o terminal confirma que você entrou na conta. Deixe o comando terminar antes de seguir.

## 8. Criar e vincular o projeto Vercel

Execute:

```powershell
npx.cmd vercel@latest link
```

As perguntas podem aparecer em inglês e variar conforme a versão da ferramenta. Use estas orientações:

| Pergunta ou opção | Resposta para a primeira publicação |
| --- | --- |
| Configurar esta pasta? / `Set up ...?` | `y` |
| Conta ou equipe / `Which scope` ou `Which team` | Selecione sua conta usando as setas e Enter |
| Vincular a projeto existente? / `Link to existing project?` | `n`, se você ainda não criou o projeto |
| Nome / `Project name` ou `Name` | `inventario-rebio`, ou outro nome disponível |
| Diretório do código, se perguntado | `./` — representa a pasta atual |
| Personalizar configurações? / `Customize settings?` | Mantenha os padrões; o projeto já tem configuração Flask |

Se a ferramenta reconhecer um projeto existente, confira o nome antes de aceitar o vínculo. Não selecione outro projeto da sua conta por engano.

**Resultado esperado:** mensagem de vínculo concluído e criação da pasta `.vercel`. Isso conecta o código ao projeto; a publicação será feita na etapa 11. Referência: [vínculo de projetos na Vercel](https://vercel.com/docs/cli/project-linking).

## 9. Gerar a chave de sessão

Essa chave protege as sessões de acesso. Ela **não é** sua senha de login nem a senha do banco.

No terminal, execute:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

**Resultado esperado:** uma sequência de 64 letras e números. Copie somente essa sequência. Na próxima etapa ela será o valor de `REBIO_SECRET_KEY`.

Mantenha a mesma chave nas próximas publicações. Trocar a chave encerra as sessões existentes e obriga os usuários a entrar novamente.

## 10. Cadastrar as configurações no painel Vercel

1. No navegador, abra o painel da Vercel e selecione o projeto vinculado.
2. Abra **Settings** (Configurações).
3. Procure **Environment Variables** (Variáveis de ambiente).
4. Adicione cada linha da tabela abaixo, usando o nome e o valor em campos separados.
5. Selecione **Production** como ambiente de destino e salve.

| Campo de nome / Key | Campo de valor / Value |
| --- | --- |
| `DATABASE_URL` | URL real do Neon, preferencialmente com pooling |
| `REBIO_SECRET_KEY` | Sequência gerada na etapa 9 |
| `REBIO_SECURE_COOKIE` | Apenas o número `1` |

Não acrescente aspas ou o sinal `=` aos valores. Os nomes precisam estar escritos exatamente como na tabela.

Para este roteiro, use **Production**. Se o painel marcar **Preview** ou **Development** também, desmarque esses ambientes. Um futuro ambiente de testes deverá usar banco separado.

Não precisa cadastrar `VERCEL`, `PORT` ou `REBIO_DATABASE`, nem editar `.env.example`. Referência: [configurar variáveis na Vercel](https://vercel.com/docs/environment-variables/managing-environment-variables).

**Resultado esperado:** as três variáveis aparecem na lista do projeto para Production, sem precisar revelar seus valores.

## 11. Publicar o site

Volte ao terminal, ainda na pasta do projeto, e execute:

```powershell
npx.cmd vercel@latest --prod
```

Esse comando envia o código para a Vercel e solicita a publicação em produção. Espere terminar; não feche o terminal durante o processo.

**Resultado esperado:** o processo conclui com sucesso e mostra um endereço HTTPS de publicação. Abra o endereço identificado como **Production** ou o domínio principal do projeto. O link **Inspect**, quando mostrado, abre informações do deployment, não necessariamente a tela do inventário.

Se aparecer **Error** ou **Failed**, a publicação não está concluída. Veja a tabela de problemas abaixo. Referência: [publicação pela ferramenta Vercel](https://vercel.com/docs/cli/deploy).

## 12. Conferir se realmente funcionou

1. Abra o endereço publicado. A tela de login deve aparecer com o visual do projeto.
2. Entre usando o gestor criado na etapa 5.
3. Uma lista vazia é normal: o banco da nuvem é novo.
4. Cadastre um item autorizado para teste, identificando claramente no nome e na descrição que é um teste. Para coordenadas, use somente dados autorizados; não apresente uma localização fictícia como levantamento da REBIO.
5. Confira se o item aparece na lista e no mapa.
6. Edite a descrição e confira o histórico da alteração.
7. Clique em Sair, entre novamente e confira se o cadastro continua presente.
8. Teste a exportação GeoJSON.
9. Exclua apenas o item criado para esse teste, se ele não precisar ser preservado.

Você também pode abrir o endereço do site acrescentando `/health` no final. A resposta deve indicar `ok`, mas esse teste sozinho não comprova o funcionamento do banco: login e cadastro são necessários.

Se aparecer uma página pedindo acesso à própria Vercel antes da tela do inventário, pode ser a proteção do deployment. Confira se abriu o endereço de produção e a configuração **Deployment Protection** do projeto. Essa proteção é diferente do login do sistema.

## Quando alterar o projeto depois

Salve os arquivos no VS Code e publique novamente pela mesma pasta:

```powershell
npx.cmd vercel@latest --prod
```

Não precisa criar outra conta, outro banco ou outro gestor a cada atualização. Se alterar uma variável no painel, publique novamente para que a nova configuração seja utilizada. Não troque `DATABASE_URL` por outro banco esperando que os dados sejam transferidos.

## Se algo der errado

| Mensagem ou situação | Como proceder |
| --- | --- |
| `npx` ou `node` não reconhecido | Instale Node.js com npm, reabra o VS Code e repita a etapa 2 |
| `python.exe` não encontrado | Confira a pasta atual e a existência da `.venv`; veja a etapa 2 |
| Arquivo `setup_cloud.py` ou `requirements.txt` não encontrado | Volte à etapa 1 e abra a pasta correta |
| PowerShell bloqueia um script npm | Use `npx.cmd` e `npm.cmd` exatamente como no guia |
| `EBUSY` ou arquivo `.vsidx` bloqueado dentro de `.vs` | A pasta `.vs` é cache do Visual Studio e está excluída pelo `.vercelignore`. Salve a configuração atualizada e repita a publicação; não é necessário apagar essa pasta |
| `ModuleNotFoundError` | Repita a instalação de dependências da etapa 3 usando o Python da `.venv` |
| Não aparece nada ao digitar senha ou colar a URL | A entrada é oculta; cole/digite e pressione Enter |
| URL ou conexão inválida ao preparar o banco | Atualize os arquivos do projeto e execute novamente `tools/setup_cloud.py`. No Neon, copie a connection string de Connect, não o endereço HTTPS do navegador. O assistente aceita também `psql 'URL'`; a colagem fica oculta |
| Senha curta ou confirmação diferente | Execute novamente o assistente e use uma senha com pelo menos 10 caracteres, igual nas duas entradas |
| `Usuário já existe` | Use o login já criado e sua senha; o assistente não redefine senhas |
| Erro solicitando `DATABASE_URL` ou `REBIO_SECRET_KEY` | Confira a etapa 10, o ambiente Production e publique novamente |
| Erro mencionando `users` ou tabela inexistente | A etapa 5 não foi concluída no mesmo banco configurado na Vercel |
| `Usuário ou senha incorretos` | Use o gestor da etapa 5, respeitando maiúsculas/minúsculas; o usuário local não foi transferido |
| Site sem aparência ou botões sem funcionar | Confira no registro do build se executou `python tools/build_vercel.py`; não configure uma pasta de saída de frontend |
| Erro 413 ao importar | Na Vercel, o limite de arquivo é 4 MiB; reduza o arquivo antes de tentar novamente |
| Erro 413 ao salvar ou exportar | A geometria ou a resposta também pode exceder o limite; reduza coordenadas ou filtre a exportação |
| Mapa não carrega, mas lista aparece | Confira internet e bloqueios ao serviço de mapas; a lista continua disponível |
| Timeout ou erro de conexão com banco | Confira URL, opções TLS e disponibilidade do projeto Neon |

Para localizar o erro de uma publicação, abra o projeto Vercel, entre em **Deployments**, selecione a tentativa e consulte o registro de construção, geralmente chamado **Build Logs**. Para erro ao usar um site já publicado, consulte os logs da aplicação disponíveis no projeto. O nome exato dessas áreas pode mudar.

Se precisar compartilhar uma mensagem de erro para receber ajuda, remova senhas, URL completa do banco e chaves secretas do texto ou da imagem.

## O que fica para a próxima etapa

A preparação foi testada localmente com SQLite, PostgreSQL temporário e navegador. A conta real da Vercel, o banco Neon e o endereço publicado precisam ser verificados após você concluir este roteiro.

A versão Vercel aceita GPX/KML de até 4 MiB; a local mantém 15 MiB. O acervo ainda não possui paginação e exportação por lotes, por isso respostas muito grandes podem atingir os limites da plataforma. Backup do banco deve ser definido no provedor; exportar GeoJSON não guarda contas e histórico completo.

Para detalhes da configuração, limites e referências técnicas, consulte o [guia técnico de publicação](PUBLICAR_VERCEL.md).
