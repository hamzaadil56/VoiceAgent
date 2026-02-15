# Backend Quality Gates

Apply these gates before merge and before release.

## Merge gates

- Linting and static analysis pass
- Type checks pass (where applicable)
- Unit and integration tests pass
- API contract checks pass
- Security scan findings triaged (no unapproved critical issues)

## Release gates

- Migration scripts reviewed and rollback-safe
- Performance baseline within target budgets
- SLO dashboards and alerts configured
- Runbook and on-call ownership documented
- Feature flags or progressive rollout plan prepared

## Production readiness checklist

- Health/readiness probes implemented
- Structured logs, traces, and metrics emitted
- Timeouts, retries, and circuit breakers configured
- Idempotency defined for side-effecting operations
- Data retention and audit requirements satisfied
