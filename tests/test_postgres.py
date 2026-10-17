"""Integração opt-in: banco de testes, cada caso em um schema descartável."""
import os
import uuid
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode, quote

import test_app


@unittest.skipUnless(os.environ.get('REBIO_TEST_DATABASE_URL'), 'PostgreSQL de testes não configurado.')
class PostgreSQLInventoryTest(test_app.InventoryTest):
    def database_config(self):
        import psycopg
        self.postgres_url = os.environ['REBIO_TEST_DATABASE_URL']
        self.schema = 'test_inventory_' + uuid.uuid4().hex
        # Identificador gerado internamente; não recebe texto do usuário.
        with psycopg.connect(self.postgres_url, autocommit=True) as connection:
            connection.execute(f'CREATE SCHEMA {self.schema}')
        self.addCleanup(self.drop_schema)
        url = urlsplit(self.postgres_url)
        params = [(key, value) for key, value in parse_qsl(url.query) if key != 'options']
        params.append(('options', f'-c search_path={self.schema}'))
        return {'DATABASE_URL': urlunsplit(url._replace(query=urlencode(params, quote_via=quote)))}

    def drop_schema(self):
        import psycopg
        with psycopg.connect(self.postgres_url, autocommit=True) as connection:
            connection.execute(f'DROP SCHEMA {self.schema} CASCADE')

    def test_cloud_setup_creates_first_manager(self):
        from tools import setup_cloud
        with patch('getpass.getpass', side_effect=[self.app.config['DATABASE_URL'],
                                                 'teste-seguro-123', 'teste-seguro-123']), \
             patch('builtins.input', return_value='gestor.nuvem'):
            setup_cloud.main()
        response = self.client.post('/api/login', json={'username':'gestor.nuvem','password':'teste-seguro-123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['role'], 'gestor')

    def test_simultaneous_edits_preserve_one_winner_and_history(self):
        feature_id = self.create()
        clients = [self.app.test_client(), self.app.test_client()]
        headers = []
        for client in clients:
            response = client.post('/api/login', json={'username':'gestor','password':'teste-seguro-123'})
            headers.append({'X-CSRF-Token': response.json['csrf']})
        barrier = Barrier(2)

        def edit(index):
            barrier.wait(timeout=10)
            return clients[index].put(f'/api/features/{feature_id}',
                                      json={**self.data, 'name':f'Edição {index}', 'version':1},
                                      headers=headers[index]).status_code

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(edit, range(2)))
        self.assertEqual(sorted(statuses), [200,409])
        history = self.client.get(f'/api/features/{feature_id}/history').json['items']
        self.assertEqual(len(history), 2)
