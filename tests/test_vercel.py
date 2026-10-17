import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inventario import create_app


class VercelConfigurationTest(unittest.TestCase):
    def test_missing_database_fails_instead_of_using_ephemeral_sqlite(self):
        with patch.dict(os.environ, {'VERCEL': '1', 'REBIO_SECRET_KEY': 's'*64}, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'DATABASE_URL'):
                create_app()

    def test_missing_secret_fails(self):
        with patch.dict(os.environ, {'VERCEL': '1', 'DATABASE_URL': 'postgresql://unused/db'}, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'REBIO_SECRET_KEY'):
                create_app()

    def test_serverless_initialization_does_not_write_or_connect(self):
        with patch.dict(os.environ, {'VERCEL': '1', 'DATABASE_URL': 'postgresql://unused/db',
                                    'REBIO_SECRET_KEY': 's'*64}, clear=True):
            with patch('inventario.Path.mkdir') as mkdir, patch('inventario.Database') as database:
                app = create_app()
                mkdir.assert_not_called()
                database.assert_not_called()
                self.assertTrue(app.config['SESSION_COOKIE_SECURE'])
                self.assertEqual(app.config['IMPORT_MAX_FILE_SIZE'], 4*1024*1024)
                self.assertEqual(app.test_client().get('/health').status_code, 200)
                html = app.test_client().get('/').data
                self.assertIn(b'data-import-max-bytes="4194304"', html)
                self.assertIn(b'Tamanho m\xc3\xa1ximo: 4 MiB', html)

    def test_import_obeys_environment_limit(self):
        with tempfile.TemporaryDirectory() as folder:
            app = create_app({'TESTING': True, 'SECRET_KEY': 'test', 'DATABASE_URL': None,
                              'DATABASE': str(Path(folder)/'test.sqlite3'),
                              'IMPORT_MAX_FILE_SIZE': 128})
            runner = app.test_cli_runner()
            self.assertEqual(runner.invoke(args=['init-db']).exit_code, 0)
            created = runner.invoke(args=['create-user', 'gestor', '--password', 'teste-seguro-123'])
            self.assertEqual(created.exit_code, 0, created.output)
            duplicate = runner.invoke(args=['create-user', 'gestor', '--password', 'teste-seguro-123'])
            self.assertNotEqual(duplicate.exit_code, 0)
            self.assertIn('Usuário já existe', duplicate.output)
            client = app.test_client()
            csrf = client.post('/api/login', json={'username': 'gestor', 'password': 'teste-seguro-123'}).json['csrf']
            response = client.post('/api/import-geometry', headers={'X-CSRF-Token': csrf},
                                   data={'kind': 'nascente', 'file': (io.BytesIO(b'x'*129), 'teste.gpx')})
            self.assertEqual(response.status_code, 400)
            self.assertIn('máximo', response.json['error'])
