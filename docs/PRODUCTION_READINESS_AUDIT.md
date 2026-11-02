# CRM Signals — Production-readiness audit

**Audit date:** 2026-11-02  
**Repository:** MitMike/crm_signals  
**Base:** `main` at `7904a70fec15fc01caf512977b9aca42477dc305` (PR #79 bug/fix registers merged; PR #74 immutable deployment revision procedure merged; latest functional baseline remains `c5720bf`)  
**Implementation under audit:** PRs #13/#15/#19/#21/#23/#26/#32/#38/#42/#44/#45/#49/#50/#51/#53/#54/#55/#56/#57/#59/#60/#61/#62/#63/#65/#66/#67/#68/#69/#70 merged; PR #69 (POS settlement fixture) is CI-verified as `efe7872`; PR #70 (read-only target-site preflight) is CI-verified as `13341b7`; PR #71 (High-Value Quote source drill-down) merged as `c5720bf`; final head `df0c273` passed all required Quality, Security, Python, Frappe v15/v16 Bench including Playwright, and pinned Frappe v16.5.0 checks; latest main baseline `c5720bf`  
**Decision:** **Not approved for production sign-off.** PR #19, PR #21 and PR #23 are merged; supported-version CI passes. Target-site acceptance and the roadmap's external discovery/policy inputs remain outstanding. Durable realtime retry is implemented on PR #54 and CI-verified on head `d2ac43e`; target-site Redis/worker recovery evidence remains open. The transactional outbox and audited Failed-row replay are already implemented.

## 2026-11-02 follow-up status

- **D1/D2 query compatibility:** PR #63 adds and merges a read-only Sales Compass query-contract smoke on the Frappe v15/v16 Bench matrix and pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane. Final-head Quality, Security, Semgrep, Python, Bench and pinned-target checks passed. This does not replace target-site role acceptance or financial reconciliation.
This is a historical audit of the earlier PR #19/#23 baseline; main now also contains the PR #67 synthetic D1/D2 aggregate fixture and PR #68 documentation reconciliation. PR #70 added the read-only target-site preflight report and merged as `13341b7` after all final-head checks passed; target-site execution remains open. PR #69 adds a real ERPNext POS Profile/Mode of Payment and submitted POS invoice settlement to the disposable D2 fixture; synchronized final head `33b750a` passed all 15 checks and merged as `efe7872`. PR #71 adds permission-gated High-Value Quote source drill-down. Three final-head attempts (`cbe8898`, `007fcd4`, `047a903`) failed only Prettier formatting for `e2e/sahdev-dashboard.spec.ts`; two manual revisions did not resolve it. ADR-071 records the stop decision: no speculative edits or bypass; revisit only when the exact locked Prettier 3.2.5 output can be generated in a CI-equivalent environment or retrieved as an exact CI diff. H-AC11 remains code-complete, not CI-verified. The following later changes supersede the affected open findings. PR #62 reconciles the Explorer and policy-gated roadmap status; PR #63 merges the read-only D1/D2 Bench query-contract smoke. This smoke is not a financial reconciliation.

- **Signal outbox:** transactional source-event outbox merged in PR #26; audited System Manager replay for terminal Failed rows merged in PR #38. The old P1 replay gap is closed; target-site backup/restore and operational monitoring remain P0 acceptance.
- **Realtime authorization and retry:** source-document read checks merged in PR #44. PR #54 implements the ADR-053 per-recipient ledger, stable delivery ID, bounded retry, permission recheck and active-session deduplication. `Attempted` means the after-commit callback was queued, not that Redis or a browser confirmed delivery. Required CI passed on head `d2ac43e`; target-site Redis/worker recovery tests remain open.
- **Multi-company quotation thresholds:** Company-specific explicit threshold rows merged in PR #45 as `ff434bdf`; all 16 required checks passed on head `84783d15`. No implicit FX conversion; each enabled Company still needs an approved amount or explicit approval of the exact-currency legacy fallback.
- **D3 Helpdesk:** standard adapter merged in PR #32 and field-level fail-closed guard merged in PR #42. Target-site versions, Sales-role read-only permissions and active SLA calendar remain unverified.
- **Operator kit:** added a beginner-friendly D3 Support & SLA discovery worksheet, a Frappe v16.5.0 support configuration guide, and the target-site acceptance checklist. The discovery script is metadata-only; the pilot operator still needs to run it and record the site's exact app versions and policy.
- **Exact target compatibility:** PR #50 merged the path-filtered Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 reference CI lane. The final-head target run passed: [Bench target workflow](https://github.com/MitMike/crm_signals/actions/runs/41363739985). The first v1.31.1 attempt failed during Helpdesk post-install because the Notification Type controller is absent from exact Frappe v16.5.0; ADR-055/056 were superseded by ADR-057, which records the final v1.28.0 pin. The Helpdesk v1.30.2 installed but its after-migrate asset build failed because @framework/ui links to frappe/ui, absent from the Frappe v16.5.0 tag. The v1.31.1 tag additionally expects Notification Type. ADR-057 pins v1.28.0, whose required D3 fields remain at permlevel 0 and whose desk build does not import @framework/ui. The v1.30.2 D3 aggregate smoke exposed an app bug: the adapter treated the system `creation` audit column as a DocType field. PR #50 now checks `frappe.db.has_column` and adds a regression test that models the system column correctly; the first v1.28.0 target lane passed Helpdesk installation, schema/role checks, the real D3 aggregate smoke test, CRM Signals schema-upgrade, full application asset build and Bench tests on the code head. A documentation-only ADR evidence wording correction triggered final-head revalidation, which has passed Helpdesk install/schema/role, D3 aggregate smoke, CRM Signals upgrade, full asset build and Bench tests; standard v15/v16 checks passed and PR #50 is merged. This is not evidence of the pilot site's exact installed versions.

## 2026-11-02 follow-up after PR #65 and PR #67

- **D2 source permissions:** PR #65 merged as `0cfeda4fb39f79722fdf733abd06a3460ebcdd4d`. Payment Entry customer receipts are now evaluated independently of Sales Invoice read access; a query-level invoice `PermissionError` clears partial invoice metrics without suppressing permitted receipts. Final-head Quality, Security/Semgrep, Python, Bench v15/v16 and pinned Frappe v16.5.0 checks passed.
- **D1/D2 aggregate values:** PR #67 merged as `84ab2ce0b4ce1a9614882635e4c085092cf2a0c5`; final head `cfd7c5ec64786e394374d31ba7b89354565a2070` passed all 15 check runs. The disposable fixture checks Lead/Opportunity and submitted invoice/payment aggregates, INR/USD and party-account currency grouping, overdue/receipt/POS filters, and Payment Entry-only read access. Synthetic records/permissions are rolled back. POS settlement, native-report reconciliation and target-site role acceptance remain outside CI.
- **Current status:** the historical audit baseline above predates PR #65/#67. These merges improve reference-stack evidence but do not change the production decision: **not approved for production sign-off** until the P0 target-site acceptance gates below have recorded evidence and owner approval. The latest functional baseline is `84ab2ce`; the open PR #68 is documentation-only.

## Current audit status after PR #5, PR #74 and PR #79

The main branch is `7904a70`; PRs #13/#14/#15, #71, #73, #5, #74 and #79 are merged with their recorded CI evidence. PR #73 was a documentation-only H-AC11/ADR-073 reconciliation. PR #5 upgraded actions/checkout v4 to v7; refreshed final head `8856f35` passed all 17 checks, including Quality, Security, Python, dependency audits, Frappe v15/v16 Bench and pinned Frappe v16.5.0 / Helpdesk 1.28.0. PR #74 merged as `1b57003` with immutable deployment-SHA instructions; PR #79 merged as `7904a70` with the durable bug/fix registers. The latest functional baseline remains `c5720bf`; these documentation/CI maintenance merges did not change application runtime behavior. PR #76's current head `1f0795a` adds fail-closed changed-path gates, workflow/workspace/migration/packaging coverage, static selector-contract tests, and a main-only Quality push trigger after duplicate feature-branch runs were observed. Its fresh final-head Quality, Security, Bench v15/v16 and pinned Frappe v16.5.0 cycle is pending. PR #75 and #78 passed checks on heads `16c9c77` and `9d31b7b`, but each is one commit behind main and needs refresh/retest; PR #80 passed Quality, Security and Bench v15/v16 and is up to date with main. None is pilot-verified. Production sign-off remains blocked on P0 target-site acceptance and owner approvals.

## Scope reviewed

- Frappe app hooks, scheduler registration, DocType metadata and Settings singleton.
- CRM Signal validation, event identity, Quotation/Opportunity hooks and external ingestion API.
- Direct-document permission hooks, list-query conditions, realtime recipient resolution and digest recipient context.
- Daily digest query volume, currency rendering, retry markers and scheduler behavior.
- Python/JavaScript quality gates, unit tests, Bench workflow, Playwright E2E workflow and security scan.
- Administrator guide, implementation specifications, ADR register, progress record and deferred follow-ups.

## Findings fixed in PR #19 and PR #23

| Finding | Change | Evidence expected |
|---|---|---|
| Realtime recipient selection used owner/assignment without proving access to the parent and CRM Signal. | Require both linked Lead/Customer read permission and CRM Signal read permission; fail closed on errors. | Unit and Bench permission tests. |
| CRM Signal list query unconditionally included owner = current_user, allowing linked records to appear even when User Permissions denied the parent. | Owner-only list clause now applies only to unlinked signals; linked records require a permission-readable owned/assigned parent. | Unit test and Bench User Permission/list parity test. |
| Fresh installation and missing-settings fallback enabled the master switch and external ingestion. | Both now default off; presets do not activate the app. | Settings fallback unit test and DocType defaults. |
| Digest could include an unlimited number of expiring Quotations. | Fetch at most 101, display at most 100, and show 100+ with an explicit truncation notice. | Digest query and rendering tests. |
| API idempotency had only mocked coverage. | Add Bench-backed tests for same-user duplicate POSTs, one notification per event, per-user source namespaces, unique-key enforcement and multiple legacy null keys. | Bench integration test suite on v15 and v16. |
| Dashboard JavaScript contained an unused catch binding. | Remove the unused binding. | ESLint. |
| Frappe v15/v16 call document permission hooks with different keyword names; v16 requires explicit boolean decisions. | Accept both `permission_type` and `ptype`, enforce DocType role permission first, and return explicit decisions before applying row restrictions (ADR-039). | Bench integration tests passed on v15 and v16. |
| Duplicate event insertion can lose a read-before-insert race and Frappe wraps a unique-key collision as `UniqueValidationError`. | PR #23 reloads the winner with a current locking document read and adds a deterministic two-connection API-handler Bench test (ADR-043). | Passed on Frappe v15 and v16 in PR #23; one created response, one deduplicated response and one notification dispatch. |
| Concurrent digest workers could both queue the same recipient/date before either updated the marker. | PR #23 locks the Settings singleton, rechecks each recipient/date marker and writes system-owned status through `db_set` in the Email Queue transaction (ADR-044). | Two-worker Bench test passed on Frappe v15/v16; target-site scheduler and mail-provider acceptance remains open. |
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

1. **Signal outbox/reconciliation:** The transactional outbox and audited Failed-row replay are implemented in PRs #26/#38 and CI-verified. Verify scheduler operation, failure monitoring and backup/restore on the target site.
2. **Realtime retry:** PR #54 merged as `37ce6003c9459f1b391de5dff8354e4bfc04cb9b`. Final synchronized head `f1cbd3e92946a4a5513b7555396cada4491fdd3e` passed all eight required checks plus the exact Frappe v16.5.0/ERPNext v16.5.0/Helpdesk v1.28.0 lane. The per-recipient ledger, stable IDs, bounded retry, permission rechecks and active-session duplicate suppression are CI-verified. PR #55 merged the staging fault-injection checklist for Redis outage, worker restart, scheduler recovery and permission revocation. Those checks remain unexecuted on the target site; no human-delivery guarantee is claimed.
3. **Multi-company threshold:** Implementation is merged in PR #45. Each enabled Company still needs a business-approved amount in its base currency or explicit approval of the exact-currency legacy fallback; there is no implicit FX conversion.

### P2 — roadmap dependencies

- D3 Service Resolution/SLA implementation and field-level guard are merged; pilot acceptance still requires the installed Helpdesk schema, ticket lifecycle, SLA pause rules, business calendar and permissions to be verified.
- H/E/V/A roadmap slices remain gated by verified source adapters, retention/privacy decisions and a server-owned metric registry. Arbitrary generated SQL remains prohibited.

## Validation status

PR #23 was merged as `d75b7f3591d2a863b0af6b8f88ad2a91e9bfd25f` after all checks passed on final head `7ed0860fd45cdc152bb2dcc868489d46b69aefb9`:
- [Bench Integration and E2E, Frappe v15/v16 + Playwright](https://github.com/MitMike/crm_signals/actions/runs/41300667892) — passed, including concurrent API idempotency and two-worker digest queueing.
- [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41300667996) — passed.
- [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41300667997) — passed.

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
