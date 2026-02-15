# Agentic Forms Platform Plan (Admin-Created, Consumer-Answered)

## Summary
Build a multi-tenant platform where admins design and publish conversational forms (chatbot/voicebot), and consumers answer through public links. Consumer login is not required for v1 (anonymous link access).

## Updated Account/Access Model
- `Admin side`: authenticated users in organization workspaces create, manage, and publish forms/bots.
- `Consumer side`: anonymous respondents access published forms via URL/QR/invite link.
- `Session identity`: generated `respondent_session_id` with optional metadata (utm/source/device/ip hash), no mandatory consumer account.

## Core Architecture (Grounded in current stack)
- Frontend remains React + Vite + TypeScript; expand to:
- Admin app routes for builder/analytics/submissions.
- Public consumer form runtime route for chat + voice.
- Backend remains FastAPI + WebSocket; refactor from single global voice agent into session-scoped bot runtime.
- Data: Postgres (durable), Redis (ephemeral session/state), object storage (exports/artifacts).
- Deploy: Vercel frontend + Dockerized VPS backend (API + worker + Postgres + Redis + reverse proxy).

## Public APIs / Interface Changes
- Admin auth/workspace:
- `POST /v1/auth/login`, `GET /v1/me`
- `POST /v1/orgs/:orgId/forms` (create)
- `POST /v1/forms/:formId/publish` (immutable version)
- Public consumer runtime:
- `POST /v1/public/f/:slug/sessions` (anonymous session)
- `POST /v1/public/sessions/:sessionId/message` (chat mode)
- `WS /v1/public/sessions/:sessionId/voice` (voice mode)
- `POST /v1/public/sessions/:sessionId/complete`
- Submissions/exports:
- `GET /v1/forms/:formId/submissions`
- `POST /v1/forms/:formId/exports/csv`

## Data Model (Key Tables)
- `organizations`, `admin_users`, `memberships`
- `forms`, `form_versions`, `form_graph_nodes`, `form_graph_edges`
- `respondent_sessions` (anonymous token, channel, locale, state pointer)
- `messages`, `answers`, `submissions`
- `audit_logs`, `exports`

## Flow Engine
- Hybrid graph + LLM:
- Deterministic graph enforces required fields, branching, and validation.
- LLM personalizes phrasing, handles clarifications, and maps responses to strict field schema.
- Required-field guardrail prevents skipping mandatory questions.

## Security Baseline (SOC2-ready)
- Strong admin auth + RBAC.
- Anonymous consumer sessions signed with expiring tokens.
- Tenant isolation in all queries.
- Encryption in transit/at rest, audit logs for admin actions and exports.
- Abuse controls on public endpoints (rate limits, bot protection).

## Phased Delivery
1. Foundation
- Add auth, org/workspace model, migrations, Redis, worker.
2. Form Builder + Publish
- Admin UI + backend for graph authoring and versioned publish.
3. Consumer Runtime
- Public chat runtime first, then voice runtime (reusing current WS audio pipeline).
4. Submissions + Analytics + CSV
- Dashboard, funnel/drop-off analytics, exports.
5. Hardening + Launch
- Performance, security, monitoring, backup/restore drills.

## Test Scenarios
- Admin creates/publishes form; consumer completes via anonymous link.
- Branching + validation correctness across chat and voice.
- Session resume/reconnect for voice.
- Cross-tenant isolation and export authorization checks.
- Load targets for concurrent anonymous sessions.

## Assumptions
- Consumers are anonymous in v1 (no account required).
- Admins are authenticated and workspace-scoped.
- Channels at launch: web chat + web voice.
- Internal analytics + CSV in v1; external integrations later.
