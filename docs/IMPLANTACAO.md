# Implantação e preservação do acervo

## Situação

Aplicação local implementada. Dockerfile e execução Waitress preparados, mas não executados/validados em nuvem nesta sessão. Escolher uma infraestrutura com **uma instância e volume persistente**; SQLite não serve para múltiplas réplicas com arquivos independentes.

## Preparar a instância

1. Construir a imagem com `docker build -t inventario-rebio .`.
2. Criar volume persistente para `/data`.
3. Configurar `REBIO_SECRET_KEY` com segredo forte, `REBIO_DATABASE=/data/inventario.sqlite3`, `REBIO_SECURE_COOKIE=1` e `PORT=8080`.
4. Inicializar o banco no mesmo volume: `python -m flask --app inventario init-db`.
5. Criar o gestor pelo terminal seguro: `python -m flask --app inventario create-user gestor --role gestor`; informar senha sem a colocar no código ou histórico de comandos.
6. Executar `python serve.py` atrás do proxy HTTPS da plataforma.
7. Confirmar `/health`, login, criação de item fictício identificado como teste, persistência após reinício e acesso restrito aos endpoints.

`.env.example` contém exemplos; o programa lê variáveis de ambiente e não carrega `.env` automaticamente. O contêiner usa usuário sem privilégios. Verificar permissões do volume na plataforma escolhida. No Windows local sem HTTPS, deixar `REBIO_SECURE_COOKIE` ausente.

O centro inicial do mapa é uma aproximação para navegação, não o limite oficial da unidade. O serviço público de tiles do OpenStreetMap exige atribuição; reavaliar o provedor conforme a [política de uso](https://operations.osmfoundation.org/policies/tiles/) antes de ampliar tráfego. Não implementar downloads em massa ou mapas offline sobre esse serviço.

O cabeçalho da aplicação usa `Referrer-Policy: strict-origin-when-cross-origin`, permitindo enviar apenas a origem da página para identificar os pedidos de tiles. Não alterar para `same-origin` ou `no-referrer`, pois isso elimina o Referer exigido pelo serviço. Os testes automáticos interceptam os tiles com imagens simuladas e não acessam os servidores cartográficos.

## Backup e restauração

GeoJSON exporta registros ativos, sem contas ou histórico completo, portanto não substitui backup do banco. Criar backup consistente com `sqlite3.Connection.backup`, para pasta restrita e armazenamento separado.

```python
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

folder = Path('/backups')
folder.mkdir(parents=True, exist_ok=True)
target = folder / ('inventario-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.sqlite3')
source = sqlite3.connect('/data/inventario.sqlite3')
destination = sqlite3.connect(target)
try:
    source.backup(destination)
finally:
    destination.close()
    source.close()
```

Definir frequência, retenção e responsável com a REBIO. Para restaurar, interromper escritas, preservar o arquivo atual, restaurar cópia verificada e executar `PRAGMA integrity_check` antes de iniciar. Conferir usuários, registros e histórico. Testar em ambiente isolado antes de confiar no backup.

## Critérios para publicação

- Conciliação dos RF/RNF e telas oficiais.
- HTTPS e cookies seguros verificados.
- Limitação de tentativas de login no proxy ou aplicação (ainda não implementada).
- Banco fora da pasta pública, volume persistente e segredo estável.
- Regras de exposição das coordenadas e perfis validadas com a REBIO.
- Backup completo e recuperação testados.
- Avaliação manual de acessibilidade e testes automatizados.

Não há publicação, conta em provedor, cobrança ou alteração de compartilhamento realizada nesta entrega.
