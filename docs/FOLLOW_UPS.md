# CRM Signals — Deferred follow-ups and production acceptance

This file records known work that is intentionally not represented as complete. Revisit an item when its trigger or dependency is satisfied.

**Ownership convention:** P0 target-site items belong to the site administrator/implementation lead with the relevant security or finance owner; P1 engineering items belong to CRM Signals maintainers; site-specific configuration items belong to the Sales Manager/business owner; P2 roadmap items belong to the product owner. Close an item only with the evidence described below.

## P0 — required before production sign-off

- [ ] **Target-site preflight and acceptance.** Use the evidence template in [Target-Site Acceptance Kit](TARGET_SITE_ACCEPTANCE.md). Record Frappe/ERPNext versions, installed apps, Company currencies, timezone, workflows, custom fields and role matrix. Run Pilot import, migrate, scheduler, email, realtime, dashboard and rollback smoke tests.
- [ ] **Permission parity.** Verify Sales User, Sales Manager, System Manager and non-sales users across list, direct form, API, report, export and print. Notifications are not an authorization grant. PR #41 requires read access to the CRM Signal, linked Lead/Customer and originating source DocType before realtime content is queued. The scheduled digest queries Leads and Quotations separately under each recipient's user context; confirm both paths with the target site's actual permissions.
- [ ] **D2 financial reconciliation.** Compare invoices, Payment Entry receipts, separate POS receipts and party-account-currency receivables to native ERPNext reports, by currency.
- [ ] **Webhook operations.** Provision a dedicated integration System User, least-privilege create access, TLS, gateway rate limiting, monitoring, secret rotation and secure secret storage.
- [ ] **Target-site deployment rehearsal.** The generic backup, migration, smoke-test and rollback procedure is documented in [Deployment Runbook](DEPLOYMENT_RUNBOOK.md); execute it with the intended site's actual backup, restore, app revision and process manager before sign-off.

## P1 — engineering reliability improvements

- [x] **Durable signal outbox/reconciliation core.** PR [#26](https://github.com/MitMike/crm_signals/pull/26) merged as `b0364a74affa823977af74d1907781d1533e60c0`. The final synchronized head `222e70ec71164dab4448f7319525042323a357b4` passed Quality Checks, Security Scanning and Bench Integration/E2E on Frappe v15/v16. Source event/outbox persistence is transactional; delivery is queued after commit; bounded retries, scheduled recovery and a System Manager-visible Failed state are included. **Remaining:** PR [#38](https://github.com/MitMike/crm_signals/pull/38) adds a POST-only System Manager + outbox-read-gated replay action, preserves attempt history, records replay audit data and queues the existing idempotent worker after commit. Final v15/v16 validation and merge remain. This does not provide durable realtime notification retry.
- [ ] **Durable realtime retry.** Realtime notification failures are isolated and logged per recipient, but they are not yet retried automatically. Decide whether the site's operational requirement justifies an outbox/notification attempt record.
- [x] **Digest concurrency proof.** PR #23 merged as `d75b7f3`. The Settings-singleton row lock and per-recipient marker recheck passed the two-worker Bench test on Frappe v15 and v16; v16 Playwright also passed. Live scheduler topology, mail-provider behavior and recipient policy still require target-site validation.
- [x] **API idempotency contract coverage.** Bench-backed tests cover same-user duplicate POST deduplication, one notification per event, cross-user source namespacing, unique-key enforcement, legacy null keys and the deterministic two-connection insert race. The race test and migration rehearsal passed on Frappe v15 and v16 in PR #23/#21; quality, security and v16 Playwright checks also passed. Broader HTTP gateway/load testing remains a separate optional stress test.

## P1 — site-specific configuration decisions

- [ ] **Multi-company threshold policy.** PR #34 adds Company-specific threshold rows with currencies derived from Company metadata. The legacy site-wide threshold is used only when it exactly matches the Quotation Company's base currency; no implicit FX conversion. CI passed on the prior branch head; rebased CI/merge and target-site approval for each enabled Company remain.
- [ ] **Opportunity and Lead semantics.** Confirm the exact trigger statuses and terminal Lead statuses from the live site's workflows. Confirm the Lead modified timestamp is an acceptable proxy for attention.
- [ ] **Digest policy.** Confirm timezone, delivery time, additional recipients, mail-queue behavior and stale window with the Sales Manager/business owner.

## P2 — S.A.H.D.E.V. roadmap

- [ ] **D3 target-site acceptance:** the standard Frappe Helpdesk adapter merged in PR #32 and passed Frappe v15/v16 CI. Record the exact Frappe v16.5 patch, ERPNext and Helpdesk versions; verify Sales User/Manager HD Ticket/SLA DocType and field-level read permissions; confirm each active SLA's Monday–Saturday schedule, hours, holiday list and timezone. A fail-closed field-level guard is in validation. CI is not site acceptance.
- [ ] **H Highlights:** VIP alert rules and first-party proposal link tracking only after stable event IDs, scanner exclusion, retention and privacy/consent approval.
- [ ] **E Explorer:** inventory configured integrations and implement source adapters only for verified sources.
- [ ] **V Vault:** approve metric definitions, source visibility and retention before enabling aggregate snapshot scheduling.
- [ ] **A Analysis:** build a server-owned versioned metric registry and constrained intent mapping. Arbitrary generated SQL remains prohibited.

## Operating rule

Do not close a follow-up because code compiles or a mocked unit test passes. Close it only with evidence from the relevant unit/Bench/E2E tests and, for site-dependent items, a recorded target-site validation result.
