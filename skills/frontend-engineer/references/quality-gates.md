# Quality Gates

## Pull request gate

A change is ready for review only if it passes:
- Lint and formatting checks
- Type checks with no ignored errors
- Unit/integration tests for new behavior
- Accessibility checks for changed UI flows
- Performance budget checks for critical routes

## Definition of done

- Behavior matches acceptance criteria.
- Edge states are implemented (loading/empty/error).
- Telemetry/logging for critical actions is included.
- Documentation is updated for architecture-impacting decisions.
- Rollback strategy exists for risky releases.

## Testing expectations

- Unit tests: deterministic logic and pure transforms.
- Integration tests: feature workflows and component composition.
- E2E smoke tests: critical user journeys.
- Visual regression tests: shared primitives and key pages.

## Performance expectations

- Set budgets for bundle size and route-level LCP/INP/CLS.
- Track regressions in CI and block significant budget breaches.
- Prefer measured optimization over speculative micro-optimizations.

## Accessibility expectations

- Include automated checks in CI (axe or equivalent).
- Run manual keyboard traversal on high-traffic screens.
- Validate labels, names, roles, and focus order.
