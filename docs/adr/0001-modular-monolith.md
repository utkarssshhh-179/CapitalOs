# ADR 0001: Modular monolith with layered modules
Status: accepted

One deployable FastAPI app. Each module (`app/modules/<name>`) owns router, service,
repository, schemas and models. Routers never contain business logic; services never touch
sessions directly; repositories never contain business rules. Modules talk to each other only
through service interfaces, so any module can later be extracted.
