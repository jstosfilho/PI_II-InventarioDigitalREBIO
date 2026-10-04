# Material técnico para compartilhar com o grupo

## Texto sugerido para a apresentação do MVP

O MVP proposto utiliza Flask no backend, HTML/CSS e JavaScript na interface e SQLite como banco inicial. O modelo reúne usuários, trilhas/nascentes e histórico de alterações. As nascentes são pontos e as trilhas são percursos em GeoJSON. A primeira versão permite login, cadastro, edição, filtros, mapa, exportação e histórico. Treze testes automatizados foram aprovados. A implantação em nuvem foi planejada, mas ainda não foi realizada.

Para fecharmos o escopo com José e Wagner, precisamos conciliar a base com os RF/RNF e o Figma, especialmente fotos, permissões e forma de inserir o percurso das trilhas. Para o relatório de Marisa, o texto técnico detalhado está em `CONTRIBUICAO_RELATORIO_PARCIAL.md`. A proposta não substitui o levantamento de campo pela equipe da REBIO.

## Sequência sugerida para Canva ou reunião

1. Problema: ausência de inventário georreferenciado consolidado e necessidade de preservar o acervo.
2. Solução: cadastro, consulta e visualização de trilhas e nascentes.
3. Fluxo: entrar → cadastrar → consultar mapa/lista → atualizar → consultar histórico → exportar.
4. Arquitetura: navegador com JavaScript → API Flask → SQLite; Leaflet para visualização.
5. Banco: usuários → registros geográficos → histórico, com autoria e versões.
6. Evidências: 13 testes aprovados; registro das pendências sem confundir planejamento e execução.
7. Próximos passos: conciliar requisitos/telas, priorizar fotos, implantar e validar com a REBIO.

Este material foi salvo localmente; não foi enviado ao grupo, ao Drive ou ao Canva.
