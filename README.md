# CapitalOS
AI Powered Lending & Collection Management Platform.

## Quick start
```bash
make up        # builds and starts db, redis, migrations, backend, nginx
curl localhost:8080/api/v1/health/ready
# API docs: http://localhost:8080/api/docs
```

## Develop
```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make test && make lint
```

## Architecture
Modular monolith, layered: router -> service -> repository -> PostgreSQL. See `docs/adr`.

## Roadmap
0 Foundation (done) -> 1 Auth & RBAC -> 2 Audit -> 3 Borrowers/Investors -> 4 Loan engine -> ...
