# Comparação da implementação com as imagens do Figma

Análise em 03/10/2026. Fonte: seis imagens de `Dados do PI_II/imagens figma.zip`, extraídas em `Dados do PI_II/figma_extraido`. As imagens estão disponíveis localmente; o arquivo Figma navegável e o documento RF/RNF continuam sem leitura confirmada. Esta análise complementa as pendências registradas na primeira entrega.

## Telas identificadas

| Imagem (horário e sufixo) | Tela | Elementos observados |
| --- | --- | --- |
| 14.38.18, sem sufixo | Login | Painel verde à esquerda com nome da REBIO e descrição; formulário branco à direita, título Bem-vindo, login, senha e Entrar. |
| 14.38.18 (1) | Inventário | Cabeçalho REBIO ASP, lista de registros à esquerda, Novo Cadastro, total no rodapé e mapa amplo à direita. |
| 14.38.19, sem sufixo | Editar cadastro | Nome, categoria, descrição, link das fotos e abas GPX/KML ou Coordenadas. Arquivo geográfico previamente associado; botão Salvar. |
| 14.38.19 (1) | Novo cadastro | Estrutura igual à edição; seletor de arquivo .gpx ou .kml com indicação de limite de 15 MB. |
| 14.38.20, sem sufixo | Detalhes | Nome, categoria, descrição, extensão/geometria, link de fotos no Drive e botões Excluir e Editar. |
| 14.38.20 (1) | Confirmar exclusão | Modal com nome do registro, aviso de remoção permanente, Cancelar e Sim, excluir. |

## Diferenças em relação à versão atual

| Aspecto | Referência visual | Implementação atual | Ajuste identificado |
| --- | --- | --- | --- |
| Login | Duas colunas, identidade verde à esquerda | Cartão central com cabeçalho | Reorganizar HTML/CSS e comportamento móvel. |
| Área principal | Lista lateral e mapa ocupando a área restante | Indicadores, filtros, mapa e cartões em sequência vertical | Adotar estrutura lateral, sem perder filtros e acessibilidade. |
| Navegação | Lista → detalhes → edição na lateral, mapa permanece | Edição e histórico em diálogos | Criar estados de navegação no painel lateral. |
| Fotografias | Link para pasta no Drive | Campo ausente | Acrescentar URL validada no banco, API, formulário e detalhes. Upload de fotos para o servidor não aparece nessas imagens. |
| Dados geográficos | Arquivo GPX/KML ou coordenadas | Coordenadas manuais em GeoJSON | Acrescentar importação e parser; manter alternativa manual. |
| Tamanho do arquivo | Indicação de 15 MB | Limite global de requisição de 256 KiB | Definir endpoint de upload e limites coerentes, sem ampliar indiscriminadamente todas as requisições. |
| Extensão | Comprimento da trilha em metros | Sem cálculo | Calcular extensão geodésica a partir da geometria e exibir unidade; definir apresentação para nascentes. |
| Exclusão | Remoção permanente com confirmação própria | Arquivamento preservando histórico, com confirmação do navegador | Conciliar política de exclusão com os RF/RNF e a preservação do acervo. Não trocar silenciosamente o significado da ação. |
| Situação | Exemplos marcados Ativo | Situação de conservação e sinalizador de arquivamento | Separar estado do cadastro de condição de conservação. |

## Pontos que as imagens não resolvem

- Categoria aparece como Trilha na edição e como Rota de Pesquisa nos detalhes. Confirmar se são tipo do recurso e classificação de uso distintos, ou textos inconsistentes do protótipo.
- A aba Coordenadas não foi capturada aberta; quantidade de campos, inclusão de múltiplos pontos e seleção pelo mapa não estão especificadas visualmente.
- Não há trilhas ou nascentes desenhadas no mapa dessas capturas; geometria, tooltip, seleção e destaque ainda precisam ser definidos.
- Os exemplos de nomes, descrição, extensão e total são conteúdo de protótipo, não dados de campo verificados.
- As imagens não definem perfis de acesso, origem e data do levantamento, histórico, backup, filtros, exportação ou estados de erro. Não remover controles existentes com base apenas na ausência visual.
- Não há versão móvel nas imagens. A adaptação precisa manter mapa e lista utilizáveis em telas pequenas, com rótulos e navegação por teclado.
- GPX pode conter múltiplos segmentos e KML múltiplas geometrias. Definir os formatos aceitos e como preservar segmentos sem ligar artificialmente partes desconectadas.

## Ordem sugerida de implementação

1. Ajustar login, cabeçalho e disposição de lista/mapa, preservando autenticação e funcionalidades atuais.
2. Implementar painel de detalhes e edição lateral com navegação Voltar e seleção do registro no mapa.
3. Adicionar link das fotos com validação de URL e extensão calculada das trilhas.
4. Adicionar importação GPX/KML com validação de conteúdo, geometria, segmentos e limite de tamanho; criar testes para arquivos inválidos.
5. Conciliar categoria, estado do cadastro e exclusão com o documento RF/RNF; só então fechar os comportamentos correspondentes.
6. Verificar desktop, celular, teclado e leitor de tela, e coletar feedback específico da REBIO.

Nesta etapa foram inspecionadas as imagens e documentadas as diferenças. O código da aplicação não foi alterado por esta análise.
