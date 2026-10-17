"""SQL interno parametrizado para SQLite local e PostgreSQL em produção."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3


class Database:
    def __init__(self, sqlite_path, postgres_url=None):
        self.postgres = bool(postgres_url)
        if self.postgres:
            import psycopg
            from psycopg.rows import dict_row
            # Conexão por requisição: sem estado compartilhado entre funções.
            # prepare_threshold=None permite URLs com pooler transacional.
            self.connection = psycopg.connect(
                postgres_url, autocommit=True, row_factory=dict_row,
                connect_timeout=15, prepare_threshold=None,
            )
        else:
            self.connection = sqlite3.connect(sqlite_path, timeout=15)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute('PRAGMA foreign_keys = ON')

    @property
    def timestamp_sql(self):
        if self.postgres:
            return "to_char(clock_timestamp() AT TIME ZONE 'UTC', 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"')"
        return "strftime('%Y-%m-%dT%H:%M:%SZ','now')"

    @property
    def lock_suffix(self):
        return ' FOR UPDATE' if self.postgres else ''

    def execute(self, query, params=()):
        # Apenas instruções internas: '?' nunca aparece em literais SQL usados
        # pela aplicação. Valores externos continuam separados como parâmetros.
        if self.postgres:
            query = query.replace('?', '%s')
        return self.connection.execute(query, params)

    @contextmanager
    def transaction(self):
        if self.postgres:
            with self.connection.transaction():
                yield
        else:
            # Serializa os escritores antes de consultar a versão para excluir.
            self.connection.execute('BEGIN IMMEDIATE')
            with self.connection:
                yield

    def initialize(self):
        name = 'schema_postgres.sql' if self.postgres else 'schema.sql'
        script = Path(__file__).with_name(name).read_text(encoding='utf-8')
        if self.postgres:
            with self.transaction():
                # DDL estático, sem ';' em strings ou procedimentos.
                for statement in script.split(';'):
                    if statement.strip():
                        self.execute(statement)
        else:
            self.connection.executescript(script)

    def close(self):
        self.connection.close()


def is_duplicate_user(error):
    return (isinstance(error, sqlite3.IntegrityError)
            and getattr(error, 'sqlite_errorname', '') == 'SQLITE_CONSTRAINT_UNIQUE'
            or getattr(error, 'sqlstate', None) == '23505')
