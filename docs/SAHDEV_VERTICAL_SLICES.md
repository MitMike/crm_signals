# S.A.H.D.E.V. vertical-slice roadmap

This roadmap follows the product capabilities described in the Sahdev Signals presentation. Each slice should be independently usable, permission-aware, tested, and deployable. Avoid implementing a dashboard card or UI shell before its underlying metric and source are real.

## D — Dashboard: Executive Compass

### D1. Sales Compass (implemented in this branch)
- Lead inflow for the last 30 days and active Lead count.
- Active Opportunity count and stage distribution.
- Pipeline amount grouped by transaction currency; never sum unlike currencies.
- Recent Opportunities with a direct Desk drill-down.
- Lead and Opportunity reads use Frappe permission-aware list APIs.

### D2. Billing realization (implemented in this branch)
- Invoiced: submitted, non-return Sales Invoice grand totals posted in the last 30 days, grouped by invoice currency.
- Outstanding: current positive outstanding amounts on submitted, non-return Sales Invoices, grouped by the Sales Invoice party-account currency (the currency used by ERPNext's outstanding_amount field).
- Customer receipts: submitted Receive Payment Entries for Customer parties in the last 30 days, grouped by receiving-account currency. This includes allocated and advance/unallocated receipts.
- POS receipts: submitted POS Sales Invoice paid_amount in the last 30 days, grouped by invoice currency. Kept separate from Payment Entry receipts.
- Overdue: count and top eight submitted, non-return invoices with a positive outstanding amount and a due date before today.
- Every source uses permission-aware Frappe list APIs. Unlike currencies are never added together.
- Scope note: Payment Entry receipts are cash received, not necessarily cash allocated to an invoice. POS receipts are presented separately. Refunds, credit notes and advance applications are not re-labelled as customer cash receipts.

### D3. Service resolution / SLA
- Add ticket volume and resolution metrics from the installed support-ticket and SLA configuration.
- Confirm what constitutes an SLA breach and which timestamp represents resolution on the target site.
- Keep unavailable or unconfigured SLA data visibly unavailable; do not substitute generic ticket counts.

## H — Highlights: event-driven alerts
- Add real-time event triggers for high-value submitted quotations and VIP proposal-link opens.
- Deliver WebSocket alerts to the configured escalation recipients, not every logged-in user.
- Make threshold and escalation routing configurable; record why a recipient received an alert.
- Test duplicate events, retries, recipient permissions, and alert fatigue controls.

## A — Analysis: natural-language questions
- Start with a small set of approved sales questions and a metric/field registry.
- Support questions such as quotations above a configured threshold with no recorded interaction during a chosen period.
- Return the computed answer, filters, period, and source links so results can be checked.
- Do not execute model-generated SQL. Resolve prompts through approved query definitions and permission-aware Frappe queries.

## E — Explorer: customer interaction timeline
- Provide a chronological, customer-scoped activity stream opened from a Signal, Highlight, Lead, Customer, or Opportunity.
- Normalize activity references from calls, WhatsApp, emails, quotations, and CRM records.
- Show a source-specific detail link only where the integration actually provides one.
- Respect permissions for every source record; missing integrations should not create fake timeline entries.

## V — Vault: historical intelligence
- Store versioned daily snapshots of approved signal and operating metrics.
- Define retention, correction, and audit rules before persisting snapshots.
- Support trend comparisons such as response-latency improvement only when the underlying timestamps are available and validated.
- Keep historical snapshots attributable to their source and calculation version.

## Delivery rule

A vertical slice is complete only when its data contract, permission behavior, UI, tests, operational configuration, and documentation are all present. A visible metric must be backed by real source data and a stated calculation. Cross-department dashboard cards are added only after their source slices (D2 and D3) are complete.
