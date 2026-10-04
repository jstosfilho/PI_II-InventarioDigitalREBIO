# Análise e plano do MVP

Data de referência: 03/10/2026. Base documental: pasta `Dados do PI_II`.

## Conclusão

O projeto vigente é uma plataforma de inventário digital de trilhas e nascentes, e não um sistema de check-in turístico. Essa escolha consta do plano de ação revisado e da mensagem de 30/09 às 11h03 no histórico. O grupo deve concentrar a entrega parcial na definição do problema, proposta inicial, arquitetura, modelagem e evidências da interação com a comunidade.

## Contexto e evidências

| Evidência local | Consequência para o projeto |
| --- | --- |
| `Grupo - Contexto.txt`, 25/08 | Proposta original para o PEXJ: check-in e segurança de visitantes. |
| Histórico, 03/09 | PEXJ recusou a parceria e indicou a REBIO. |
| Plano de ação revisado; histórico, 29/09 | A reunião de 09/09 identificou demanda por mapeamento de trilhas e nascentes; visitação turística não era pertinente. |
| Plano de ação revisado | Relata perda de documentação em enchentes e necessidade de consolidar dados para apoiar a gestão. Informação atribuída ao relato local, sem verificação externa independente. |
| Histórico, 30/09 às 11h03 | José relata aceitação da proposta de inventário digital pela REBIO. |
| Histórico, 30/09 às 22h34 | Corrige prazo parcial para 30/09 com carência até 04/10. Confirmar prazo no AVA. |
| Histórico, 01/10 e 02/10 | RF/RNF e protótipo Figma foram produzidos por José, mas não estão anexados localmente. |

O plano revisado é mais atual que a proposta original. Mensagens que sugeriram plataforma de pesquisadores ou projeto de perfumaria não representam a decisão final. Imagens ocultadas no histórico não podem ser tratadas como evidência visual disponível.

## Problema e objetivo

Problema do plano: como uma aplicação web em nuvem pode estruturar dados de trilhas e nascentes, apoiar o monitoramento, reduzir a perda de acervo e fornecer um inventário para a gestão?

Objetivo: desenvolver uma plataforma para cadastrar, armazenar e visualizar dados georreferenciados da REBIO do Alto da Serra de Paranapiacaba. A solução oferece infraestrutura digital; a obtenção e verificação das coordenadas cabem à equipe da reserva e aos pesquisadores autorizados.

## Relação com as referências

- Q1/apresentação e desenvolvimento web: definem framework web, banco, JavaScript, nuvem, API, acessibilidade, versionamento e testes; análise de dados é opcional.
- Q1/metodologia e Design Thinking: orientam aproximação à comunidade, entendimento do problema e iteração da proposta.
- Q2/delimitação: orienta fundamentar o problema nas falas e observações da comunidade, evitando construir uma solução sem demanda identificada.
- Q2/JavaScript: fundamenta interação no navegador; aqui usada em formulários, filtros, requisições à API e mapa.
- Q3/nuvem: fundamenta a proposta de acesso remoto e armazenamento; a implantação efetiva ainda é uma etapa futura.
- Q4/acessibilidade: orienta rótulos, conteúdo semântico e alternativas de consulta; a lista oferece acesso aos dados exibidos no mapa.
- Q4/protótipos: orienta construir uma solução simples para responder perguntas e colher feedback.

Os livros e links em `Referencias.txt` são uma bibliografia inicial. Não afirmar leitura dos capítulos dos livros, pois seus textos não foram fornecidos. A referência técnica consultada foi a documentação oficial do Flask, Leaflet e Waitress indicada no README. O documento RF/RNF retornou 404 no conector Drive e o Figma não pôde ser lido; suas funcionalidades específicas não foram presumidas como requisitos confirmados.

## Requisitos propostos, sujeitos à conciliação com José

