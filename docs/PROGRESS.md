# Project Progress

**Last reviewed:** 2026-11-02  
**Repository:** [MitMike/crm_signals](https://github.com/MitMike/crm_signals)  
**Latest main:** [00e997c](https://github.com/MitMike/crm_signals/commit/00e997ce25747f24b8af9948527a1738cc6f3920) (PR #5 actions/checkout v7 dependency update merged and CI-verified); **latest functional baseline:** [c5720bf](https://github.com/MitMike/crm_signals/commit/c5720bfb3fbe8b554ec6febd549a8d5e58acc1d7)  
**Completed implementation:** PR #19 delivered settings/presets and core idempotency; PR #21 validated the legacy-schema migration; PR #23 closed concurrent API-idempotency and digest-queue races; PR #26 merged the transactional signal outbox; PR #32 merged the standard Frappe Helpdesk D3 adapter; PR #38 merged audited Failed-row replay; PR #42 merged D3 field-level permission hardening; PR #44 merged source-document notification authorization; PR #45 merged per-Company quotation thresholds; PR #49 corrected Company-currency display/fetch; PR #50 fixed the D3 system creation-column guard and added the exact Frappe v16.5.0 / Helpdesk v1.28.0 compatibility lane; PR #51 merged the Frappe v16.5 pilot operator kit; PR #53 merged the D3 aggregate fixture; PR #54 merged durable per-recipient realtime retry; PR #55 merged the staging realtime-recovery acceptance checks; PR #56 merged the pilot-status reconciliation as `704997e88a52071c15f95e5985703dc00bc10f03`; PR #57 merged the Explorer core API as `ba6317204784868a39d7c91ead01959663c9a33a`; PR #59 merged the Explorer Desk UI as `6b381fe4c7164c099cbd841086bf79566cb72ed1`; PR #61 merged five-context browser coverage and operator-runbook hardening as `6ef9642b63c24053fb437f67d9d4fb47e360c80a`; PR #62 reconciled post-Explorer status/decision records as `aeea9599b11f17bff0ef5bbd7904f44f23567e3e`; PR #63 merged read-only D1/D2 query-contract Bench smoke coverage as `0a7de966ea0639c86a59d7df28dbad343fa13488`; PR #65 fixed independent Payment Entry source permissions and merged as `0cfeda4fb39f79722fdf733abd06a3460ebcdd4d`; PR #66 reconciled the plan/progress/decision/follow-up records and merged as `e82c34f1afee054b2103d316c06a078290b97a39`; PR #67 added the D1/D2 synthetic aggregate-value fixture and merged as `84ab2ce0b4ce1a9614882635e4c085092cf2a0c5`; PR #68 reconciled D1/D2 progress and operator records and merged as `2cc7725d4e36f53d492139187fa6cd9adf663f0f`; PR #70 added the read-only target-site preflight report and merged as `13341b756e2d2a92c9432f3c50ac77594e2483e9` after all required Quality, Security, v15/v16 Bench and pinned v16.5.0 checks passed; PR #69 added the real ERPNext POS invoice settlement fixture and merged as `efe78729881390cacba343749364ceccdcb7ffb2` after all 15 final-head checks passed  ; PR #15 upgraded the locked Prettier development dependency to 3.9.10 and merged as `5fc32b0313e61eba45695ab2322b2f10140a4482` after all required contexts and dependency audits passed; PR #13 upgraded Oxlint to 1.90.0 and merged as `b466ac87613afc5b2726ef866d9a28b37ac3fab4` after all required v15/v16, quality and security contexts passed; PR #14 upgraded the locked globals development dependency to 17.13.0 and merged as `567f4586b9f7c8965f6aa00ed673962b8bc29539` after all required v15/v16, Quality and Security contexts passed; PR #71 added permission-gated High-Value Quote source Quotation drill-down and merged as `c5720bfb3fbe8b554ec6febd549a8d5e58acc1d7`; final head `df0c27363c60f4f4e6f02b25c37708db24b71ebb` passed Quality, Security, Python 3.10/3.11/3.12/3.14, Frappe v15/v16 Bench Integration/E2E and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 checks; PR #73 reconciled H-AC11 post-merge status and ADR-073, merged documentation-only as `51798f2a2711737cf67ea91c597405c224e6228f` after Quality, Security, Python 3.10/3.11/3.12/3.14 and Bench v15/v16 passed; PR #5 upgraded actions/checkout from v4 to v7, refreshed onto main, passed all 17 final-head check runs including Quality, Security, dependency audits, Frappe v15/v16 Bench and pinned Frappe v16.5.0 / Helpdesk 1.28.0, and merged as `00e997ce25747f24b8af9948527a1738cc6f3920`
**Next acceptance:** complete the target-site Frappe v16.5 pilot: exact app versions, per-Company threshold amounts/currencies, the custom read-only Helpdesk role, D1/D2 reconciliation, Helpdesk SLA calendar, scheduler/mail/realtime, and backup/restore/rollback. CI-verified work is not pilot-verified.

This file is the operational source of truth. [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) is the roadmap, [DECISIONS.md](DECISIONS.md) is the durable decision register, [FOLLOW_UPS.md](FOLLOW_UPS.md) tracks deferred issues, and [specs/](../specs/) holds feature contracts.

## Current status

## Read-only target-site preflight report — merged, CI-verified

ADR-068 is recorded. PR #70 added a non-whitelisted Bench diagnostic and unit coverage for app-version discovery, Company currency/threshold reporting without FX conversion, active Lead/Opportunity workflow states, required DocType fields, Select options, static DocPerm rows, missing D3 fields and omission of digest recipient addresses. The command performs metadata/configuration reads only; it does not read transaction, ticket or customer rows or write data.

**State:** PR #70 merged as 13341b756e2d2a92c9432f3c50ac77594e2483e9 from final head 1b1a107c8df6f9b70ea2e429c0fb5ec2b53e24a4. All final-head required Quality, Security and Frappe v15/v16 Bench contexts passed; the pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lane and Semgrep OSS also passed. This is CI-verified, not pilot-verified: an authorized operator must still run the report on the target site and complete effective-user permissions, finance reconciliation and SLA/operations acceptance. Static DocPerm is not effective-permission proof.

## H-AC11 source Quotation drill-down — merged, CI-verified; pilot acceptance open

The CRM Signals dashboard now includes a source label and routes a High-Value Quote row to its originating Quotation only when the current user can read the CRM Signal source fields and that exact Quotation. Other source types are suppressed; permission or metadata errors fail closed, preserving the existing Lead/Customer/CRM Signal fallback. API tests cover field denial, document denial, metadata lookup/field-permission failures, Quotation permission-check exceptions, exact source-name authorization and non-Quotation sources; Playwright covers the visible source label and route.

**State:** merged as `c5720bf`; code-complete and CI-verified. Final head `df0c27363c60f4f4e6f02b25c37708db24b71ebb` passed Quality, Security, Python 3.10/3.11/3.12/3.14, Frappe v15/v16 Bench Integration/E2E (including the Playwright source-route test) and the pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lane. The exact Prettier 3.9.10 output was emitted by the ADR-072 diagnostic and applied before final validation. This is CI verification only: target-site Sales User/Manager/non-sales permission checks, staging rehearsal and pilot acceptance remain open.

## Immutable deployment revision pin — PR #74 (documentation-only, CI pending)

ADR-074 corrects an operator-safety inconsistency: first installs and upgrades must use the approved full 40-character CRM Signals commit SHA, verify the detached checkout, and run `bench setup requirements` from that pinned tree before site migration. The administrator guide, deployment runbook and target-site acceptance kit now use the same procedure. PR #74 is open; the documentation is code-complete, but required CI is not yet complete. This does not claim a deployment or pilot verification.

## D2 source-permission isolation — PR #65 merged

**Status: merged and CI-verified.** The billing API now evaluates Payment Entry receipts even when Sales Invoice read access is denied, resets partial invoice results after an invoice `PermissionError`, and preserves the existing `billing.available` meaning (Sales Invoice source availability). Regression tests cover both denied Sales Invoice access and a query-level permission exception while Payment Entry remains readable. Final-head Quality, Security/Semgrep, Python 3.10/3.11/3.12/3.14, Bench v15/v16 and pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 checks passed. Merge commit: `0cfeda4`. Target-site permission parity and finance reconciliation remain pilot gates.


## D1/D2 synthetic aggregate-value fixture — PR #67 merged (CI-verified)

**Status: CI-verified.** The disposable Bench fixture completes the ERPNext setup wizard when needed, provisions a Customer and non-stock Item, creates a Lead and three Opportunities (including a terminal status and two currencies), submits four Sales Invoices and an allocated Payment Entry, and asserts D1/D2 aggregate deltas against a pre-fixture baseline. It also creates a dedicated Payment Entry reader with no Sales Invoice read permission to exercise the split-source behavior through real Frappe permissions. Final PR head `cfd7c5ec64786e394374d31ba7b89354565a2070` passed all 15 check runs: Quality, Security/Semgrep, Python 3.10/3.11/3.12/3.14, Frappe v15/v16 Bench and the pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lane. Merged to main as `84ab2ce0b4ce1a9614882635e4c085092cf2a0c5`.

The USD invoice is deliberately posted against the Company's INR receivable account so invoice value and outstanding balance are checked against their separate currency bases. The POS-shaped row sets the persisted `is_pos`, `paid_amount` and `outstanding_amount` fields directly; POS payment workflow/accounting is not tested. The one-time setup-wizard baseline is committed to the disposable CI database, but all synthetic records and temporary permissions are rolled back. This is not financial reconciliation or pilot acceptance.

**Next gate:** target-site native-report reconciliation, actual Sales User/Manager permissions, and operational pilot acceptance.


## D2 real POS invoice settlement — PR #69 merged (CI-verified)

PR #69 replaces the prior POS-shaped aggregate row with a disposable POS Profile, a company-specific Mode of Payment and a submitted `is_pos` Sales Invoice using ERPNext's normal payment-row lifecycle. The fixture asserts that ERPNext calculates `paid_amount` equal to `grand_total`; it uses a non-stock item and disables POS stock updates. Browser checkout, POS Opening/Closing, cash-drawer and inventory workflows remain out of scope.

The synchronized final head `33b750a43721163c9d58200a01e214b24142c26d` passed all 15 checks: Quality, Security/Semgrep, Python 3.10/3.11/3.12/3.14, Frappe v15/v16 Bench + Playwright, and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. PR #69 merged as `efe78729881390cacba343749364ceccdcb7ffb2`. This is CI evidence, not target-site financial reconciliation.

**D1/D2 Bench query-contract coverage — PR #63 merged (2026-11-02):** The real Sales Compass API now runs read-only in the Frappe v15/v16 Bench matrix and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane. The PR's final-head Quality, Security, Semgrep, Python, Bench v15/v16 and pinned-target checks passed. This verifies query/schema compatibility only; it does not establish financial totals, role-specific target-site visibility or native-report reconciliation. Merge commit: `0a7de966`.



## Completed reliability hardening — PR #23

- Fixes the real unique-key race: after both API requests observe an event key as absent, the losing insert now reloads the winning CRM Signal with `for_update=True` so MariaDB repeatable-read cannot hide the row behind an older snapshot.
- Adds a deterministic Bench test using two independent database connections. The expected result is one CRM Signal, one created response, one deduplicated response and one notification dispatch.
- Serializes digest recipient claims by locking the CRM Signals Settings singleton and rechecking the queued-recipient marker before each email queue request. The lock and marker update share the same transaction as that recipient's Email Queue write.
- Adds a two-worker Bench test asserting one queue request for a recipient/date.
- **Status:** merged to `main` as `d75b7f3`. [Bench v15/v16 + Playwright](https://github.com/MitMike/crm_signals/actions/runs/41300667892), [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41300667996) and [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41300667997) passed on PR head `7ed0860`. No target-site mail/scheduler acceptance is implied.

## Completed engineering task — legacy schema upgrade rehearsal

- PR #21 adds a disposable Bench scenario to both Frappe v15 and v16 lanes: create two historical CRM Signal rows, remove the newer source-event identity columns and DocField metadata, run the real `bench migrate`, then verify the current schema returns and both legacy rows remain intact with null event keys.
- The test deliberately exercises Frappe DocType synchronization. An empty `crm_signals/patches.txt` is not treated as a defect; a custom patch will be added only if migration evidence requires one.
- Status: **passed** on Frappe v15 and v16 in PR #21. The final head `3578dd566683d2dff4c9f663b733e838b6627e25` passed Quality Checks, Bench Integration and E2E, and Security Scanning. The merge commit is `72833cd383811d7c9be591206647b2e0b1f3fbd9`. This does not replace target-site upgrade, backup, restore and rollback rehearsal.

## Merged repository foundation

- [PR #11](https://github.com/MitMike/crm_signals/pull/11) — dependency security monitoring, lockfile, pip/npm audits, Dependabot and tooling remediation.
- [PR #16](https://github.com/MitMike/crm_signals/pull/16) — complete specifications, decision register, delivery plan and feature roadmap.
- [PR #17](https://github.com/MitMike/crm_signals/pull/17) — D1/D2 correctness safeguards for missing Lead/Opportunity status metadata and Sales Invoice return metadata. Merge commit: [fed496f](https://github.com/MitMike/crm_signals/commit/fed496f230f5ca88af25d663bc61fe4d748f5f83).
- [PR #18](https://github.com/MitMike/crm_signals/pull/18) — graduated file/function size and complexity rules. Merge commit: [f51fbce](https://github.com/MitMike/crm_signals/commit/f51fbce19b7d1e84cfa6f3ab26118f2977a8fe40).
- [PR #19](https://github.com/MitMike/crm_signals/pull/19) — configurable settings, presets, Frappe v15/v16 permission compatibility, event idempotency and digest hardening. Merge commit: [a495919](https://github.com/MitMike/crm_signals/commit/a49591947a89b011cc1770be176c1f11571b131b).

## Repository governance

GitHub ruleset [Protect main](https://github.com/MitMike/crm_signals/rules/26282133) is active on `refs/heads/main`.

- Pull requests required; direct main updates, deletion and force pushes are blocked.
- Eight strict required contexts cover lint/static checks, Python 3.10/3.11/3.12/3.14, Semgrep and Bench v15/v16.
- Review threads must be resolved. Required approving review count is zero to avoid deadlocking a single-maintainer repository.
- No bypass actors are configured. Emergency recovery requires an authorized administrator to temporarily edit and then restore the ruleset.
- Dependency Security Audit is active, but is not one of the eight required branch contexts.

[Issue #12](https://github.com/MitMike/crm_signals/issues/12) was closed after ruleset verification.


## Durable transactional signal outbox — PR #26 merged

- PR [#26](https://github.com/MitMike/crm_signals/pull/26) merged to `main` as `b0364a74affa823977af74d1907781d1533e60c0`.
- Final synchronized head: `222e70ec71164dab4448f7319525042323a357b4` (based on main after PR #28).
- Quality Checks, Security Scanning and Bench Integration/E2E all passed on that exact head; Bench covered Frappe v15/v16 and the concurrent enqueue/process idempotency cases.
- Source events and outbox rows commit atomically; delivery is queued after commit, with the scheduled pending-event worker retained as recovery. Retry is bounded and terminal failures are visible to System Managers.
- **Still open:** audited operator replay for terminal Failed rows (PR #38 merged) and durable realtime notification retry. These are not included in the merged outbox scope.

## Stage 1 — release readiness and core hardening

### Completed in merged code
- D1 active Lead/Opportunity counts, stages and active pipeline become unavailable when status metadata is missing rather than incorrectly counting all rows as active.
- D2 Sales Invoice metrics that exclude returns require `is_return`; no return-sensitive aggregation runs without that filter.
- Payment Entry receipt metrics remain independent of Sales Invoice return metadata.
- Branch protection and file/function size standards are merged.

### Implemented and merged in PR #19
- Add System Manager-only CRM Signals Settings singleton and editable Balanced, Sales Focused and Executive presets.
- Configure master/external-ingestion/Quotation/Opportunity/digest switches, Company-currency threshold, Opportunity status list, stale-day window, digest time and extra recipients validated against registered enabled System Users.
- Add source-event metadata and a unique hash-based identity for CRM Signals.
- Make webhook retries idempotent when the caller supplies a stable `source_event_id`.
- Schedule the digest at the configured System Settings timezone, query CRM rows under each recipient's user context, send separate permission-filtered emails and record each queued recipient in the same transaction as that email-queue request.
- Remove hard-coded INR formatting and isolate realtime notification errors by recipient.
- Filter realtime recipients by the linked Lead/Customer read permission before sending signal content; denied/failed permission checks are excluded (ADR-034).
- Also require CRM Signal document read permission; add a real FrappeTestCase for both checks and run it with `bench run-tests --app crm_signals` on v15 and v16.
- Align list-query access with direct-document access: owner-only visibility is restricted to unlinked signals; linked signals require a permission-readable owned/assigned parent (ADR-035).
- Add a generic deployment/rollback runbook; actual target-site backup/restore rehearsal remains a P0 acceptance gate.
- Record a production-readiness audit with fixed findings, outstanding P0/P1 risks and an explicit not-ready-for-sign-off decision in docs/PRODUCTION_READINESS_AUDIT.md.
- Default the master switch and external ingestion to disabled, including missing-settings fallback, until System Manager explicitly activates the reviewed configuration (ADR-036).
- Bound daily digest quotation output to 100 rows with an explicit truncation notice to prevent unbounded email payloads (ADR-037).
- Add Bench-backed webhook and database tests for same-user duplicate POSTs, one notification per event, per-user namespaces, unique-key enforcement and multiple legacy null keys; concurrent insert and true pre-feature upgrade migration remain open.
- CI follow-up (2026-11-01): Bench v15/v16 exposed an invalid CRM Signal autoname expression that persisted the literal `SIG-.YYYY.-.#####`; corrected to Frappe's brace-delimited `format:SIG-{YYYY}-{#####}` (ADR-038). The API integration test now sets request form data after switching users because the user-context switch clears the local request form.
- CI follow-up (2026-11-01): Bench v16 exposed the changed document-permission hook contract: it passes `ptype` and requires an explicit boolean. Updated the hook to accept both v15/v16 argument names and preserve role-level DocType permissions before row-level restrictions (ADR-039). Corrected duplicate-key recovery to handle Frappe's `UniqueValidationError` using a locking read, added a race-recovery regression test, and changed notification idempotency coverage to count one dispatch rather than assume one realtime recipient. Prettier formatting was corrected and its temporary diagnostic step removed. These changes passed the final v15/v16 Bench matrices, Playwright, Python, lint and security checks before PR #19 merged.
- CI follow-up (2026-11-01): The first v16 Playwright run exposed a login race: the session cookie existed before Frappe completed the redirect, causing subsequent API/navigation actions to overlap with that redirect and trigger aborted requests and CSRF errors. The shared login helper now waits for the version-appropriate Desk URL; the settings custom-preset handler awaits its form-model update and the E2E test blurs the integer field before asserting. See ADR-040. The corrected v16 Playwright suite passed on final PR head `a90315be7ef37e2dceeacb9b4e9b77d5d31df131`.
- Add an admin guide, settings/reliability spec and configuration/identity/digest tests.

### Target-site acceptance — still required
- [ ] Run Frappe Pilot import on the intended site and record installed Frappe/ERPNext versions and applications.
- [ ] Confirm Company default currency and verify quotation threshold behavior for every enabled Company.
- [ ] Confirm Opportunity status values and terminal Lead statuses from actual workflows.
- [ ] Confirm site timezone, digest time and recipients.
- [ ] Validate Sales User, Sales Manager, System Manager and non-sales roles in list, direct form, API, report, export and print paths.
- [ ] Reconcile D2 invoice, Payment Entry receipt, POS receipt and receivable figures against native ERPNext reports, by currency.
- [ ] Configure a dedicated integration user, API credentials, TLS, gateway rate limiting, monitoring and secret rotation.
- [ ] Exercise scheduler, mail queue, realtime notifications, migration, backup and rollback on the intended site.

## Explicitly deferred

See [FOLLOW_UPS.md](FOLLOW_UPS.md) for issues that should not be silently treated as complete:
- Target-site acceptance for durable realtime retry (engineering implementation in PR #54); audited terminal Failed-row replay for the transactional signal outbox is merged in PR #38.
- Multi-company quotation thresholds merged in PR #45; target-site Company amounts and exact-currency fallback approval remain; no implicit FX conversion.
- D3 field-level permission hardening and target-site acceptance; H privacy/consent decisions, E integration inventory, V retention and A metric-registry work.

## Completed branch work — PR #21

- PR #21 adds a disposable Frappe v15/v16 rehearsal for upgrading historical CRM Signal rows from the pre-source-event-identity schema.
- First rehearsal attempts failed because Frappe's stored DocType `migration_hash` still matched the current JSON, so the importer skipped the schema import even after the timestamp rewind.
- The fixture now clears that hash and rewinds the DocType timestamp before `bench migrate` (ADR-042). This is a CI fixture correction; the final migration rehearsal passed on both supported Frappe versions.
- Latest fix commit: `acc096879841286afa61073571fbe40eea473fd4`. PR #21 is merged as `72833cd383811d7c9be591206647b2e0b1f3fbd9`.

## CI and release evidence

PR #23 was merged to `main` as `d75b7f3591d2a863b0af6b8f88ad2a91e9bfd25f` after all required checks passed on final PR head `7ed0860fd45cdc152bb2dcc868489d46b69aefb9`: [Bench Integration and E2E, v15/v16 + Playwright](https://github.com/MitMike/crm_signals/actions/runs/41300667892), [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41300667996), [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41300667997). API idempotency and digest concurrency regression tests passed on both supported Frappe versions. The earlier PR #21 legacy-schema migration rehearsal also passed; target-site upgrade/restore/rollback remains open.

PR #21 was merged after all required checks passed on final head `3578dd566683d2dff4c9f663b733e838b6627e25`. Quality Checks, Bench Integration and E2E (Frappe v15/v16), and Security Scanning passed. The legacy-schema upgrade rehearsal is complete at CI level; target-site upgrade/restore/rollback remains open.

PR #19 was validated on head `a90315be7ef37e2dceeacb9b4e9b77d5d31df131` and merged as `a49591947a89b011cc1770be176c1f11571b131b`. [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41274491111), [Bench Integration and E2E](https://github.com/MitMike/crm_signals/actions/runs/41274491113) and [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41274491117) passed; all 16 check-runs on that head reported success, including Frappe/ERPNext v15 and v16 and the v16 Playwright suite.

CI is necessary, not production acceptance. Never mark a target-site gate complete based only on a mocked unit test or the existence of source code.

## Update protocol

For each change:
1. Update the relevant spec before or alongside implementation.
2. Record material data, security, compatibility and delivery choices in [DECISIONS.md](DECISIONS.md).
3. Add tests for the acceptance criteria.
4. Update [CHANGELOG.md](../CHANGELOG.md) for user-visible or operationally significant changes.
5. Reconcile this file after merge and attach commit/CI evidence.
6. Put blocked or intentionally deferred work in [FOLLOW_UPS.md](FOLLOW_UPS.md), with an owner/trigger and reason.


## D3 adapter merged — Frappe Helpdesk

- Merge: PR #32 as `43fddfbbc46cac277a48c840251a7a2c963a8eb5`; CI verified on Frappe v15/v16.
- Source schema verified against Helpdesk v1.28.0 reference: HD Ticket, HD Ticket Status, HD Service Level Agreement; ticket fields include status_category, resolution_date, resolution_time, sla and agreement_status at permlevel 0. Later Helpdesk releases may move fields to higher levels.
- API aggregates ticket creation, current Open/Paused backlog, resolved cohort, native resolution duration and SLA fulfilled/failed outcomes. Ticket and SLA permissions are checked independently; payload contains no ticket subjects, comments, contacts or identifiers.
- SLA outcome counts use the same rolling 30-day created-ticket cohort; only Fulfilled/Failed are eligible. No-SLA tickets are counted separately.
- Monday–Saturday is the agreed business-week assumption; configured Helpdesk SLA hours and holiday lists are not overridden.
- Field-level fail-closed permission guard merged in PR #42; exact Frappe v16.5.0/ERPNext v16.5.0/Helpdesk v1.28.0 CI merged and passed in PR #50. Pilot-site versions and role/SLA acceptance remain. The first run exposed a malformed MariaDB client config; the here-doc correction is in place.
- Remaining: capture the pilot site's exact app versions, configure the approved custom read-only Helpdesk role for Sales, and verify the active SLA calendar, hours and holiday list.


## Resolved PR #57 merge gate — cancelled duplicate Bench checks

- **Evidence:** GitHub rejected the earlier merge attempt on head `7f9d840226e6d6db1a435b8c1cc629e70dc63eca` because two required Bench contexts were cancelled by a push run on the stacked Desk branch. A new unique head `dda6eb88c0e8735645018de60275d9cf55d2d99d` then passed all eight required contexts and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane; PR #57 merged as `ba631720`.
- **Decision:** Do not bypass the main ruleset or retry stale shared-SHA runs. The original stacked PR #58 was closed unmerged; PR #59 is its clean replacement based on `main`.
- **Revisit criteria:** No further action is required for PR #57. If a future PR produces duplicate or cancelled contexts, inspect the push and pull-request run sources and require successful final-head contexts before merging. Never bypass branch protection.
