# Specifications

Product and engineering changes start with a spec before implementation. The spec is the contract for behavior, data semantics, permissions, tests, rollout and acceptance.

## Specification catalogue

| File | Area | State |
|---|---|---|
| [2026-10-31-pillar-d2-billing-realization.md](2026-10-31-pillar-d2-billing-realization.md) | D2 Billing Realization | Return-metadata guard, PR #63 v15/v16 + pinned v16.5.0 query smoke, and PR #65 independent Payment Entry permission fix merged/CI-verified; target-site reconciliation and role validation remain |
| [2026-11-01-crm-signals-core-and-access.md](2026-11-01-crm-signals-core-and-access.md) | CRM Signal model, ingestion, permissions and Console | Baseline implemented; release hardening and target-site acceptance remain |
| [2026-11-01-settings-and-core-reliability.md](2026-11-01-settings-and-core-reliability.md) | Settings singleton, starter presets, event identity and digest reliability | PR #19/#23 merged and CI-verified; target-site configuration and scheduler/mail acceptance remain |
| [2026-11-01-crm-signals-events-and-notifications.md](2026-11-01-crm-signals-events-and-notifications.md) | Quotation/Opportunity events and realtime routing | Settings/idempotency PR #19/#23, transactional outbox PR #26 and durable realtime retry PR #54 merged/CI-verified; target-site event policy and recovery acceptance remain |
| [2026-11-01-crm-signals-daily-digest.md](2026-11-01-crm-signals-daily-digest.md) | Scheduled Sales Manager digest | Configurable schedule/date idempotency PR #19/#23 merged/CI-verified; target-site timezone, recipient and mail-queue acceptance remain |
| [2026-11-01-pillar-d1-sales-compass.md](2026-11-01-pillar-d1-sales-compass.md) | D1 Sales Compass | Missing-status correctness PR #17 and PR #63 v15/v16 + pinned v16.5.0 query-contract smoke merged/CI-verified; target-site workflow and role validation remain |
| [2026-11-01-pillar-d3-service-resolution-sla.md](2026-11-01-pillar-d3-service-resolution-sla.md) | D3 Service Resolution/SLA | Adapter, aggregate fixture and exact v16.5.0/Helpdesk v1.28.0 reference CI verified; target-site source/permission/SLA acceptance remains |
| [2026-11-01-pillar-h-highlights.md](2026-11-01-pillar-h-highlights.md) | H Highlights | High-value Quotation alerts, per-Company thresholds and PR #60 contract tests merged/CI-verified; VIP escalation needs approved trigger/recipient policy and proposal-link tracking remains gated on privacy/consent and retention approval |
| [2026-11-01-pillar-e-explorer.md](2026-11-01-pillar-e-explorer.md) | E Explorer | Core API PR #57, Desk UI PR #59 and five-context browser/operational hardening PR #61 merged/CI-verified; target-site role/source acceptance and optional-provider inventory remain |
| [2026-11-01-pillar-v-vault.md](2026-11-01-pillar-v-vault.md) | V Vault | Design specified; metric registry and retention configuration required |
| [2026-11-01-pillar-a-analysis.md](2026-11-01-pillar-a-analysis.md) | A Analysis | Design specified; approved metric/query registry required |

The complete dependency order and release gates are in [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md). Durable decisions are in [docs/DECISIONS.md](../docs/DECISIONS.md).

## Required content

Every feature spec must include:

1. **Problem and user** — who needs the change and what decision or action it supports.
2. **Goals and non-goals** — what is included and what is explicitly deferred.
3. **Source of truth** — DocTypes, fields, integrations and permission rules.
4. **Metric or behavior definitions** — filters, date windows, currency basis, state transitions and edge cases. Avoid ambiguous terms such as "revenue" when the calculation is actually invoiced value or cash received.
5. **Acceptance criteria** — observable, testable statements written before implementation.
6. **Validation mapping** — unit, Bench integration and browser E2E tests that prove each criterion.
7. **Risks and rollout** — migrations, permissions, compatibility, configuration and operational checks.
8. **Known gaps** — what exists today versus what remains to be implemented or verified.

## Required test progression

- **Unit tests** validate calculation rules, edge cases, permission-denied behavior, idempotency and invalid inputs.
- **Bench integration tests** install the app on a real Frappe/ERPNext site and run tests inside the Bench Python environment.
- **Browser E2E tests** log in through Frappe and exercise the actual Desk page and its API. Seeded records should be unique and cleaned up after each test.
- **Migration checks** are required when a change introduces DocTypes, fields, patches, indexes or data backfills.
- **Target-site acceptance** checks actual Company currency, timezone, role permissions, workflow states, installed apps and financial totals. CI does not replace this.

A spec is not complete because code exists. Its acceptance criteria must be linked to passing tests, and unsupported sources must be reported as unavailable rather than replaced with guessed data. D3's discovery spec is complete for the discovery/adapter contract; its concrete source-field mapping is deliberately gated on target-site evidence.

| Realtime delivery reliability | [Durable realtime delivery](2026-11-02-durable-realtime-delivery.md) | PR #54 merged; code/test CI verified on v15/v16 and exact Frappe v16.5.0 reference; target-site Redis/worker/scheduler acceptance remains |
