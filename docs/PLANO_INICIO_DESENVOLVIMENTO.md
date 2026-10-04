# Início da próxima etapa de desenvolvimento

Data: 03/10/2026.

## Ponto de partida

A aplicação já possui login, perfis, cadastro, edição, mapa/lista, filtros, importação GPX/KML, exportação GeoJSON, histórico e exclusão. A próxima etapa começa pela consolidação técnica e validação dessa base, orientada pela [especificação reversa](ESPECIFICACAO_FUNCIONAL_REVERSA.md), pela [stack](STACK_TECNOLOGICA_E_FUNDAMENTACAO.md) e pela [modelagem](MODELAGEM_BANCO_DE_DADOS.md).

## Executar no VS Code

Abrir `C:\UNIVESP\PI_II`, selecionar o interpretador `.venv\Scripts\python.exe` e usar o terminal PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app inventario init-db
.\.venv\Scripts\python.exe -m flask --app inventario run --host 127.0.0.1 --port 5000
```

Se a conta ainda não existir, executar uma vez:

```powershell
.\.venv\Scripts\python.exe -m flask --app inventario create-user seu.usuario --role gestor
```

Não recriar uma conta existente. Se o servidor já estiver em execução, reiniciar após atualizar dependências. Acessar `http://127.0.0.1:5000/`.

## Sequência de trabalho

| Prioridade | Trabalho | Critério de conclusão |
| --- | --- | --- |
| 1 | Conciliar RF/RNF completos com comunidade e imagens | Divergências documentadas e decisões confirmadas |
| 2 | Validar fluxos da versão atual e corrigir salvar um registro fora dos filtros ativos | Cadastro/edição apresenta um resultado coerente mesmo quando o item deixa de corresponder à busca |
| 3 | Definir aviso ao sair de um formulário com alterações | Comportamento acordado e verificado por teclado |
| 4 | Organizar commits e remoto do grupo | Código e documentação versionados, sem banco, segredos ou fontes pessoais |
| 5 | Avaliar acessibilidade manual | Login, cadastro, detalhes e exclusão utilizáveis por teclado e leitor de tela |
| 6 | Implantar piloto em nuvem com persistência | Aplicação acessível por HTTPS, banco preservado após reinício |
| 7 | Executar backup e restauração | Banco recuperado em ambiente separado, com integridade verificada |

As prioridades 2 e 3 são pendências identificadas na extração reversa, não mudanças já implementadas por este documento. O provedor e o orçamento da nuvem ainda precisam ser definidos. Upload de fotos, contas pela interface e medições independentes dependem de confirmação de escopo.

## Verificação da base

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Consultar [VALIDACAO.md](VALIDACAO.md) para as evidências existentes e pendências manuais. Testes usam bancos temporários; não executar demonstrações destrutivas sobre o inventário real. A etapa atual entrega as decisões técnicas e a modelagem, preservando a aplicação existente.
