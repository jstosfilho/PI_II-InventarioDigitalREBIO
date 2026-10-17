"""Entrypoint Flask reconhecido pela Vercel; não inicia servidor ao importar."""
from inventario import create_app

app = create_app()
