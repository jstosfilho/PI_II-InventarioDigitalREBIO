# Inventário Digital REBIO

Estrutura base da aplicação (Next.js + FastAPI + PostGIS), conforme o documento *Arquitetura e Modelagem – Inventário Digital*. Ainda não há tabelas, autenticação nem storage.

## Subir com Docker

```bash
cp .env.example .env
docker compose up --build
```

| Serviço  | URL                           |
|----------|-------------------------------|
| Frontend | http://localhost:3000         |
| Backend  | http://localhost:8000/docs    |
| Health   | http://localhost:8000/health  |
| Banco    | localhost:5432 (PostGIS)      |

## Testes unitários

```bash
# Backend (pytest)
docker compose run --rm --no-deps backend pytest

# Frontend (vitest)
docker compose run --rm --no-deps frontend npm test
```

Os testes do backend usam um banco simulado, então não precisam do Postgres no ar.
