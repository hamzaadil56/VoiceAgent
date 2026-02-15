---
name: backend-engineer
description: Architect, design, and evolve backend systems for enterprise applications with scalability, reliability, security, and long-term maintainability. Use when coding agent must choose backend frameworks or architectural patterns, define service boundaries, design APIs and data models, set operational standards, or make tradeoff-driven technical decisions for backend services.
---

# Backend Engineer

Design backend solutions that scale with product growth, team size, and operational load.

## Core workflow

1. Clarify domain, scale, and reliability constraints.
2. Select architecture style and service boundaries.
3. Choose framework and runtime intentionally.
4. Define API, data, and async interaction contracts.
5. Enforce security, observability, and resilience defaults.
6. Ship with quality gates and migration-safe rollout plans.

## 1) Clarify constraints

Capture before implementation:
- Business capabilities and bounded contexts
- Latency and throughput targets (p50/p95/p99)
- Availability and recovery targets (SLA/SLO, RTO, RPO)
- Compliance and data governance requirements
- Team constraints (skills, staffing, deployment maturity)

If inputs are missing, state assumptions explicitly and proceed.

## 2) Choose architecture and boundaries

Use this decision order:
1. Start from domain boundaries, then map services/modules.
2. Prefer modular monolith first unless clear scaling or ownership pressure requires distributed services.
3. Isolate cross-cutting concerns (auth, config, telemetry, retries, idempotency).
4. Keep integration edges explicit (API gateway, event bus, external adapters).
5. Define ownership and change boundaries per service.

Read `references/architecture-playbook.md` for boundary and decomposition patterns.

## 3) Choose framework and runtime

Make decisions using:
- Problem fit (I/O heavy, CPU heavy, real-time, batch)
- Ecosystem maturity for required capabilities
- Operational profile (startup time, memory, concurrency model)
- Team familiarity and hiring sustainability
- Testing and observability support

Read `references/framework-decision-matrix.md` for a practical decision rubric.

## 4) Design contracts first

Define these explicitly:
- API contracts (versioning, error model, pagination, idempotency)
- Persistence model (transaction boundaries, consistency model, indexing)
- Async workflows (event schema, retries, dead-letter handling)
- Service-to-service communication (timeouts, backoff, circuit breaking)
- Backward compatibility and migration strategy

## 5) Apply production defaults

Apply by default:
- Zero-trust service security and least privilege
- Structured logs, traces, and metrics with correlation IDs
- Resilience controls (timeouts, retries, bulkheads, rate limiting)
- Data safety controls (encryption, retention, auditability)
- Safe deploy patterns (canary/blue-green/feature flags)

## 6) Delivery output format

When asked to architect backend work, return:
1. Architecture decision summary with tradeoffs
2. Service/module boundaries and ownership map
3. API and data contract strategy
4. Reliability, security, and observability design
5. Delivery plan with migration and rollback steps
6. Quality gates for CI/CD and release
7. Risks with mitigation and follow-up actions

## Anti-patterns to avoid

- Distributed services without clear ownership boundaries
- Shared database coupling across service boundaries
- Implicit contracts and undocumented failure semantics
- Missing idempotency in external side-effect flows
- Late-stage observability and security retrofits

## References map

- `references/architecture-playbook.md`: Service boundary and architecture patterns for enterprise systems
- `references/framework-decision-matrix.md`: Framework and runtime selection matrix with tradeoffs
- `references/quality-gates.md`: Backend definition of done and release readiness checks
