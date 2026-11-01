# S.A.H.D.E.V. vertical-slice roadmap

This roadmap tracks capability status and dependencies. The complete project delivery sequence, exit criteria and release gates are in [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md). Feature contracts are indexed in [specs/README.md](../specs/README.md).

## D — Dashboard: Executive Compass

### D1. Sales Compass — implemented

- Lead creation in the rolling last-30-day window.
- Active Lead count using an explicit terminal-status policy.
- Active Opportunity count and stage distribution.
- Pipeline amount grouped by transaction currency; never sum unlike currencies.
- Recent Opportunities with a direct Desk drill-down.
- Lead and Opportunity reads use permission-aware Frappe list APIs.

**Remaining:** The missing-status fallback was removed in PR #17. Confirm terminal statuses and custom workflows on the target site, then validate role and data visibility with real Sales User and Sales Manager accounts.

Specification: [D1 Sales Compass](../specs/2026-11-01-pillar-d1-sales-compass.md).

### D2. Billing Realization — implemented

- Invoiced: submitted, non-return Sales Invoice grand totals posted in the last 30 days, grouped by invoice currency.
- Outstanding: current positive outstanding amounts on submitted, non-return Sales Invoices, grouped by party-account currency.
- Customer receipts: submitted Receive Payment Entries for Customer parties in the last 30 days, grouped by receiving-account currency. Includes allocated and advance/unallocated receipts.
- POS receipts: submitted POS Sales Invoice paid_amount in the last 30 days, grouped by invoice currency. Kept separate from Payment Entry receipts.
- Overdue: count and oldest eight submitted, non-return invoices with a positive outstanding amount and a due date before today.
- Every source uses permission-aware Frappe list APIs. Unlike currencies are never added together.

**Remaining:** The return-metadata guard was merged in PR #17. Reconcile values against native Sales Invoice and Payment Entry reports on the target site. Validate invoice, party-account and receiving-account currency behavior.

Specification: [D2 Billing Realization](../specs/2026-10-31-pillar-d2-billing-realization.md).

### D3. Service Resolution/SLA — adapter and exact reference CI verified; pilot acceptance open

- PR #32 adds the standard Frappe Helpdesk adapter using HD Ticket and HD Service Level Agreement metadata.
- Dashboard aggregates ticket creation, current Open/Paused backlog, resolved cohort, native resolution_time and Fulfilled/Failed SLA outcomes.
- SLA outcomes/no-SLA counts use the rolling 30-day created-ticket cohort; only Fulfilled/Failed are eligible for compliance. Due/paused states are excluded.
- Ticket/SLA DocType permissions are checked independently; the payload contains aggregates only.
- Monday–Saturday is the agreed initial assumption, but the active Helpdesk SLA's working hours, holiday list and timezone remain authoritative.

**Remaining:** confirm the pilot's exact Frappe v16.5 patch and installed ERPNext/Helpdesk versions; verify the Sales User/Manager read-only role on HD Ticket and HD Service Level Agreement, inspecting actual field permlevels for that Helpdesk release (the v1.28.0 reference fields are all permlevel 0); validate each active SLA calendar on the target site. The fail-closed field-level permission correction merged in PR #42, and the exact v16.5.0/Helpdesk v1.28.0 reference lane passed in PR #50. Do not treat CI as pilot acceptance.

Specification: [D3 Service Resolution/SLA](../specs/2026-11-01-pillar-d3-service-resolution-sla.md).

## H — Highlights: event-driven alerts

**Status:** High-value Quotation signals and per-company threshold implementation are merged in PR #45; PR #49 fixes Company-currency display/fetch. Target-site Company amounts/fallback policy still require explicit approval. VIP proposal-link tracking remains gated on privacy/consent and retention approval.

- High-value submitted Quotations use the Company's base currency and an admin-configured threshold; per-company overrides merged in PR #45. Each enabled Company requires an explicitly approved amount.
- VIP proposal-link opens only from first-party tracked links or a provider with stable event IDs.
- Escalation to enabled, related users with source-record read permission.
- Idempotency, bot/scanner exclusion, alert cooldown and privacy/consent controls.
- No site-wide broadcast and no invasive browser fingerprinting.

Specification: [H Highlights](../specs/2026-11-01-pillar-h-highlights.md).

## E — Explorer: customer interaction timeline

**Status:** Design specified; target-site integration inventory required.

- Chronological Lead/Customer activity view from Signals, Highlights and the verified source integrations.
- Adapter contract for source identity, event ID, timestamp, party relationship, permission and route.
- Stable pagination and deduplication.
- No copying of full email bodies, recordings, WhatsApp messages or attachments.
- Missing integration, empty result and permission denial remain distinct.

Specification: [E Explorer](../specs/2026-11-01-pillar-e-explorer.md).

## V — Vault: historical intelligence

**Status:** Design specified; metric registry and retention policy required.

- Daily snapshots of approved aggregate metrics with dimensions, source counts, provenance and definition versions.
- Append-only revisions; never silently rewrite historical values.
- No raw party names, source record identifiers or free-text content in snapshot rows.
- Snapshot scheduling disabled until an explicit retention period and source-visibility policy are approved.
- Bounded, admin-only audited backfills and dry-run pruning.

Specification: [V Vault](../specs/2026-11-01-pillar-v-vault.md).

## A — Analysis: natural-language sales questions

**Status:** Design specified; metric registry required.

- Start with deterministic, approved questions mapped to versioned metrics.
- Optionally classify natural language to a constrained metric/filter/grouping intent.
- Execute server-owned definitions with permission-aware Frappe reads.
- Never execute model-generated SQL, Python or arbitrary field/DocType requests.
- Return period, filters, metric version, units/currency and authorized source links.

Specification: [A Analysis](../specs/2026-11-01-pillar-a-analysis.md).

## Delivery rule

A vertical slice is complete only when its data contract, permission behavior, UI, tests, operational configuration and documentation are all present. A visible metric must be backed by real source data and a stated calculation. Cross-slice dependencies are enforced by the [implementation plan](../IMPLEMENTATION_PLAN.md).
