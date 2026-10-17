"""Inicializa um banco PostgreSQL novo; segredos digitados sem eco no terminal."""
import getpass
import argparse
import re
import shlex
import sys
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import click
from inventario import create_app


def normalize_connection_url(value):
    """Aceita os formatos copiados do painel, sem executar comandos de shell."""
    value = value.strip().lstrip('\ufeff').strip()
    if not value or any(ord(char) < 32 for char in value):
        raise click.ClickException(
            'A entrada está vazia ou contém caracteres de controle. '
            'Copie a conexão no Neon e execute: python tools/setup_cloud.py --clipboard'
        )
    assignment = re.fullmatch(r'(?:export\s+)?DATABASE_URL\s*=\s*(.+)', value, re.S)
    if assignment:
        value = assignment.group(1).strip()
    if value.startswith('psql '):
        try:
            parts = shlex.split(value)
        except ValueError:
            parts = []
        if len(parts) != 2:
            raise click.ClickException('Copie somente a URL PostgreSQL ou o comando psql com a URL entre aspas, sem opções adicionais.')
        value = parts[1]
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('\"', "'"):
        value = value[1:-1]
    try:
        from psycopg.conninfo import conninfo_to_dict
    except ImportError:
        raise click.ClickException(
            'Driver PostgreSQL ausente ou indisponível. Execute: '
            '.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt'
        ) from None
    try:
        parsed = urlsplit(value)
        valid = (parsed.scheme in ('postgresql', 'postgres') and parsed.hostname
                 and parsed.username and parsed.path.strip('/')
                 and not parsed.fragment and not any(c.isspace() for c in value))
        parsed.port  # Valida a porta, se fornecida.
        if valid:
            conninfo_to_dict(value)
    except Exception:
        valid = False
    if not valid:
        raise click.ClickException(
            'Conexão inválida. No Neon, abra Connect e copie a connection string completa, '
            'começando com postgresql://. Não use o endereço https:// do painel nem o exemplo do guia. '
            'A URL não será exibida para proteger suas credenciais.'
        )
    return value


def read_connection_from_clipboard():
    """Leitura explícita por --clipboard; não imprime o conteúdo ou erros brutos."""
    try:
        result = subprocess.run(
            ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
             '[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); Get-Clipboard -Raw'],
            capture_output=True, text=True, encoding='utf-8', check=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        raise click.ClickException('Não foi possível ler a área de transferência do Windows. Copie a conexão e tente novamente.') from None
    return normalize_connection_url(result.stdout)


def main(use_clipboard=False):
    print('No Neon, abra Connect e copie a connection string. Também aceitamos psql seguido da URL entre aspas.')
    if use_clipboard:
        url = read_connection_from_clipboard()
        print('Conexão lida da área de transferência e formato validado. O conteúdo não será exibido.')
    else:
        print('A colagem será oculta: cole uma vez e pressione Enter, mesmo sem aparecer texto.')
        print('Se a colagem não funcionar, use a opção --clipboard após copiar a conexão.')
        url = normalize_connection_url(getpass.getpass('Cole DATABASE_URL do PostgreSQL (entrada oculta): '))
    username = input('Login do gestor a criar: ').strip()
    if not username:
        raise click.ClickException('Informe o login do gestor.')
    # Apenas neste processo. Não escreve URL nem senha em arquivo ou histórico.
    app = create_app({'DATABASE_URL': url})
    with app.app_context():
        app.cli.main(args=['init-db'], standalone_mode=False)
        app.cli.main(args=['create-user', username, '--role', 'gestor'], standalone_mode=False)
    print('Banco e gestor preparados. Cadastre DATABASE_URL no painel da Vercel.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preparar banco PostgreSQL e criar gestor.')
    parser.add_argument('--clipboard', action='store_true', help='Ler a conexão copiada no Windows, sem exibi-la.')
    args = parser.parse_args()
    try:
        main(use_clipboard=args.clipboard)
    except click.ClickException as error:
        error.show()
        raise SystemExit(1)
    except Exception:
        # Erros de conexão podem incluir endereço/credenciais; não os imprimir.
        print('Não foi possível preparar o banco. Confira URL, acesso de rede e credenciais.', file=sys.stderr)
        raise SystemExit(1)
