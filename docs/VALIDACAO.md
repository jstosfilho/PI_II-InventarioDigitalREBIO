# Evidências de verificação e roteiro de validação

Data: 03/10/2026.

## Atualização após ajustes do Figma

Correção posterior do bloqueio de tiles: o cabeçalho foi alterado de `same-origin` para `strict-origin-when-cross-origin`. O teste HTTP do cabeçalho passou, e a verificação em Edge headless confirmou envio de `Referer: http://127.0.0.1:5051/` nos pedidos de tiles. Nesta execução, todos os tiles foram interceptados e simulados; nenhum acesso foi feito ao OpenStreetMap. Os demais fluxos da interface também passaram. A disponibilidade do serviço na rede do usuário deve ser confirmada após reiniciar o servidor.

Suíte ampliada: **27 testes aprovados**, em 26,873 segundos. Além dos casos da primeira versão, valida links HTTPS, classificação, importação autenticada, exclusão permanente, migração de banco existente, GPX/KML, limites de tamanho, XML inseguro e preservação de segmentos separados.

Verificação da interface realizada com Playwright e Edge headless, em servidor isolado na porta 5051 e banco fictício em `tmp/figma-qa`. Fluxos aprovados: login, lista, detalhes, edição, cancelamento de exclusão, importação GPX, cadastro de trilha, exclusão de registro de teste, cadastro de nascente por coordenadas e apresentação em 390 px. Sem erros JavaScript ou rolagem horizontal indevida. Foram produzidas e inspecionadas sete capturas de desktop e celular.

Os testes e as capturas não validam o documento RF/RNF completo, o leitor de tela ou a aceitação pela comunidade. O mapa usa cartografia OpenStreetMap, distinta da referência. Dados fictícios de revisão não foram inseridos no banco principal.

## Verificações executadas

Comando: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`.

Resultado final: **13 testes executados, todos aprovados**, em 22,956 segundos, em Python 3.12 no Windows. Bancos temporários e coordenadas fictícias; nenhum dado real da reserva foi utilizado.

| Verificação automatizada | Resultado |
| --- | --- |
| Autenticação, credenciais inválidas e logout | Aprovado |
| Proteção CSRF em criação e logout | Aprovado |
| Criação, edição, arquivamento e histórico preservado | Aprovado |
| Edição concorrente rejeitada sem sobrescrever dados | Aprovado |
| Perfis de leitor, editor e gestor | Aprovado |
| Coordenadas fora dos limites ou inválidas | Aprovado |
| Trilhas e ordem longitude/latitude na exportação | Aprovado |
| Trilhas sem percurso válido rejeitadas | Aprovado |
| Filtros com resultados equivalentes em lista e exportação | Aprovado |
| Campos obrigatórios, enumerações, datas e JSON inválido | Aprovado |
| Dados disponíveis após recriar a aplicação | Aprovado |
| Inicialização do banco preserva registros existentes | Aprovado |
| Página HTML e arquivos estáticos disponíveis | Aprovado |

Também foi executado `node --check inventario/static/app.js`, com sucesso. O banco local vazio foi inicializado pelo comando `flask --app inventario init-db`.

A execução inicial identificou uma conexão aberta na preparação dos testes, impedindo a exclusão de arquivos temporários no Windows. Foi corrigido o fechamento explícito da conexão e das respostas de arquivos estáticos, e a suíte completa foi executada novamente com sucesso.

O executor do sandbox apresentou erro de preparação após a inicialização do Git; as verificações finais foram executadas com autorização fora do sandbox. O Git foi inicializado, mas a leitura pelo usuário do host acusou diferença de proprietário. Não foi alterada a configuração global de segurança do Git.

## Limites das evidências

Na primeira versão, não houve teste visual de navegador. Após receber as imagens, essa verificação foi realizada conforme a atualização acima. Continuam pendentes leitor de tela, publicação em nuvem, teste de Docker, restauração operacional de backup e validação com a comunidade. Testes HTTP não comprovam que os tiles carregam na rede do usuário. Não afirmar conformidade integral WCAG a partir destas verificações.

## Roteiro de revisão do grupo

1. Criar um gestor pelo comando documentado no README e entrar no sistema.
2. Cadastrar uma nascente fictícia marcada como demonstração, com origem e data.
3. Cadastrar uma trilha com dois ou mais pontos distintos e conferir o percurso.
4. Testar nome, tipo e situação nos filtros; comparar mapa, lista e totais.
5. Editar um registro, verificar histórico e exportar GeoJSON.
6. Entrar como leitor e confirmar consulta sem edição; como editor, confirmar edição sem arquivamento.
7. Testar teclado, foco em diálogos, Escape, link de salto e leitura dos rótulos. Conferir 320 px de largura e zoom de 200%.
8. Bloquear o carregamento do Leaflet e confirmar que cadastro e lista continuam utilizáveis.
9. Comparar campos e fluxos com o documento RF/RNF e as telas do Figma.

## Validação com a REBIO

Solicitar que um participante execute, com dados autorizados, as tarefas de localizar um registro, cadastrar um recurso, atualizar sua situação e consultar seu histórico. Registrar dificuldade, tempo aproximado, campos ausentes e sugestões, sem induzir respostas.

Perguntas centrais: os campos representam o levantamento realizado? As coordenadas são pontos isolados ou percursos completos? Quem pode cadastrar, editar e consultar? Fotos são indispensáveis à primeira entrega? Há informação cuja localização deve ter acesso mais restrito? A lista e o mapa permitem localizar o que a equipe precisa?

| Registro do encontro | Preenchimento após validação |
| --- | --- |
| Data e modalidade | A registrar |
| Participante e função | A registrar |
| Versão demonstrada | A registrar |
| Tarefa e resultado observado | A registrar |
| Comentário específico da comunidade | A registrar |
| Ajuste acordado e prioridade | A registrar |

Não usar a aceitação do tema como se fosse aprovação do software. A aprovação do escopo e o feedback sobre o protótipo são evidências diferentes.
