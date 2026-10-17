import unittest
import subprocess
from unittest.mock import patch

import click
from tools.setup_cloud import normalize_connection_url, read_connection_from_clipboard


class ConnectionInputTest(unittest.TestCase):
    def test_neon_copy_formats_preserve_credentials_and_tls_options(self):
        url = 'postgresql://usuario:senha%40teste@db.example.invalid/banco?sslmode=require&channel_binding=require'
        for value in (url, f'  {url}\n', f"'{url}'", f'"{url}"',
                      f"psql '{url}'", f'psql "{url}"',
                      f'DATABASE_URL={url}', f'DATABASE_URL="{url}"',
                      f"export DATABASE_URL='{url}'"):
            with self.subTest(format=value.split('://')[0]):
                self.assertEqual(normalize_connection_url(value), url)

    def test_incomplete_or_wrong_addresses_do_not_expose_input(self):
        for value in ('', 'https://console.neon.tech/', 'postgresql://',
                      'postgresql://usuario:segredo@host',
                      'postgresql://usuario:segredo@host:errada/banco',
                      'postgresql://usuario:segredo@host/banco#fragmento',
                      "psql 'postgresql://usuario:segredo@host/banco", 'DATABASE_URL='):
            with self.subTest():
                with self.assertRaises(click.ClickException) as caught:
                    normalize_connection_url(value)
                self.assertNotIn('segredo', str(caught.exception))

    def test_clipboard_reads_without_using_hidden_terminal_paste(self):
        url = 'postgresql://usuario:senha@host.invalid/PI_II-InventarioDigitalREBIO?sslmode=require&channel_binding=require'
        with patch('tools.setup_cloud.subprocess.run', return_value=subprocess.CompletedProcess([], 0, url+'\r\n')) as run:
            self.assertEqual(read_connection_from_clipboard(), url)
        self.assertTrue(run.call_args.kwargs['capture_output'])
        self.assertNotIn(url, str(run.call_args.args))

    def test_empty_or_control_character_input_explains_clipboard_alternative(self):
        for value in ('', '\x16', 'postgresql://usuario:senha@host/banco\x16'):
            with self.assertRaises(click.ClickException) as caught:
                normalize_connection_url(value)
            self.assertIn('--clipboard', str(caught.exception))