| ID local | Entrega | Critério de aceite | Situação |
| --- | --- | --- | --- |
| P01 | Acesso por perfil | Leitor consulta; editor cadastra/edita; gestor também arquiva. | Implementado |
| P02 | Cadastro | Nome, tipo, situação, descrição, origem, data e geometria válidos persistem. | Implementado |
| P03 | Georreferenciamento | Nascente como ponto e trilha como linha; longitude/latitude validadas. | Implementado |
| P04 | Mapa e lista | Registros aparecem nos dois modos, sem exigir uso do mapa para consultar. | Implementado; validação visual pendente |
| P05 | Busca e indicadores | Filtros aplicados igualmente à lista, mapa, totais e exportação. | Implementado |
| P06 | Preservação do histórico | Cada criação, edição e arquivamento guarda autor, data e snapshot. | Implementado |
| P07 | API | JavaScript consome endpoints autenticados; saída GeoJSON. | Implementado |
| P08 | Nuvem | Aplicação acessível via HTTPS, volume persistente e restauração testada. | Preparação feita; implantação pendente |
| P09 | Fotografias | Fotos vinculadas ao registro com autoria e armazenamento. | Mencionado na proposta; backlog desta versão |

Estes identificadores são locais e não substituem os RF/RNF originais. Não divulgar localizações em página pública sem definir com a REBIO o público autorizado. Nesta versão, todos os dados do inventário exigem login.

## Arquitetura e decisões

Flask e Jinja no backend; HTML/CSS semântico e JavaScript no frontend; SQLite com integridade referencial no piloto; Leaflet para representar GeoJSON. É uma arquitetura pequena e executável sem infraestrutura paga. A decisão de Flask é proposta técnica, não acordo previamente registrado entre Jorge e Wagner.

SQLite permite persistência local e piloto em uma instância de nuvem com volume. PostgreSQL/PostGIS é evolução para maior concorrência e consultas espaciais; não existe integração PostgreSQL implementada nesta entrega. A API da própria aplicação é usada efetivamente pelo frontend; confirmar com o orientador se é exigida uma API externa de dados além dessa integração e do serviço cartográfico.

## Matriz acadêmica

| Exigência | Evidência concreta | Pendência |
| --- | --- | --- |
| Framework web | `inventario/__init__.py`, Flask | Conciliar stack com equipe |
| Banco de dados | `schema.sql`, SQLite persistente | Política de backup operacional |
| JavaScript | `static/app.js`, fetch e Leaflet | Revisão com protótipo |
| API | `/api/features`, `/api/geojson`, sessões | Confirmar interpretação acadêmica |
| Nuvem | Dockerfile, Waitress, plano de implantação | Publicar, HTTPS, volume e evidência real |
| Acessibilidade | Idioma, labels, foco, link de salto, lista, diálogos | Teclado, leitor de tela e auditoria manual |
| Controle de versão | Estrutura pronta para Git; verificação em VALIDACAO | Remote e revisão entre colegas |
| Testes | Testes de API com banco isolado | Usabilidade e validação externa |

## Plano de trabalho sugerido

| Etapa | Prazo proposto | Responsabilidade no contexto | Entrega |
| --- | --- | --- | --- |
| Relatório parcial | 03–04/10 | Marisa integra; Jorge/Wagner fornecem seção técnica; José revisa e submete | Problema, proposta, arquitetura, fontes e evidências reais |
| Conciliação dos RF/RNF e Figma | 05–06/10 | José, Jorge e Wagner | Escopo fechado, telas conferidas e backlog priorizado |
| Completar MVP | 07–12/10 | Jorge e Wagner | Fotos se prioritárias, melhorias de geometria e ajustes validados |
| Nuvem e testes | 13–17/10 | Jorge e Wagner; revisão do grupo | HTTPS, persistência, backup e resultados registrados |
| Validação na REBIO | 18–20/10, a combinar | José coordena; equipe participa | Tarefas reais e feedback documentado |
| Refinamento e relatório final | 21–24/10, a confirmar no AVA | Grupo | Correções, relatório e roteiro de vídeo |

Datas após 04/10 são proposta de organização, não prazos oficiais. Responsabilidades técnicas e do relatório seguem as mensagens; não foi inferida nova obrigação para Esdras.

## Informações ainda necessárias

Documento completo RF/RNF, telas Figma, ata da reunião de 09/09, retorno específico da comunidade sobre o protótipo, confirmação de realização da visita prevista para 02/10, dados geográficos autorizados e modelo oficial de relatório. O histórico não comprova que a visita ou a validação do protótipo ocorreu. Não preencher resultados ou depoimentos fictícios.
