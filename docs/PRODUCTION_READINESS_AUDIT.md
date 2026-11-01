# CRM Signals — Production-readiness audit

**Audit date:** 2026-11-01  
**Repository:** MitMike/crm_signals  
**Base:** main at f51fbce19b7d1e84cfa6f3ab26118f2977a8fe40 (PR #18 merged)  
**Implementation under audit:** PR #19, branch feat/settings-and-core-reliability, current audited revision 1d47b03ae26c45a638b787e763576dbf374c025b  
**Decision:** **Not yet approved for production sign-off.** PR #19 is open; CI and target-site acceptance must complete before release.

## Scope reviewed

- Frappe app hooks, scheduler registration, DocType metadata and Settings singleton.
- CRM Signal validation, event identity, Quotation/Opportunity hooks and external ingestion API.
- Direct-document permission hooks, list-query conditions, realtime recipient resolution and digest recipient context.
- Daily digest query volume, currency rendering, retry markers and scheduler behavior.
- Python/JavaScript quality gates, unit tests, Bench workflow, Playwright E2E workflow and security scan.
- Administrator guide, implementation specifications, ADR register, progress record and deferred follow-ups.

## Findings fixed in PR #19

| Finding | Change | Evidence expected |
|---|---|---|
| Realtime recipient selection used owner/assignment without proving access to the parent and CRM Signal. | Require both linked Lead/Customer read permission and CRM Signal read permission; fail closed on errors. | Unit and Bench permission tests. |
| CRM Signal list query unconditionally included owner = current_user, allowing linked records to appear even when User Permissions denied the parent. | Owner-only list clause now applies only to unlinked signals; linked records require a permission-readable owned/assigned parent. | Unit test and Bench User Permission/list parity test. |
| Fresh installation and missing-settings fallback enabled the master switch and external ingestion. | Both now default off; presets do not activate the app. | Settings fallback unit test and DocType defaults. |
| Digest could include an unlimited number of expiring Quotations. | Fetch at most 101, display at most 100, and show 100+ with an explicit truncation notice. | Digest query and rendering tests. |
| API idempotency had only mocked coverage. | Add Bench-backed tests for same-user duplicate POSTs, one notification per event, per-user source namespaces, unique-key enforcement and multiple legacy null keys. | Bench integration test suite on v15 and v16. |
| Dashboard JavaScript contained an unused catch binding. | Remove the unused binding. | ESLint. |
| Release procedure was spread across guidance and assumptions. | Add a deployment/rollback runbook and link it from the administrator guide. | Target-site rehearsal remains outstanding. |

Decisions are recorded in ADR-034 through ADR-037, in addition to the earlier settings and reliability ADRs.

## Remaining production blockers

### P0 — target-site acceptance

1. **Installation/upgrade:** CI installs the current app on fresh Bench sites. A true upgrade from the pre-source-event-key schema with existing CRM Signal rows still needs validation on both supported Frappe versions.
2. **Permission matrix:** Bench tests cover important parent-read, signal-read and list-query cases. The intended site's actual Sales User, Sales Manager, System Manager, non-sales and User Permission matrix still needs testing across list, direct form, API, report, export and print.
3. **Webhook operations:** Provision a dedicated integration System User and least-privilege create role; confirm HTTPS, gateway rate limiting, secret storage, monitoring and rotation.
4. **Financial acceptance:** Reconcile D2 invoice, Payment Entry, POS, receivable and overdue figures to native ERPNext reports by currency.
5. **Deployment rehearsal:** Run the documented backup/migrate/smoke/rollback process with the target site's real backup and restore procedure, workers and process manager.

### P1 — reliability work intentionally deferred

1. **Signal outbox/reconciliation:** Source hook failures are logged without blocking the source business transaction. A transient CRM Signal write failure can still lose an event; guaranteed delivery requires a durable outbox or reconciliation process.
2. **Realtime retry:** Per-recipient failures are isolated and logged but not automatically retried.
3. **Digest concurrency:** The Settings marker and email queue request are committed per recipient. Concurrent scheduler workers have not been proven safe; add a per-recipient lock or unique delivery record if the target site's worker topology permits overlapping runs.
4. **Idempotency race and upgrade:** Bench tests cover normal duplicate requests and the unique key, but concurrent duplicate inserts and migration from the pre-feature schema remain open.
5. **Multi-company threshold:** One site-wide Company-currency threshold is supported. Sites with different Company base currencies need an approved per-company threshold or conversion policy before enabling signals for all companies.

### P2 — roadmap dependencies

- D3 Service Resolution/SLA remains disabled until the installed support app, ticket lifecycle, SLA pause rules, business calendar and permissions are verified.
- H/E/V/A roadmap slices remain gated by verified source adapters, retention/privacy decisions and a server-owned metric registry. Arbitrary generated SQL remains prohibited.

## Validation status

PR #19's current CI is still running at the audited revision. Record the completed run IDs and final conclusions here before merge. Passing CI is necessary but does not close any target-site P0 item.

## Release decision rule

CRM Signals may be called production-ready only after:
- PR #19 is merged with all required checks green;
- the true upgrade/migration path is verified;
- P0 target-site acceptance items have evidence and an owner;
- remaining P1 reliability limitations are either fixed or explicitly accepted by the site's business/technical owner.

See [Deferred follow-ups](FOLLOW_UPS.md), [Deployment runbook](DEPLOYMENT_RUNBOOK.md), [Administrator guide](ADMIN_GUIDE.md) and [Project progress](PROGRESS.md).
