# Specifications

Product and engineering changes start with a spec before implementation. The spec is the contract for behavior, data semantics, permissions, tests, rollout and acceptance.

## Specification catalogue

| File | Area | State |
|---|---|---|
| [2026-10-31-pillar-d2-billing-realization.md](2026-10-31-pillar-d2-billing-realization.md) | D2 Billing Realization | Return-metadata guard merged in PR #17; target-site reconciliation remains |
| [2026-11-01-crm-signals-core-and-access.md](2026-11-01-crm-signals-core-and-access.md) | CRM Signal model, ingestion, permissions and Console | Baseline implemented; release hardening and target-site acceptance remain |
| [2026-11-01-settings-and-core-reliability.md](2026-11-01-settings-and-core-reliability.md) | Settings singleton, starter presets, event identity and digest reliability | Implementation in PR #19; CI and merge pending |
| [2026-11-01-crm-signals-events-and-notifications.md](2026-11-01-crm-signals-events-and-notifications.md) | Quotation/Opportunity events and realtime routing | Baseline implemented; settings/idempotency implementation in PR #19 |
| [2026-11-01-crm-signals-daily-digest.md](2026-11-01-crm-signals-daily-digest.md) | Scheduled Sales Manager digest | Baseline implemented; configurable schedule and date idempotency in PR #19 |
| [2026-11-01-pillar-d1-sales-compass.md](2026-11-01-pillar-d1-sales-compass.md) | D1 Sales Compass | Missing-status correctness merged in PR #17; target-site validation remains |
| [2026-11-01-pillar-d3-service-resolution-sla.md](2026-11-01-pillar-d3-service-resolution-sla.md) | D3 Service Resolution/SLA | Discovery contract ready; source mapping must be completed on the target site |
| [2026-11-01-pillar-h-highlights.md](2026-11-01-pillar-h-highlights.md) | H Highlights | Design specified; implementation planned |
| [2026-11-01-pillar-e-explorer.md](2026-11-01-pillar-e-explorer.md) | E Explorer | Design specified; integration inventory required |
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
