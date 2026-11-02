# Inventário Digital REBIO

Primeira versão funcional do Projeto Integrador em Computação II da UNIVESP: cadastro e visualização de trilhas e nascentes da REBIO do Alto da Serra de Paranapiacaba.

O escopo segue o plano de ação local e o histórico até 02/10/2026. A interface foi ajustada às seis imagens do Figma adicionadas à pasta de dados em 03/10. O documento RF/RNF e o arquivo navegável ainda precisam ser conciliados. Não há dados reais ou coordenadas da reserva pré-carregados.

## Executar no Windows

Python 3.12 ou superior. Nesta pasta, o ambiente `.venv` já foi preparado durante o desenvolvimento.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app inventario init-db
.\.venv\Scripts\python.exe -m flask --app inventario create-user seu.usuario --role gestor
.\.venv\Scripts\python.exe -m flask --app inventario run --host 127.0.0.1 --port 5000
```

O comando `create-user` pede uma senha de pelo menos 10 caracteres; não há senha padrão. Abra http://127.0.0.1:5000. Para criar outros perfis, use `--role editor` ou `--role leitor`. Não é necessário ativar o ambiente virtual. O banco é criado em `instance/inventario.sqlite3`. Nunca coloque banco, senhas ou dados ambientais reais no Git. As fontes originais e os textos extraídos, que contêm dados pessoais do grupo, também estão excluídos pelo `.gitignore`.

## Executar no Linux

Python 3.12 ou superior (no Debian/Ubuntu, `sudo apt install python3-venv`).

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m flask --app inventario init-db
.venv/bin/python -m flask --app inventario create-user seu.usuario --role gestor
.venv/bin/python -m flask --app inventario run --host 127.0.0.1 --port 5000
```

Testes: `.venv/bin/python -m unittest discover -s tests -v`.

## Executar com Docker Compose

```bash
export REBIO_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
docker compose up -d --build
docker compose exec web python -m flask --app inventario init-db
docker compose exec web python -m flask --app inventario create-user seu.usuario --role gestor
```

Abra http://localhost:8080. O banco fica no volume `rebio-data`. Para persistir a chave, coloque `REBIO_SECRET_KEY=...` em um arquivo `.env` (já ignorado pelo Git). Atrás de HTTPS, altere `REBIO_SECURE_COOKIE` para `"1"`.

## Funcionalidades

- Login e perfis gestor, editor e leitor.
- Cadastro e edição de nascentes (`Point`) e trilhas (`LineString`).
- Validação de campos, data e coordenadas em WGS84, na ordem **longitude, latitude**.
- Mapa Leaflet/OpenStreetMap, lista equivalente, filtros e indicadores sobre os resultados filtrados.
- Exportação GeoJSON autenticada e histórico de versões.
- Arquivamento pelo gestor, preservando o histórico; proteção contra edição concorrente.
- Painéis laterais de detalhes, cadastro e edição conforme o Figma.
- Link HTTPS de fotos, importação GPX/KML de até 15 MiB e extensão aproximada das trilhas.
- Exclusão permanente pelo gestor com confirmação, removendo também o histórico do registro.
- Sessões, senhas com hash e proteção CSRF nas mutações autenticadas.

O mapa exige internet para carregar Leaflet e as imagens do OpenStreetMap. A lista e o cadastro funcionam mesmo quando a biblioteca do mapa não carrega. As coordenadas inseridas precisam vir da REBIO ou de pesquisadores autorizados; o sistema não faz levantamento topográfico.

## Testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes utilizam bancos temporários e dados fictícios. Consulte [validação](docs/VALIDACAO.md) para evidências e verificações manuais pendentes.

## Documentação

- [Stack tecnológica e fundamentação](docs/STACK_TECNOLOGICA_E_FUNDAMENTACAO.md)
- [Modelagem conceitual, lógica e física do banco](docs/MODELAGEM_BANCO_DE_DADOS.md)
- [Início da próxima etapa no VS Code](docs/PLANO_INICIO_DESENVOLVIMENTO.md)
- [Análise das fontes e decisões](docs/ANALISE_E_PLANO_MVP.md)
- [Banco e API](docs/BANCO_E_API.md)
- [Texto técnico para o relatório parcial](docs/CONTRIBUICAO_RELATORIO_PARCIAL.md)
- [Implantação em nuvem e backup](docs/IMPLANTACAO.md)
- [Roteiro de validação com a comunidade](docs/VALIDACAO.md)
- [Ajustes realizados a partir do Figma](docs/AJUSTES_FIGMA.md)

## Limites desta entrega

Fotos são acessadas por link externo, como nas imagens do Figma; não há upload de imagens para o servidor. GPX/KML são convertidos em geometria; o XML original não é guardado. Desenho pelo mapa e gestão de contas na interface permanecem no backlog. O monitoramento registra situação e histórico, sem observações independentes ou séries temporais. Não foi feita implantação em nuvem. A conformidade integral de acessibilidade exige avaliação manual com leitor de tela. Confirmar o escopo contra os RF/RNF completos.

Para bancos existentes, a aplicação faz migração aditiva e backup `.pre-figma.bak` ao reiniciar. Depois dos ajustes, execute `python -m pip install -r requirements.txt` no ambiente virtual, reinicie o servidor e recarregue o navegador com Ctrl+F5.

## Referências técnicas

- [Flask](https://flask.palletsprojects.com/en/stable/)
- [Waitress com Flask](https://flask.palletsprojects.com/en/stable/deploying/waitress/)
- [Leaflet 1.9.4](https://leafletjs.com/reference.html)
- [Política de uso dos mapas OpenStreetMap](https://operations.osmfoundation.org/policies/tiles/)

As fontes acadêmicas originais permanecem em `Dados do PI_II`; textos extraídos para análise estão em `analise/fontes_extraidas`.
- [Especificação funcional reversa](docs/ESPECIFICACAO_FUNCIONAL_REVERSA.md)
