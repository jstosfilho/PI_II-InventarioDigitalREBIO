# Ajustes do Figma — 03/10/2026

## Implementação

- Login dividido em painel verde de identificação (58,3%) e formulário branco (41,7%), conforme a captura.
- Cabeçalho compacto REBIO ASP e Inventário Digital; painel esquerdo de 500 px e mapa no restante da tela desktop.
- Lista de cartões com categoria, estado Ativo, nome e descrição; total no rodapé.
- Navegação lateral entre lista, detalhes, novo cadastro e edição, mantendo o mapa visível.
- Formulários com nome, categoria do recurso, descrição, link das fotos e abas GPX/KML e Coordenadas.
- Link HTTPS das fotos persistido e exibido nos detalhes. É uma referência externa; fotos não são enviadas ao servidor.
- Importação de track, route e waypoint GPX; Point e LineString KML. Vários segmentos de trilha são preservados como MultiLineString.
- Arquivo de até 15 MiB, XML sem DTD/entidades externas e validação de coordenadas. O servidor persiste geometria e nome do arquivo, sem armazenar o XML original.
- Extensão geodésica aproximada em metros, somando apenas segmentos reais. Não equivale a medição topográfica nem certifica o levantamento.
- Exclusão permanente com diálogo equivalente ao Figma, verificação de versão e permissão exclusiva do gestor. Exclui também o histórico do registro. O arquivamento anterior continua disponível na API.
- Origem, data, conservação, classificação de uso, filtros, exportação e histórico em áreas secundárias, preservando o desenho principal.
- Seleção de um registro destaca sua geometria e enquadra o mapa; formulário apresenta prévia da geometria.
- Em celular, painel e mapa ficam empilhados. As abas permitem navegação por setas do teclado.

## Migração

Ao iniciar a aplicação atualizada, bancos existentes recebem `photo_url`, `category` e `geometry_file` com valores vazios. Contas, senhas, registros e histórico permanecem. Uma cópia `.pre-figma.bak` é criada ao lado do banco antes da primeira migração.

Reiniciar o servidor no VS Code após atualizar os arquivos e recarregar o navegador. A nova dependência `defusedxml` está em `requirements.txt`.

## Decisões diante das ambiguidades das imagens

Categoria principal permanece Trilha/Nascente. “Rota de Pesquisa” é classificação de uso opcional nos dados complementares e pode ser exibida nos detalhes.

O mapa usa OpenStreetMap, com atribuição, portanto a cartografia difere da imagem do protótipo. Os nomes e coordenadas das capturas não foram inseridos no banco do usuário. Dados demonstrativos existem somente no servidor isolado de revisão visual.

A tela distingue exclusão permanente de arquivamento. Cancelar ou fechar o diálogo não altera dados; nenhuma exclusão é realizada automaticamente.

## Limitações

Um arquivo corresponde a um registro: nascentes exigem um ponto; trilhas aceitam um ou mais segmentos. GPX com trilhas utiliza track/route; waypoints adicionais não são incorporados ao percurso. KML utiliza Point/LineString; polígonos e arquivos KMZ não são suportados. Geometrias com altitude são reduzidas a longitude/latitude para exibição.

Até 100.000 coordenadas por registro, sujeito ao limite de 8 MiB para requisição JSON de cadastro/edição. Upload de arquivo recebe até 16 MiB de requisição multipart para comportar o arquivo de 15 MiB; outros endpoints mantêm limites menores.

Ainda faltam confirmação dos RF/RNF completos e avaliação pela REBIO. Sem essas evidências, a aproximação às imagens não representa homologação pela comunidade.
