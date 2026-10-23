.PHONY: up down logs test lint fmt migrate revision
up:
$\tcp -n .env.example .env || true
$\tdocker compose -f infra/docker-compose.yml up --build -d
down:
$\tdocker compose -f infra/docker-compose.yml down
logs:
$\tdocker compose -f infra/docker-compose.yml logs -f backend
test:
$\tcd backend && pytest
lint:
$\tcd backend && ruff check . && mypy app
fmt:
$\tcd backend && ruff format . && ruff check --fix .
migrate:
$\tdocker compose -f infra/docker-compose.yml run --rm migrate
revision:
$\tcd backend && alembic revision --autogenerate -m "$(m)"
