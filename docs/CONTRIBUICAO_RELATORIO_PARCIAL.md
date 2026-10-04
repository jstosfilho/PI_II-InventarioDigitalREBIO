# Contribuição técnica para o relatório parcial

Material para incorporar ao documento organizado por Marisa e revisar com o grupo. Não substitui o modelo oficial da UNIVESP. Data de referência: 03/10/2026.

## Atualização após receber as imagens do Figma

A interface foi adaptada às seis capturas disponibilizadas pelo grupo, incluindo login em duas colunas, lista lateral, mapa à direita e navegação lateral entre cadastro, edição e detalhes. Foram acrescentados link externo das fotos, importação de arquivos GPX/KML, preservação de segmentos geográficos separados, estimativa de extensão das trilhas e confirmação de exclusão permanente pelo gestor. Os dados complementares do levantamento e o histórico permanecem acessíveis em áreas recolhidas.

A suíte ampliada executou 27 testes com sucesso. A verificação da interface em navegador isolado concluiu os fluxos de login, cadastro, edição, importação e exclusão com dados fictícios, sem erros JavaScript; também verificou apresentação em celular. O banco existente recebe migração aditiva com backup. Esses resultados não substituem a validação da comunidade ou a conciliação com o documento RF/RNF completo.

## Desenvolvimento da solução inicial

A solução inicial consiste em uma aplicação web de inventário digital destinada ao cadastro e à visualização de trilhas e nascentes da Reserva Biológica do Alto da Serra de Paranapiacaba. O recorte foi definido a partir da demanda descrita no plano de ação revisado, após a reunião com a comunidade externa em 09/09/2026. A proposta concentra-se na organização e preservação de dados fornecidos pela equipe da reserva ou por pesquisadores autorizados, sem atribuir ao grupo o levantamento físico do território.

Foi desenvolvida uma primeira versão funcional utilizando o framework Flask, com interface em HTML, CSS e JavaScript e persistência em SQLite. A escolha dessa arquitetura buscou reduzir a complexidade de preparação do ambiente e permitir a demonstração de um fluxo completo entre navegador, API e banco. As requisições JavaScript consultam e atualizam dados por endpoints autenticados. A representação cartográfica utiliza Leaflet e imagens do OpenStreetMap.

## Modelagem dos dados

O modelo inicial possui três entidades: usuários, registros geográficos e histórico de alterações. Usuários armazenam identificação da conta, hash de senha e perfil de acesso. Registros geográficos reúnem nome, tipo, descrição, situação de conservação, geometria, origem do levantamento, data de observação e metadados de autoria. Nascentes são pontos e trilhas são linhas conforme o padrão GeoJSON, com coordenadas na ordem longitude e latitude.

O histórico conserva versões após operações de criação, edição e arquivamento. Cada alteração identifica usuário responsável e momento da operação. O arquivamento preserva o acervo, retirando o registro das consultas correntes. Um número de versão evita que edições simultâneas sobrescrevam silenciosamente os dados.

## Funcionalidades da primeira versão

A aplicação permite autenticação, consulta por perfil, cadastro e edição de trilhas e nascentes, filtragem por texto, tipo e situação, visualização em mapa e lista, consulta de histórico e exportação GeoJSON. Os indicadores apresentam totais dos registros filtrados, incluindo trilhas, nascentes e itens que requerem atenção. A validação no servidor verifica campos obrigatórios, tipo de geometria, limites de latitude e longitude, data da observação e pelo menos dois pontos distintos para uma trilha.

## Acessibilidade e segurança inicial

A interface contém idioma declarado, rótulos associados aos campos, link para acesso direto ao conteúdo, indicação de foco e mensagens de estado. A lista disponibiliza os dados geográficos sem exigir interação com o mapa. Essas medidas constituem uma base para avaliação de acessibilidade, que ainda deve incluir testes com teclado e leitor de tela.

O inventário exige autenticação. A versão inicial diferencia gestor, editor e leitor, utiliza hash de senha e proteção CSRF nas alterações autenticadas. Os dados enviados pelo usuário são apresentados como texto na interface. Antes da publicação externa, serão necessários controles adicionais, incluindo limitação de tentativas de login, HTTPS e definição das regras de acesso com a comunidade.

## Verificação e próximas etapas

Foram preparados testes de integração com banco temporário para autenticação, autorização, criação, edição, arquivamento, validação de geometria, filtros, exportação, persistência e histórico. Os resultados efetivamente obtidos constam de `docs/VALIDACAO.md` e devem ser conferidos antes de incluir no relatório entregue.

A estrutura inclui Dockerfile e execução com Waitress para apoiar futura implantação em nuvem. A implantação não foi realizada; portanto, ainda não há evidência de disponibilidade remota ou restauração em nuvem. As próximas etapas são conciliar a implementação com os RF/RNF e telas do grupo, completar funcionalidades prioritárias, implantar com persistência e backup e colher feedback específico da REBIO sobre o protótipo.

## Evidências a inserir pelo grupo

Incluir ata original, registro da aceitação do novo escopo, telas oficiais, retorno efetivo da comunidade e resultados dos testes executados. A visita prevista para 02/10 e a avaliação do protótipo não foram comprovadas nos arquivos locais. Não apresentar essas atividades como realizadas sem registros.

## Referências técnicas para normalização

PALLETS. Flask Documentation. Disponível em: https://flask.palletsprojects.com/en/stable/. Acesso em: 3 out. 2026.

PALLETS. Waitress. Disponível em: https://flask.palletsprojects.com/en/stable/deploying/waitress/. Acesso em: 3 out. 2026.

LEAFLET. API Reference, versão 1.9.4. Disponível em: https://leafletjs.com/reference.html. Acesso em: 3 out. 2026.

OPENSTREETMAP FOUNDATION. Tile Usage Policy. Disponível em: https://operations.osmfoundation.org/policies/tiles/. Acesso em: 3 out. 2026.

Acrescentar referências da UNIVESP com autoria, ano e dados completos do AVA. Os arquivos locais de slides não fornecem todos os elementos bibliográficos para uma referência definitiva.
