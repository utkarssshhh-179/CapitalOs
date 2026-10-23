# ADR 0003: Multi-tenancy
Status: accepted

Shared database, shared schema. Every business table has `organization_id` (see `TenantMixin`).
Milestone 1 adds the `organizations` table and enforces tenant scoping in the repository base
class, with PostgreSQL row-level security as a second layer.
