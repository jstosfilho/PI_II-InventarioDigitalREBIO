"""Copia apenas os assets públicos. Não conecta nem altera banco no build."""
from pathlib import Path
import shutil


def main():
    root = Path(__file__).resolve().parents[1]
    source = root / 'inventario' / 'static'
    target = root / 'public' / 'static'
    target.mkdir(parents=True, exist_ok=True)
    for name in ('app.js', 'style.css'):
        shutil.copyfile(source / name, target / name)
    print('Assets públicos preparados em public/static.')


if __name__ == '__main__':
    main()
