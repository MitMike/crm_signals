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

**Remaining:** Remove fallback behavior that counts all Leads/Opportunities as active when status metadata is missing. Confirm terminal statuses and custom workflows on the target site. Validate role and data visibility with real Sales User and Sales Manager accounts.

Specification: [D1 Sales Compass](../specs/2026-11-01-pillar-d1-sales-compass.md).

### D2. Billing Realization — implemented

- Invoiced: submitted, non-return Sales Invoice grand totals posted in the last 30 days, grouped by invoice currency.
- Outstanding: current positive outstanding amounts on submitted, non-return Sales Invoices, grouped by party-account currency.
- Customer receipts: submitted Receive Payment Entries for Customer parties in the last 30 days, grouped by receiving-account currency. Includes allocated and advance/unallocated receipts.
- POS receipts: submitted POS Sales Invoice paid_amount in the last 30 days, grouped by invoice currency. Kept separate from Payment Entry receipts.
- Overdue: count and oldest eight submitted, non-return invoices with a positive outstanding amount and a due date before today.
- Every source uses permission-aware Frappe list APIs. Unlike currencies are never added together.

**Remaining:** Require return metadata to guarantee exclusion semantics. Reconcile values against native Sales Invoice and Payment Entry reports on the target site. Validate invoice, party-account and receiving-account currency behavior.

Specification: [D2 Billing Realization](../specs/2026-10-31-pillar-d2-billing-realization.md).

### D3. Service Resolution/SLA — initial adapter merged; target-site acceptance open

- PR #32 adds the standard Frappe Helpdesk adapter using HD Ticket and HD Service Level Agreement metadata.
- Dashboard aggregates ticket creation, current Open/Paused backlog, resolved cohort, native resolution_time and Fulfilled/Failed SLA outcomes.
- SLA outcomes/no-SLA counts use the rolling 30-day created-ticket cohort; only Fulfilled/Failed are eligible for compliance. Due/paused states are excluded.
- Ticket/SLA DocType permissions are checked independently; the payload contains aggregates only.
- Monday–Saturday is the agreed initial assumption, but the active Helpdesk SLA's working hours, holiday list and timezone remain authoritative.

**Remaining:** confirm the exact Frappe v16.5 patch and installed ERPNext/Helpdesk versions; inspect actual Sales User/Manager permitted fields at the installed Helpdesk release's permlevels; validate each active SLA calendar on the target site. PR #42's fail-closed field-level guard is merged. The exact v16.5.0 reference lane is testing Helpdesk v1.30.2; its D3 fields are permlevel 0, unlike the v1.31.1 schema. Target-site version, read-only role and active SLA calendar acceptance remain. Do not treat CI as pilot acceptance.

Specification: [D3 Service Resolution/SLA](../specs/2026-11-01-pillar-d3-service-resolution-sla.md).

## H — Highlights: event-driven alerts

**Status:** High-value Quotation signals and per-company threshold implementation are merged (PR #45); PR #49 merged the row-currency auto-fetch/display fix. Every enabled Company still needs an approved threshold or explicit fallback approval during pilot configuration. VIP proposal-link tracking remains gated on privacy/consent and retention approval.

- High-value submitted Quotations use the Company's base total and an explicit Company-specific threshold when configured; the legacy site-wide threshold is a fallback only on exact currency match. No implicit FX conversion.
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
