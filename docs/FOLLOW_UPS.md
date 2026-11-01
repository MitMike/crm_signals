# CRM Signals — Deferred follow-ups and production acceptance

This file records known work that is intentionally not represented as complete. Revisit an item when its trigger or dependency is satisfied.

**Ownership convention:** P0 target-site items belong to the site administrator/implementation lead with the relevant security or finance owner; P1 engineering items belong to CRM Signals maintainers; site-specific configuration items belong to the Sales Manager/business owner; P2 roadmap items belong to the product owner. Close an item only with the evidence described below.

## P0 — required before production sign-off

- [ ] **Target-site preflight and acceptance.** Record Frappe/ERPNext versions, installed apps, Company currencies, timezone, workflows, custom fields and role matrix. Run Pilot import, migrate, scheduler, email, realtime, dashboard and rollback smoke tests.
- [ ] **Permission parity.** Verify Sales User, Sales Manager, System Manager and non-sales users across list, direct form, API, report, export and print. Notifications are not an authorization grant. The scheduled digest now queries Leads and Quotations separately under each recipient's user context; confirm this behavior with the target site's actual user permissions.
- [ ] **D2 financial reconciliation.** Compare invoices, Payment Entry receipts, separate POS receipts and party-account-currency receivables to native ERPNext reports, by currency.
- [ ] **Webhook operations.** Provision a dedicated integration System User, least-privilege create access, TLS, gateway rate limiting, monitoring, secret rotation and secure secret storage.
- [ ] **Target-site deployment rehearsal.** The generic backup, migration, smoke-test and rollback procedure is documented in [Deployment Runbook](DEPLOYMENT_RUNBOOK.md); execute it with the intended site's actual backup, restore, app revision and process manager before sign-off.

## P1 — engineering reliability improvements

- [ ] **Durable signal outbox/reconciliation.** Current source hooks log unexpected CRM Signal creation failures and preserve the source Quotation/Opportunity transaction. This avoids blocking sales operations, but a transient DB failure can still lose the generated signal. Add a transactional outbox or scheduled reconciliation with retry/backoff and an admin-visible failed-event queue before claiming guaranteed delivery.
- [ ] **Durable realtime retry.** Realtime notification failures are isolated and logged per recipient, but they are not yet retried automatically. Decide whether the site's operational requirement justifies an outbox/notification attempt record.
- [ ] **Digest concurrency proof.** The current sendmail queue request and per-recipient Settings marker are written within one Frappe transaction. Verify this behavior and simultaneous scheduler execution on supported Frappe versions. Add a per-recipient lock or unique delivery record if concurrent workers can process the same recipient/date before either commits.
- [ ] **API idempotency contract coverage.** Bench-backed tests verify same-user duplicate POST deduplication, one notification per event, cross-user source namespacing, unique-key enforcement and multiple legacy rows with null keys. PR #21's pre-feature-schema upgrade rehearsal passed on Frappe v15 and v16. Concurrent duplicate-request load testing remains outstanding. Concurrent duplicate-request load testing remains outstanding.

## P1 — site-specific configuration decisions

- [ ] **Multi-company threshold policy.** The first version uses one site-wide threshold currency. Companies with different base currencies need a per-company threshold table or an explicitly approved conversion policy before enabling all company events.
- [ ] **Opportunity and Lead semantics.** Confirm the exact trigger statuses and terminal Lead statuses from the live site's workflows. Confirm the Lead modified timestamp is an acceptable proxy for attention.
- [ ] **Digest policy.** Confirm timezone, delivery time, additional recipients, mail-queue behavior and stale window with the Sales Manager/business owner.

## P2 — S.A.H.D.E.V. roadmap

- [ ] **D3 Service Resolution/SLA:** discover the installed support app, ticket DocType, lifecycle, SLA deadlines, pause rules, business calendar and permissions before implementing an adapter.
- [ ] **H Highlights:** VIP alert rules and first-party proposal link tracking only after stable event IDs, scanner exclusion, retention and privacy/consent approval.
- [ ] **E Explorer:** inventory configured integrations and implement source adapters only for verified sources.
- [ ] **V Vault:** approve metric definitions, source visibility and retention before enabling aggregate snapshot scheduling.
- [ ] **A Analysis:** build a server-owned versioned metric registry and constrained intent mapping. Arbitrary generated SQL remains prohibited.

## Operating rule

Do not close a follow-up because code compiles or a mocked unit test passes. Close it only with evidence from the relevant unit/Bench/E2E tests and, for site-dependent items, a recorded target-site validation result.
