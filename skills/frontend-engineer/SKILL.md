---
name: frontend-engineer
description: Architect, implement, and evolve modern frontend applications with scalable structure, maintainable code, strong performance, accessibility, and polished user experience. Use when coding ahent design frontend architecture, choose frameworks/patterns, define folder structure, build reusable UI systems, improve UX/UI, harden quality gates, or refactor frontend codebases for long-term maintainability.
---

# Frontend Engineer

Design frontend solutions that are resilient under growth, easy to modify, and high quality for end users.

## Core workflow

1. Clarify product and technical constraints.
2. Choose architecture and boundaries.
3. Define standards before implementation.
4. Build in vertical slices with reusable primitives.
5. Enforce quality gates continuously.
6. Validate UX, accessibility, and performance before handoff.

## 1) Clarify constraints

Capture these inputs before coding:
- Product goals and primary user journeys
- Supported platforms (web, mobile web, desktop web)
- Rendering model constraints (CSR, SSR, SSG, hybrid)
- Scale assumptions (team size, feature velocity, expected traffic)
- Non-functional requirements (performance, accessibility, security)

If any are missing, make explicit assumptions and continue.

## 2) Choose architecture intentionally

Use this decision order:
1. Pick the framework/runtime that fits rendering and routing needs.
2. Split app into domains/features, not by technical layer alone.
3. Keep a thin app shell and isolated feature modules.
4. Centralize shared UI primitives, tokens, and cross-cutting utilities.
5. Keep data access and side effects at boundaries.

Read `references/architecture-playbook.md` for patterns and folder templates.

## 3) Set implementation standards

Define and follow:
- Typed contracts at all boundaries
- Predictable state strategy (server vs client state separated)
- Consistent component API design
- Styling strategy with design tokens and composition
- Testing pyramid and CI gates

Read `references/quality-gates.md` for merge and release criteria.

## 4) Build maintainable UI systems

Implement UI with these rules:
- Build primitive components first (Button, Input, Modal, Stack, Grid)
- Compose primitives into domain components
- Keep business logic out of visual primitives
- Favor accessibility-first patterns and keyboard support by default
- Create responsive behavior from tokenized breakpoints

Read `references/ui-ux-playbook.md` for practical UX/UI quality checks.

## 5) Performance and accessibility defaults

Apply by default:
- Code splitting and lazy loading at route/feature boundaries
- Memoization only where profiling justifies it
- Progressive loading states and skeletons
- Semantic HTML, focus management, ARIA only when needed
- Core Web Vitals budget tracking

## 6) Delivery output format

When asked to architect or implement frontend work, return:
1. Architecture decision summary (with tradeoffs)
2. Proposed folder/module structure
3. State/data strategy
4. UI system and design-token strategy
5. Quality gates (lint, typecheck, tests, performance, a11y)
6. Step-by-step implementation plan
7. Risks and mitigation

## Anti-patterns to avoid

- Mixing server and client state responsibilities
- Feature logic scattered across shared folders
- Deep prop drilling when composition/context boundaries are clearer
- UI libraries used without design-system constraints
- Shipping components without accessibility and test coverage

## References map

- `references/architecture-playbook.md`: Architecture choices, boundaries, and scalable folder patterns
- `references/ui-ux-playbook.md`: UX and interface quality standards for production UIs
- `references/quality-gates.md`: Definition of done and release readiness checks
