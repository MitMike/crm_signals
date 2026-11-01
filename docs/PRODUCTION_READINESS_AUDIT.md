# CRM Signals — Production-readiness audit

**Audit date:** 2026-11-01  
**Repository:** MitMike/crm_signals  
**Base:** `main` at `69140a243ed2bf6b49f24a8265948a21899f2bb4` (PR #21 and subsequent documentation updates merged)  
**Implementation under audit:** [PR #19](https://github.com/MitMike/crm_signals/pull/19), validated head a90315be7ef37e2dceeacb9b4e9b77d5d31df131, merged as a49591947a89b011cc1770be176c1f11571b131b  
**Decision:** **Not approved for production sign-off.** PR #19 is merged and its CI passed; target-site acceptance and the remaining P1 reliability work are still outstanding.

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
| Frappe v15/v16 call document permission hooks with different keyword names; v16 requires explicit boolean decisions. | Accept both `permission_type` and `ptype`, enforce DocType role permission first, and return explicit decisions before applying row restrictions (ADR-039). | Bench integration tests passed on v15 and v16. |
| Duplicate event insertion can lose a read-before-insert race and Frappe wraps a unique-key collision as `UniqueValidationError`. | PR #23 reloads the winning row with a current locking document read after a unique-key collision and adds a deterministic two-connection Bench test (ADR-043). | Python quality passed on an earlier PR #23 head; final test and both v15/v16 Bench jobs are pending. |
| Browser login can expose the session cookie before redirecting to Desk, and v16 Int input commits its model value on change. | Wait for the version-appropriate `/app` or `/desk` route, commit the field change, and await the preset transition (ADR-040). | Final v16 Playwright suite passed. |
| Release procedure was spread across guidance and assumptions. | Add a deployment/rollback runbook and link it from the administrator guide. | Target-site rehearsal remains outstanding. |

Decisions are recorded in ADR-034 through ADR-040, in addition to the earlier settings and reliability ADRs.

## Remaining production blockers

### P0 — target-site acceptance

1. **Installation/upgrade:** PR #21 passed a real `bench migrate` rehearsal from the pre-source-event-key schema with two historical CRM Signal rows on Frappe v15 and v16. Target-site upgrade with a real backup, restore and rollback rehearsal remains required.
2. **Permission matrix:** Bench tests cover important parent-read, signal-read and list-query cases. The intended site's actual Sales User, Sales Manager, System Manager, non-sales and User Permission matrix still needs testing across list, direct form, API, report, export and print.
3. **Webhook operations:** Provision a dedicated integration System User and least-privilege create role; confirm HTTPS, gateway rate limiting, secret storage, monitoring and rotation.
4. **Financial acceptance:** Reconcile D2 invoice, Payment Entry, POS, receivable and overdue figures to native ERPNext reports by currency.
5. **Deployment rehearsal:** Run the documented backup/migrate/smoke/rollback process with the target site's real backup and restore procedure, workers and process manager.

### P1 — reliability work intentionally deferred

1. **Signal outbox/reconciliation:** Source hook failures are logged without blocking the source business transaction. A transient CRM Signal write failure can still lose an event; guaranteed delivery requires a durable outbox or reconciliation process.
2. **Realtime retry:** Per-recipient failures are isolated and logged but not automatically retried.
3. **Digest concurrency:** PR #23 adds a Settings-singleton row lock, a fresh per-recipient marker read before queueing and a two-worker Bench test (ADR-044). Keep open until the v15/v16 tests pass; target-site scheduler topology and mail-queue behavior still need validation.
4. **Idempotency race:** PR #23 adds a deterministic two-connection API-handler race test and changes duplicate recovery to a current locking document read. Keep open until both supported Frappe Bench lanes pass. The pre-feature-schema upgrade rehearsal passed in PR #21 on v15/v16.
5. **Multi-company threshold:** One site-wide Company-currency threshold is supported. Sites with different Company base currencies need an approved per-company threshold or conversion policy before enabling signals for all companies.

### P2 — roadmap dependencies

- D3 Service Resolution/SLA remains disabled until the installed support app, ticket lifecycle, SLA pause rules, business calendar and permissions are verified.
- H/E/V/A roadmap slices remain gated by verified source adapters, retention/privacy decisions and a server-owned metric registry. Arbitrary generated SQL remains prohibited.

## Validation status

PR #21 was merged as `72833cd383811d7c9be591206647b2e0b1f3fbd9` after all checks passed on final head `3578dd566683d2dff4c9f663b733e838b6627e25`, including the v15/v16 legacy-schema migration rehearsal. PR #19 was merged as `a49591947a89b011cc1770be176c1f11571b131b` after all checks passed on validated head `a90315be7ef37e2dceeacb9b4e9b77d5d31df131`:

- [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41274491111) — passed, including Python 3.10/3.11/3.12/3.14, lint, formatting and static checks.
- [Bench Integration and E2E](https://github.com/MitMike/crm_signals/actions/runs/41274491113) — passed on Frappe/ERPNext v15 and v16, including `bench run-tests --app crm_signals` and Playwright on v16.
- [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41274491117) — passed.
- All 16 individual check-runs on that head completed successfully; the duplicate workflow runs also passed.

Passing CI validates the tested clean-install, browser and CI-level legacy-schema upgrade paths. It does not close any target-site P0 item or prove backup/restore/rollback behavior on the intended site.

## Release decision rule

PR #19 merge and green CI are complete. CRM Signals may be called production-ready only after:
- the true upgrade/migration path is verified on supported Frappe versions;
- P0 target-site acceptance items have evidence and an owner;
- remaining P1 reliability limitations are either fixed or explicitly accepted by the site's business/technical owner.

See [Deferred follow-ups](FOLLOW_UPS.md), [Deployment runbook](DEPLOYMENT_RUNBOOK.md), [Administrator guide](ADMIN_GUIDE.md) and [Project progress](PROGRESS.md).
