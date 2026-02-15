# Framework Decision Matrix

Use this rubric to choose backend framework/runtime in a defensible, repeatable way.

## Evaluation dimensions

- Domain fit: Align concurrency and programming model with workload shape.
- Performance profile: Validate latency, throughput, and resource footprint.
- Reliability features: Confirm support for retries, cancellation, and graceful degradation.
- Ecosystem maturity: Verify production-grade libraries for auth, persistence, messaging, and observability.
- Operability: Confirm debuggability, metrics, tracing, and deployment ergonomics.
- Team sustainability: Optimize for team expertise and maintainable hiring/training path.

## Decision process

1. List hard constraints (compliance, latency SLO, deployment platform).
2. Choose 2-3 realistic framework candidates.
3. Score each dimension from 1-5 with short rationale.
4. Reject options with hard-constraint failures regardless of score.
5. Select the best fit and record tradeoffs in an ADR.

## Common guidance by workload

- High-concurrency I/O APIs: Prefer event-loop or async-native frameworks with strong observability support.
- CPU-heavy processing: Prefer runtimes with efficient multi-core execution and clear worker isolation.
- Internal enterprise APIs: Prefer convention-rich frameworks that improve consistency and governance.
- Event-driven systems: Prefer frameworks with mature messaging, idempotency hooks, and retry/DLQ support.

## Non-negotiables

- Strong testing story (unit, integration, contract)
- First-class telemetry integration
- Security baseline support (authn/authz, secrets, transport security)
- Backward-compatible API and schema evolution patterns
