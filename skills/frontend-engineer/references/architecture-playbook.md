# Architecture Playbook

## Decision matrix

- Use Next.js/SSR hybrids for SEO-heavy or content-heavy journeys.
- Use SPA architecture for highly interactive internal apps with limited SEO constraints.
- Use modular monolith frontend before micro-frontends unless team/org boundaries demand runtime independence.

## Folder strategy (feature-first)

```text
src/
  app/                # app shell, routing, providers
  features/
    <feature>/
      components/
      hooks/
      services/
      state/
      tests/
      index.ts
  shared/
    ui/               # design-system primitives
    lib/              # cross-feature utilities
    api/              # clients and transport helpers
    config/
  styles/
    tokens/
    globals/
```

## Boundary rules

- Import direction: `app -> features -> shared`; never reverse.
- Feature modules expose public API through `index.ts` only.
- Keep services pure where possible; isolate side effects.
- Keep shared folder generic; move domain-specific code back into features.

## State strategy

- Server state: query/cache library with explicit stale policies.
- Client UI state: local state first, then scoped context/store.
- URL state: source of truth for filters, sort, pagination when shareable.
- Forms: schema-driven validation and typed payload transforms.

## Scaling rules

- Prefer adding feature modules over widening global stores.
- Introduce package boundaries only when ownership or build performance requires it.
- Enforce architecture with lint rules and import constraints.
