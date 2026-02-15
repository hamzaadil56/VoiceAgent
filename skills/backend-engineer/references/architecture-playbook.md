# Backend Architecture Playbook

## Bounded Context First

- Derive module or service boundaries from domain capabilities, not from technical layers.
- Keep each boundary responsible for its own data model and invariants.
- Define a clear ownership map to prevent ambiguous change responsibility.

## Decomposition Strategy

1. Start as a modular monolith when domain coupling is still high.
2. Extract services only when one of these is persistent:
- Independent scaling profile
- Distinct ownership team
- Different release cadence
- Isolation requirement for reliability or compliance

## Communication Patterns

- Use synchronous calls for request/response workflows that require immediate consistency.
- Use asynchronous events for decoupling, fan-out, and long-running flows.
- Avoid event choreography without explicit ownership and failure handling.

## Data Ownership

- Enforce one primary writer per business entity.
- Use replication/read models instead of cross-service shared writes.
- Design schema evolution with backward compatibility and clear deprecation windows.

## Reliability Patterns

- Set explicit timeout budgets for every outbound call.
- Retry only idempotent operations with bounded exponential backoff.
- Isolate failures with circuit breakers and bulkheads.
- Add dead-letter queues and replay tooling for asynchronous processing.

## Migration Patterns

- Prefer expand-contract database migration strategy.
- Deploy code that supports old and new schema before destructive changes.
- Roll out progressively with observability checkpoints and rollback criteria.
