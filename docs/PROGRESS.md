# Project Progress

**Last reviewed:** 2026-11-03  
**Repository:** [MitMike/crm_signals](https://github.com/MitMike/crm_signals)  
**Reviewed main baseline:** [8543da5](https://github.com/MitMike/crm_signals/commit/8543da5c2270a816608ba23927a6ee35571e5bde) (PR #121 merged; post-merge Quality Checks, Security Scanning and Bench Integration/E2E workflows completed successfully; PR #120 final-head 18/18 checks passed); **latest application feature baseline:** [c5720bf](https://github.com/MitMike/crm_signals/commit/c5720bfb3fbe8b554ec6febd549a8d5e58acc1d7); **latest UI fix:** [b1f4ad7](https://github.com/MitMike/crm_signals/commit/b1f4ad71f368c346ce16126501982cfe2233c2b9) (PR #84 dashboard inset, CI-verified)  
**Completed implementation:** PR #19 delivered settings/presets and core idempotency; PR #21 validated the legacy-schema migration; PR #23 closed concurrent API-idempotency and digest-queue races; PR #26 merged the transactional signal outbox; PR #32 merged the standard Frappe Helpdesk D3 adapter; PR #38 merged audited Failed-row replay; PR #42 merged D3 field-level permission hardening; PR #44 merged source-document notification authorization; PR #45 merged per-Company quotation thresholds; PR #49 corrected Company-currency display/fetch; PR #50 fixed the D3 system creation-column guard and added the exact Frappe v16.5.0 / Helpdesk v1.28.0 compatibility lane; PR #51 merged the Frappe v16.5 pilot operator kit; PR #53 merged the D3 aggregate fixture; PR #54 merged durable per-recipient realtime retry; PR #55 merged the staging realtime-recovery acceptance checks; PR #56 merged the pilot-status reconciliation as `704997e88a52071c15f95e5985703dc00bc10f03`; PR #57 merged the Explorer core API as `ba6317204784868a39d7c91ead01959663c9a33a`; PR #59 merged the Explorer Desk UI as `6b381fe4c7164c099cbd841086bf79566cb72ed1`; PR #61 merged five-context browser coverage and operator-runbook hardening as `6ef9642b63c24053fb437f67d9d4fb47e360c80a`; PR #62 reconciled post-Explorer status/decision records as `aeea9599b11f17bff0ef5bbd7904f44f23567e3e`; PR #63 merged read-only D1/D2 query-contract Bench smoke coverage as `0a7de966ea0639c86a59d7df28dbad343fa13488`; PR #65 fixed independent Payment Entry source permissions and merged as `0cfeda4fb39f79722fdf733abd06a3460ebcdd4d`; PR #66 reconciled the plan/progress/decision/follow-up records and merged as `e82c34f1afee054b2103d316c06a078290b97a39`; PR #67 added the D1/D2 synthetic aggregate-value fixture and merged as `84ab2ce0b4ce1a9614882635e4c085092cf2a0c5`; PR #68 reconciled D1/D2 progress and operator records and merged as `2cc7725d4e36f53d492139187fa6cd9adf663f0f`; PR #70 added the read-only target-site preflight report and merged as `13341b756e2d2a92c9432f3c50ac77594e2483e9` after all required Quality, Security, v15/v16 Bench and pinned v16.5.0 checks passed; PR #69 added the real ERPNext POS invoice settlement fixture and merged as `efe78729881390cacba343749364ceccdcb7ffb2` after all 15 final-head checks passed  ; PR #15 upgraded the locked Prettier development dependency to 3.9.10 and merged as `5fc32b0313e61eba45695ab2322b2f10140a4482` after all required contexts and dependency audits passed; PR #13 upgraded Oxlint to 1.90.0 and merged as `b466ac87613afc5b2726ef866d9a28b37ac3fab4` after all required v15/v16, quality and security contexts passed; PR #14 upgraded the locked globals development dependency to 17.13.0 and merged as `567f4586b9f7c8965f6aa00ed673962b8bc29539` after all required v15/v16, Quality and Security contexts passed; PR #71 added permission-gated High-Value Quote source Quotation drill-down and merged as `c5720bfb3fbe8b554ec6febd549a8d5e58acc1d7`; final head `df0c27363c60f4f4e6f02b25c37708db24b71ebb` passed Quality, Security, Python 3.10/3.11/3.12/3.14, Frappe v15/v16 Bench Integration/E2E and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 checks; PR #73 reconciled H-AC11 post-merge status and ADR-073, merged documentation-only as `51798f2a2711737cf67ea91c597405c224e6228f` after Quality, Security, Python 3.10/3.11/3.12/3.14 and Bench v15/v16 passed; PR #5 upgraded actions/checkout from v4 to v7, refreshed onto main, passed all 17 final-head check runs including Quality, Security, dependency audits, Frappe v15/v16 Bench and pinned Frappe v16.5.0 / Helpdesk 1.28.0, and merged as `00e997ce25747f24b8af9948527a1738cc6f3920`; PR #76 made Quality/Python/Bench validation change-aware with fail-closed stable gates and merged as `cec49e700a7a94684e8136170dd0e562ed23052a` after all 19 final-head check runs passed; PR #82 corrected pin-before-install and merged as `ac030b195394458d87b7d59656b560359260d79e` after the v15/v16 + Playwright and pinned v16.5.0 workflows passed; PR #84 restored the 24px dashboard horizontal inset and merged as `b1f4ad71f368c346ce16126501982cfe2233c2b9` after all four workflows passed on `f0e19099`; PR #85 changed the workspace display label/title to GME CRM Signals and merged as `5cc4308b388fce5ec5899679368bca6a86cad876` after all four workflows passed on `b09a0cb`; PR #88 upgraded both workflow upload sites to actions/upload-artifact v7 and merged as `de8e78b8750370934b2608564fa63ecc4095f37f` after all four final-head workflows passed on `eed57d6`; PR #89 reconciled the current release/ADR/follow-up snapshot and merged as `ac6b253b6789059e34ec6c69e6435491b539a048` after Quality, Security and Bench Integration/E2E passed; PR #7 upgraded setup-uv v6 to v7 in the two Bench workflows and merged as `331492c5be1e5e32105e6d64b710d2e861c0111a` after all 18 final-head check runs passed
**Next acceptance:** complete the target-site Frappe v16.5 pilot: exact app versions, per-Company threshold amounts/currencies, the custom read-only Helpdesk role, D1/D2 reconciliation, Helpdesk SLA calendar, scheduler/mail/realtime, and backup/restore/rollback. CI-verified work is not pilot-verified.

This file is the operational source of truth. [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) is the roadmap, [DECISIONS.md](DECISIONS.md) is the durable decision register, [FOLLOW_UPS.md](FOLLOW_UPS.md) tracks deferred issues, and [specs/](../specs/) holds feature contracts.

## Current status

## Read-only target-site preflight report — merged, CI-verified

ADR-068 is recorded. PR #70 added a non-whitelisted Bench diagnostic and unit coverage for app-version discovery, Company currency/threshold reporting without FX conversion, active Lead/Opportunity workflow states, required DocType fields, Select options, static DocPerm rows, missing D3 fields and omission of digest recipient addresses. The command performs metadata/configuration reads only; it does not read transaction, ticket or customer rows or write data.

**State:** PR #70 merged as 13341b756e2d2a92c9432f3c50ac77594e2483e9 from final head 1b1a107c8df6f9b70ea2e429c0fb5ec2b53e24a4. All final-head required Quality, Security and Frappe v15/v16 Bench contexts passed; the pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lane and Semgrep OSS also passed. This is CI-verified, not pilot-verified: an authorized operator must still run the report on the target site and complete effective-user permissions, finance reconciliation and SLA/operations acceptance. Static DocPerm is not effective-permission proof.

## H-AC11 source Quotation drill-down — merged, CI-verified; pilot acceptance open

The CRM Signals dashboard now includes a source label and routes a High-Value Quote row to its originating Quotation only when the current user can read the CRM Signal source fields and that exact Quotation. Other source types are suppressed; permission or metadata errors fail closed, preserving the existing Lead/Customer/CRM Signal fallback. API tests cover field denial, document denial, metadata lookup/field-permission failures, Quotation permission-check exceptions, exact source-name authorization and non-Quotation sources; Playwright covers the visible source label and route.

**State:** merged as `c5720bf`; code-complete and CI-verified. Final head `df0c27363c60f4f4e6f02b25c37708db24b71ebb` passed Quality, Security, Python 3.10/3.11/3.12/3.14, Frappe v15/v16 Bench Integration/E2E (including the Playwright source-route test) and the pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lane. The exact Prettier 3.9.10 output was emitted by the ADR-072 diagnostic and applied before final validation. This is CI verification only: target-site Sales User/Manager/non-sales permission checks, staging rehearsal and pilot acceptance remain open.

## Immutable deployment revision pin and pin-before-install sequence — PR #74 / #82 (merged, CI-verified)

PR #74 merged as `1b57003`; the follow-up PR #82 corrected its first-install ordering defect and merged as `ac030b195394458d87b7d59656b560359260d79e`. Final PR #82 head `ef4dc0975a22fa3f3b5c1d87aa161baca546d231` passed all four required workflows: Quality Checks, Security Scanning, Frappe v15/v16 Bench Integration and E2E (including v16 Playwright), and the pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lane. The verified sequence is direct clone with `upstream`, detach and verify the approved full SHA, then run `bench setup requirements crm_signals` before site installation, migration or asset build. Upgrade instructions verify the Bench remote rather than assuming `origin`.

The administrator guide, deployment runbook and target-site acceptance kit now use this sequence; ADR-077 records the decision. **Code-complete and CI-verified; not target-site or pilot-verified.** An authorized operator must still rehearse the sequence on the intended staging Bench and retain the SHA, version inventory and command output.

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


## Change-aware CI execution — PR #76 (merged and CI-verified)

PR #76 merged as `cec49e700a7a94684e8136170dd0e562ed23052a`. Final head `d6a63003addf592c79f850bbfca2b1df0e3a6da2` passed all 19 check runs: Quality, Security/Semgrep, Python 3.10/3.11/3.12/3.14, Frappe v15/v16 Bench integration (including v16 Playwright), and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation. The change selectors cover runtime, package, workflow, workspace, patch and fixture paths; required Python/Bench gates fail closed on detector failure. Quality feature-branch duplicate push runs are avoided while every PR still receives the path-aware workflow. No required check context was removed. This is CI infrastructure verification, not pilot verification.

## Bug and fix registers — PR #79 merged

- PR #79 added docs/BUG_REPORT.md and docs/FIX_REPORT.md, with BUG-2026-001 / FIX-2026-001 recording the CRM Signals dashboard horizontal-inset regression and its evidence-based closure criteria. Merged as 7904a70 after Quality, Security and Bench v15/v16 passed.
- PR #80 and PR #81 are both closed unmerged. The bug/fix registers are present from PR #79; the proposed regression-review template was not merged and is not a required release gate.



## Current UI fixes — merged and CI-verified; UAT remains open

- **BUG-2026-001 / FIX-2026-001 dashboard inset:** PR #84 merged as `b1f4ad7`. Final head `f0e1909` passed Quality Checks, Security Scanning, Bench Integration and E2E, and pinned Frappe v16.5.0 + Helpdesk v1.28.0. Desktop/mobile visual UAT after asset rebuild/cache refresh remains outstanding.
- **GME CRM Signals workspace label:** PR #85 merged as `5cc4308`. Final head `b09a0cb` passed Quality, Security, Bench v15/v16 and pinned v16.5.0. Only the workspace label/title changed; technical identifiers, routes and shortcuts remain unchanged.

## Upload-artifact v7 — merged and CI-verified

PR #88 upgraded the two workflow upload sites from `actions/upload-artifact@v4` to `@v7`. Final head `eed57d69ad25d2bac73fc873b636e44360ae4030` passed Quality Checks, Security Scanning, Bench Integration and E2E, and pinned Frappe v16.5.0 + Helpdesk v1.28.0. It merged as `de8e78b8750370934b2608564fa63ecc4095f37f`. The workflows use GitHub-hosted runners; future self-hosted runners must meet the action's Node 24 minimum.

## Setup-uv v7 — PR #7 merged and CI-verified

PR #7 updates `astral-sh/setup-uv@v6` to `@v7` in `.github/workflows/bench-e2e.yml` and `.github/workflows/bench-target-v16-5.yml`. Final head `a72c82c0e6bc2a04e6edebbcdf610c4e5e3c85ac` passed all 18 check runs: Quality, Security/Semgrep, Python 3.10/3.11/3.12/3.14, Frappe v15/v16 Bench integration (including Playwright), and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. It merged as `331492c5be1e5e32105e6d64b710d2e861c0111a`. No application runtime or dependency lockfile changed.

## Historical PR queue snapshot — reviewed against main `331492c` (superseded by later maintenance entries)

- PR #89 documentation/ADR-075 skip-path reconciliation merged as `ac6b253`; Quality, Security and Bench Integration/E2E passed on final head `0967290`.
- PR #7 setup-uv v7 merged as `331492c`; all 18 final-head check runs passed.
- **Open Dependabot PRs:** #8 setup-node v7 and #10 setup-python v7 are each one commit ahead and two behind this main snapshot; their old-head checks passed but must be refreshed and rerun. PR #9 flit-core `>=3.4,<5` is one commit ahead and 52 behind; its old-head checks are stale and package-build/install compatibility remains to be verified.
- PRs #75/#78 were closed unmerged and superseded by #85/#84. PRs #80/#81 were closed unmerged; the optional regression-review template was not merged.
- These maintenance checks do not change the product release decision and are not pilot verification.



## Maintenance and release-status reconciliation — 2026-11-03 (after PR #97)

- PR #97 merged as `b18f504` after final-head Quality Checks, Security Scanning and Bench Integration/E2E passed. It reconciles the repository maintenance snapshot after PR #94.
- PR #8 (setup-node v7), PR #94 (setup-python v7; merge `926619b`) and PR #7 (setup-uv v7; merge `331492c`) are merged.
- PR #96 is refreshed onto current main `b18f504`. It changes the build-system range from `flit_core >=3.4,<4` to `>=3.4,<5` and adds a direct package compatibility gate: build wheel and sdist with flit-core v4, install each artifact into a clean environment, and import the installed package on Python 3.10 and 3.14. The workflow change also causes current-head Frappe v15/v16 Bench and pinned v16.5.0 validation to run. Final-head checks are pending; pre-refresh PR #96 checks are stale and are not merge evidence.
- PR #93 is superseded; do not reuse its checks. No other open PRs were present when this snapshot was reviewed.
- Target-site pilot acceptance remains unverified by CI. Required operator evidence remains the read-only preflight, exact installed app/full-SHA inventory, effective-role permission checks, D1/D2 native ERPNext report reconciliation by currency, Helpdesk SLA calendar, scheduler/mail/realtime/webhook operations, and backup/restore/rollback rehearsal.
- Dashboard inset visual UAT (desktop/mobile after approved asset refresh) remains open. Do not perform production migration, permission change, or deployment without required approval and backup/rollback evidence.


## Maintenance update — 2026-11-03

- **PR #96 — flit-core v4 build-system compatibility:** merged as [d0ab24b](https://github.com/MitMike/crm_signals/commit/d0ab24b6a50184af99f4af638ae64ddd9a22d08a). Final head `349bf71b0687c77e830fb8b054cedacabb16f61b` passed all 20 check runs: Quality (lint/static and Python 3.10/3.11/3.12/3.14), Security/Semgrep, Python and npm dependency audits, Frappe v15/v16 Bench integration including v16 Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation. Explicit flit-core v4 wheel and sdist builds and clean-environment installs/imports passed on Python 3.10 and 3.14.
- **Open pull requests:** none at this snapshot (checked after PR #96 merge).
- **Packaging status:** build-system range `flit_core >=3.4,<5` is merged and CI-verified. This establishes reference CI package compatibility, not a production deployment or pilot.
- **Next work:** continue source-independent product work only where contracts are approved; otherwise prioritize target-site evidence collection and dashboard desktop/mobile visual UAT. Do not treat absent site inputs as implementation-complete.


## Documentation merge reconciliation — 2026-11-03

- [PR #98](https://github.com/MitMike/crm_signals/pull/98) merged as [`1a27166`](https://github.com/MitMike/crm_signals/commit/1a27166bfe988c860b3527af5bba9a0299e1e30f) after all 13 final-head check runs completed successfully. Docs-only selectors correctly skipped Python and Bench runtime execution; Python unit tests, lint/static checks, Semgrep, Bench v15/v16 validation (including v16 Playwright) all passed.
- **Current main:** `1a27166bfe988c860b3527af5bba9a0299e1e30f`.
- **Open pull requests:** none at this snapshot.
- This closes the documentation reconciliation for PR #96 / ADR-082. No product or pilot status is upgraded by this merge.


## Dashboard inset regression guard — PR #100 (merged; CI-verified)

- PR #99 merged as `6a46c26b3a58a3ea035d7e53b15bc2f8839e2bb5` after all 13 final-head checks completed successfully. Its docs-only path detection skipped Python/Bench runtime execution while Python 3.10/3.11/3.12/3.14, lint/static, Semgrep and both Bench validation lanes completed successfully.
- PR #100 adds a rendered-page Playwright regression assertion for BUG-2026-001 / FIX-2026-001: 24px horizontal inset at 1440px and 12px at 390px. The test is code-complete. Review of the initial PR run found that `e2e/**` and `playwright.config.ts` were missing from the change-aware Bench selector; PR #100 now adds both paths plus static contract coverage (ADR-084), so the v16 Playwright lane is required for this change. Final-head CI passed: all 18 check runs completed successfully on 50759954b8801fb8edd7194fea354c3521b457f1; PR #100 merged as 9c4febf8180ef295b48ea18b1ac5fddc164ff34f.
- This guard prevents the specific CSS regression from silently returning. It does not prove rebuilt staging assets look correct and does not close desktop/mobile visual UAT or target-site pilot acceptance.


## Post-PR #100 verification — 2026-11-03

- [x] PR #100 merged as 9c4febf (https://github.com/MitMike/crm_signals/commit/9c4febf8180ef295b48ea18b1ac5fddc164ff34f) from final head 50759954b8801fb8edd7194fea354c3521b457f1.
- [x] All 18 final-head check runs completed successfully. The four workflows passed: Quality Checks, Security Scanning, Bench Integration and E2E, and pinned Frappe v16.5.0 + Helpdesk v1.28.0 validation.
- [x] Bench v15 and v16 passed; the v16 Playwright browser suite executed the new desktop/mobile dashboard inset assertion. Python 3.10/3.11/3.12/3.14 and Semgrep checks passed.
- [x] ADR-084 path coverage is exercised by the same PR: e2e/** and playwright.config.ts changes trigger the Bench browser lane.
- [x] Live open-PR search returned zero after merge.
- [ ] **Dashboard visual UAT:** execute the new repeatable procedure in [Target-Site Acceptance Kit §11](TARGET_SITE_ACCEPTANCE.md#11-dashboard-horizontal-inset-visual-acceptance) on authorized staging after the approved asset build/cache refresh; retain desktop/mobile screenshots.
- [ ] **Target-site pilot:** authorized Frappe v16.5 inventory, effective-role tests, D1/D2 native-report reconciliation by currency, Helpdesk SLA evidence, scheduler/mail/realtime/webhook recovery and backup/restore/rollback rehearsal remain outstanding.

PR #100 is code-complete and CI-verified, not pilot-verified. The automated computed-style assertion does not substitute for staging screenshots or the target-site acceptance matrix.



## Read-only preflight source revision — PR #103 merged 2026-11-03

- **Reviewed main:** `5dbda0291358350d5a720127a7d526145d3e3c60`; PR #103 merged to main.
- **Decision:** ADR-086 adds the exact CRM Signals checkout SHA to the existing server-side, non-whitelisted preflight. The helper runs `git status --porcelain --untracked-files=all` and, only for a clean checkout, `git rev-parse --verify HEAD` from the imported app directory. Each command has a five-second timeout; it validates a full 40-character hexadecimal result and reports bounded failure reasons without paths or stderr.
- **Implementation:** merged as `5dbda0291358350d5a720127a7d526145d3e3c60` from PR #103 (final head `fc7f0ae381267d04d7db9f14ec888d965c7fe828`). Regression tests cover clean/dirty checkout, exact SHA, failed Git lookup without stderr disclosure, missing Git, timeout, malformed output and report inclusion.
- **CI verification:** all 18 final-head check runs passed. Quality/Python 3.10–3.14, Semgrep, Bench v15/v16 (including the v16 Playwright E2E suite) and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation passed.
- **Operator guide:** ADMIN_GUIDE.md and TARGET_SITE_ACCEPTANCE.md require a clean checkout and exact match against the approved full release SHA.
- **Status:** code-complete and PR-CI-verified; not pilot-verified. Main-branch push workflows were still running immediately after merge. No target-site execution or pilot verification is claimed.


## Preflight repository-root identity hardening — merged and CI-verified (2026-11-03)

- **Reviewed main:** `db958124bca6a6704a75f606629c22444716f5b9`; PR #105 merged.
- **Decision:** ADR-087 closes a false-identity edge case: `git -C <package-dir>` can discover an enclosing repository. Preflight requires `git rev-parse --show-toplevel` to resolve to the CRM Signals repository root derived from the imported package path before checking cleanliness or reporting `HEAD`.
- **Implementation:** PR #105 merged as [`db95812`](https://github.com/MitMike/crm_signals/commit/db958124bca6a6704a75f606629c22444716f5b9), final head `fd2161dc933fbaf74fd5a50a5261e5f1501b283e`. Added matching-root and parent-repository rejection coverage; retained fixed, read-only Git commands, five-second per-command timeouts, dirty-tree rejection, full-SHA validation and bounded non-disclosing failure reasons. Updated ADMIN_GUIDE.md, TARGET_SITE_ACCEPTANCE.md and DEPLOYMENT_RUNBOOK.md.
- **CI verification:** all 19 final-head check runs completed successfully. Quality/lint, Python 3.10/3.11/3.12/3.14, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation passed.
- **Initial CI finding and correction:** first Python 3.11 and 3.12 runs each failed one stale dirty-checkout assertion because root validation adds a Git call before status. Updated the test to expect both calls and verify `HEAD` is not read for a dirty tree. Corrected final-head checks passed; the initial failures were test expectation failures, not an application behavior regression.
- **Status:** code-complete and reference-stack CI-verified; not pilot-verified. No target-site execution or pilot acceptance is claimed.
- **Next gate:** authorized Frappe v16.5 staging remains required for dashboard visual UAT, exact installed app/full-SHA inventory, effective-role permissions, D1/D2 native-report reconciliation, Helpdesk SLA validation, scheduler/mail/realtime/webhook recovery and backup/restore/rollback evidence.


## Real-Git nested-parent regression — PR-opening snapshot (2026-11-03)

- **Reviewed main:** `5cc7137c331db8c5026ed560d74573640a486a82` (PR #106 merged).
- **Decision:** ADR-088 complements ADR-087's mocked root-mismatch test with an actual temporary parent Git repository and nested Bench-style app path. This directly exercises Git's upward repository discovery.
- **Implementation:** [PR #107](https://github.com/MitMike/crm_signals/pull/107), branch `test/preflight-real-parent-git-regression-20261103`; creates a parent repo and empty commit, then invokes the real preflight helper and asserts it fails closed with `repository_root_mismatch`.
- **Scope:** test-only; no runtime code or site configuration changes. Existing mocked tests retain coverage of timeout, missing Git, dirty checkout, command failure and invalid SHA.
- **Status at PR opening:** code-complete; CI pending. Final merge and CI evidence are recorded in the later PR #107 section below. Not pilot-verified.


## Real-Git parent-repository regression — PR #107 merged (2026-11-03)

- [x] PR #107 merged as [`a472f19`](https://github.com/MitMike/crm_signals/commit/a472f1981f758ce7b6233d95fc0682fe69d7a304) from final head `a47c3975eebe52dccb918a1056cf30d818cdcae4`.
- [x] All 19 final-head check runs completed successfully. Quality Checks, Security Scanning, Bench Integration and E2E, and pinned Frappe v16.5.0 + Helpdesk v1.28.0 workflows all completed successfully.
- [x] Python 3.10/3.11/3.12/3.14, Semgrep, Bench v15/v16, v16 Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation passed.
- [x] The real-Git regression creates a committed enclosing repository and nested Bench-style CRM Signals package path, then verifies the real preflight rejects the parent root with `repository_root_mismatch`.
- [x] Live open-PR search returned zero immediately after merge; no open repository issues were found.
- **Decision:** ADR-088 supplements mocked mismatch coverage because the defect depends on Git's real upward repository discovery. No runtime or site configuration changed.
- **Status:** code-complete and reference-stack CI-verified; not pilot-verified.
- [ ] **Next gate:** authorized Frappe v16.5 staging for exact installed app/full-SHA inventory, dashboard desktop/mobile screenshots after approved asset rebuild/cache refresh, effective-role tests, D1/D2 native-report reconciliation by currency, Helpdesk SLA acceptance, scheduler/mail/realtime/webhook recovery and backup/restore/rollback rehearsal. No staging evidence is available in this repository review.


## PR #108 documentation reconciliation and PR #109 opening snapshot — 2026-11-03

- [x] PR #108 merged as `c31fe7eb328f552cf49f670257370189f09da9e2`; 11 applicable checks passed, and the two runtime selectors were skipped as expected for documentation-only changes.
- **Reviewed main:** `c31fe7eb328f552cf49f670257370189f09da9e2`; no open PRs were present after the merge.
- **Decision:** ADR-089 supplements mocked clean/dirty tests with a real temporary CRM Signals Git checkout. Verify the real clean SHA, then create an untracked Python file and require `working_tree_dirty`; the dirty path must not query `HEAD`.
- **Implementation:** [PR #109](https://github.com/MitMike/crm_signals/pull/109) adds the real clean/dirty integration test only. No runtime behavior or site configuration changes.
- **Status at PR opening:** code-complete; final-head CI pending; not pilot-verified. Final merge and CI evidence is recorded in the next section.
- **Independent release blocker:** authorized Frappe v16.5 staging remains required for exact deployed SHA, dashboard visual screenshots, effective-role permissions, D1/D2 finance reconciliation, Helpdesk SLA, operational recovery and backup/restore/rollback evidence.


## PR #109 merged — real-Git clean/dirty source identity regression (2026-11-03)

- [x] PR #109 merged as [`94d14f5`](https://github.com/MitMike/crm_signals/commit/94d14f56a526670d2c0ecb150ab9f08b4f034389) from final head `d8b65eedc45c05947409f9781a9caaee848aa4ba`.
- [x] All 18 final-head check runs passed: Quality/lint, Python 3.10–3.14, Security/Semgrep, Bench v15/v16 + Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0.
- [x] Real Git test proved a clean temporary checkout returns its exact `HEAD` SHA; after an untracked Python override is added, preflight returns `working_tree_dirty` and does not query `HEAD`.
- **Decision:** ADR-089 adds real Git clean/dirty coverage alongside ADR-087/088 root identity tests; mocked tests retain deterministic error-path coverage.
- **Scope/status:** test-only; no runtime or target-site configuration change. Code-complete and reference-stack CI-verified; not pilot-verified.
- **Reviewed main:** `94d14f56a526670d2c0ecb150ab9f08b4f034389`. The PR final-head required checks were all successful; the separate main-push workflow is not used as a substitute for the PR's final-head evidence.
- [ ] **Next gate:** authorized Frappe v16.5 staging remains required for deployed SHA, dashboard screenshots, effective-role permissions, D1/D2 native-report reconciliation, Helpdesk SLA, scheduler/mail/realtime/webhook recovery and backup/restore/rollback evidence.


## PR #110 merged — release-document reconciliation (2026-11-03)

- [x] PR #110 merged as [`fe7dca4`](https://github.com/MitMike/crm_signals/commit/fe7dca402293faa1e7e60f147d53adaef63009d6) from final head `f4904b7bd88725017f5f2254de9ceb3c123163cc`.
- [x] All 13 final-head check runs completed: 11 succeeded and two runtime selectors were skipped as expected for a documentation-only diff. Quality/lint, Security/Semgrep, Python version gates and stable Bench v15/v16 validation passed.
- [x] Refreshed the release-readiness sprint, marked the older production-readiness audit as historical, and corrected the README's stale statement that D3 implementation was still pending.
- **Reviewed main:** `fe7dca402293faa1e7e60f147d53adaef63009d6`. The open PR and issue queries both returned zero immediately after merge.
- **Status:** documentation complete and reference CI-verified. No application runtime code or site configuration changed.
- [ ] **Release gate:** authorized Frappe v16.5 staging remains necessary for exact installed app/full-SHA inventory, dashboard screenshots after asset/cache refresh, effective-role permissions, D1/D2 native-report reconciliation by currency, Helpdesk SLA calendar, scheduler/mail/realtime/webhook recovery and backup/restore/rollback rehearsal. No pilot verification is claimed.


## PR #111 merged — release-document reconciliation (2026-11-03)

- [x] PR #111 merged as [`166ca6b`](https://github.com/MitMike/crm_signals/commit/166ca6b2cc9838ffd68c551b327ee41d2a5316b4) from final head `30d44ffd48a1f39ef39d658a6bdc12b07f8130da`.
- [x] All 13 final-head checks completed: 11 passed and two runtime selectors were skipped as expected for a documentation-only change. Quality/lint, Security/Semgrep, Python 3.10–3.14, stable Bench v15/v16 checks and change detectors passed.
- [x] Main commit `166ca6b` subsequently completed all 17 check runs: 16 succeeded and the docs-only integration-test selector was skipped.
- **Reviewed repository state:** main is `166ca6b2cc9838ffd68c551b327ee41d2a5316b4`; live open-PR and open-issue searches returned zero.
- **Status:** documentation complete and reference CI-verified. No runtime behavior or site configuration changed. Pilot acceptance remains open.

## README pinned-install correction — PR #112 opening snapshot (2026-11-03)

- **Finding:** the root README still used `bench get-app ... --branch main`, while the Administrator Guide and Deployment Runbook correctly require pinning the approved full SHA before Bench dependency setup. That README example could install/build a moving branch before the release revision was checked.
- **Decision:** ADR-090 makes the README first-install path match the existing pin-before-install operator sequence. Existing-install upgrade instructions link to the Administrator Guide and Deployment Runbook.
- **Implementation:** PR #112 updates the README and release records and extends `test_operator_installation_pins_source_before_bench_setup` to assert that README's shell block verifies the approved SHA before Bench setup. No runtime code, dependency or site configuration changes.
- **Verification at opening:** the shell sequence was compared with the existing operator guide and runbook; a static regression test now protects the README ordering. Final-head Quality, Security, Python and Bench v15/v16 plus pinned Frappe 16.5.0 checks remain required because a test path changed.
- **Status:** documentation and static regression code-complete; CI pending; not pilot-verified. The authorized staging first-install/upgrade rehearsal remains a separate P0 acceptance gate.


## PR #112 merged — README pin-before-install consistency (2026-11-03)

- [x] PR #112 merged as [`d2e1d87`](https://github.com/MitMike/crm_signals/commit/d2e1d873a8f257545596379e179aeb3e4de40dd4) from final head `f68939ba5e2977ed62698e2a78084277fa091479`.
- [x] All 18 final-head checks passed: Quality/lint, Python 3.10/3.11/3.12/3.14, Semgrep, Bench v15/v16 + Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation.
- [x] README first-install instructions now pin and verify the approved full SHA before `bench setup requirements crm_signals`; static contract coverage enforces the order.
- **Scope:** README, docs and static test only; no runtime code, dependency or site configuration change.
- **Status:** merged and reference-stack CI-verified; first-install/upgrade staging rehearsal remains open. Not pilot-verified.

## D3 operator-guide correction — current implementation

- **Finding:** the Support & SLA setup guide's promise to build the standard adapter was stale; the discovery FAQ also implied custom sources could be adapted without an explicit approval boundary.
- **Decision (ADR-091):** state that the standard `HD Ticket` / `HD Service Level Agreement` adapter already exists. Custom/different ticket DocTypes remain unavailable until support, security and business owners approve a separate adapter scope, mapping and KPI semantics.
- **Implementation:** both HTML guides are corrected; `test_support_guides_describe_existing_adapter_and_custom_scope_boundary` protects the implemented standard-adapter statement and custom-source approval boundary.
- **Status at PR opening:** documentation and static regression code-complete; final-head CI pending; not pilot-verified. Final result is recorded below. No runtime code or site configuration changed.
- [ ] **Target-site D3 gate:** verify exact installed Helpdesk/Frappe versions, required schema and effective Sales field permissions, active SLA schedule/holidays/timezone, pause/resume and native outcomes on authorized Frappe v16.5 staging. Repository CI is not pilot evidence.


## PR-opening CI triage — D3 setup guide (2026-11-03)

- **Observed failure:** PR-opening Python 3.11 and 3.12 runs each reported 1 failed, 125 passed and 36 skipped. The failing static assertion found another stale promise in the Support & SLA setup guide's final workflow list: "We build a small adapter for the support app actually installed."
- **Additional defect:** the setup guide footer incorrectly identified itself as the read-only discovery guide.
- **Fix:** replaced the adapter promise with steps to validate/configure the existing standard adapter and keep custom sources behind separate approval; corrected the footer; extended the static contract test to reject both stale statements.
- **Status:** fix committed to the focused D3 branch; final-head CI must rerun. No runtime code, dependency or site configuration changed. Do not merge until all required final-head checks pass.


## Second D3 CI triage — assertion wording mismatch

- **Observed failure:** on head `87a5f8f479d291ddaf119c8d4938a9a2d30d54bc`, Python 3.11, 3.12 and 3.14 each reported 1 failed, 125 passed and 36 skipped.
- **Cause:** the setup guide correctly replaced the old promise with "custom sources require separate approval and scope", but the static test still asserted the previous wording "separately scoped adapter change".
- **Fix:** updated the static expectation to match the approved operator wording. This is a test expectation mismatch, not a runtime defect.
- **Status:** corrected on the D3 branch; a fresh final-head CI run is still required before merge.


## PR #117 merged — D3 operator-guide and static-contract correction (2026-11-03)

- [x] PR #117 merged as 93e7e16 (merge commit 93e7e16271d727476618b4981498ad901835bad4) from final head 2d7463f5e73bec3741ef9fb68d9b707b9bb1afc6.
- [x] All 35 final-head check runs passed: Python 3.10–3.14, Quality/lint/static, Security/Semgrep, Bench v15/v16 including Playwright, pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation, and both bench-validation selectors.
- [x] Pinned target validation passed Helpdesk schema/read-role contract, D3 synthetic aggregates, schema upgrade, asset build, Python tests and Frappe integration tests.
- [x] Static test failures on earlier heads were diagnosed and fixed: stale adapter promise in the guide, wrong footer, then obsolete test wording. No failing head was merged.
- Scope: documentation and static-test-only; no runtime code, dependencies, schema or site configuration changed.
- Current main: 93e7e16271d727476618b4981498ad901835bad4. PR #117 is closed/merged; the open-PR search was empty at merge.
- Status: code-complete and reference-stack CI-verified; not pilot-verified.
- [ ] Target-site D3 acceptance: verify installed versions, exact required fields, effective Sales read permissions, active SLA calendar/holidays/timezone, pause/resume and native outcomes on authorized Frappe v16.5 staging.


## PR #118 merged — post-PR117 documentation reconciliation (2026-11-03)

- [x] PR #118 merged as 3cb9f017b1694727f0b1729d5e2af9a7913a7715.
- [x] All 11 applicable final-head checks passed; two runtime selectors were skipped as expected for the documentation-only diff.
- [x] Implementation plan, progress, follow-ups, ADR-091 verification and changelog now record PR #117's 35/35 CI result and keep target-site acceptance separate.
- **Current main:** 3cb9f017b1694727f0b1729d5e2af9a7913a7715. Live open-PR and open-issue searches returned zero at review.
- **Scope:** documentation-only; no runtime code, dependency, schema or site configuration change.
- **Main-push checks:** Quality/Security checks for the PR #118 merge were still running at this review; PR final-head checks passed.


## PR #120 opening snapshot — effective-user permission preflight (2026-11-03)

- **Reviewed main:** `e57d3de9bad76d67caaa378bfb91bd0d692b9ec4`. The main push completed 16 check runs: 15 succeeded and the docs-only integration-test detector was skipped. Live open-PR and open-issue searches returned zero before this branch.
- **Finding:** the existing preflight reports static DocPerm rows and field permlevels, but operators still had to manually inspect whether named synthetic Sales User, Sales Manager, System Manager and non-sales accounts were active and had effective DocType/field read access.
- **Decision (ADR-092):** accept an optional alias-to-User mapping; validate active account and role boundary; use Frappe's user-aware DocType permission and permitted-field APIs; emit aliases and outcomes only. Never select test accounts automatically or return usernames/emails. Keep row-level permission and end-to-end checks separate.
- **Implementation:** `get_site_preflight_report(test_users=None)` now emits `effective_user_permissions`. It rejects Administrator, disabled, duplicate and invalid-role accounts; records DocType and required-field results per installed DocType; and fails closed to unavailable/partial status on lookup errors. Added regression tests for Sales User/Sales Manager/System Manager/non-sales outcomes, field-level differences, disabled/Administrator/role-mismatch/duplicate accounts, default-unavailable behavior, unknown profile rejection and identity non-disclosure. Updated the Administrator Guide, Deployment Runbook and Target-Site Acceptance Kit with the optional command and its limits.
- **Scope:** read-only diagnostic and tests/docs only. No schema, dependency, dashboard metric or site setting changes. Supported Frappe v15/v16 APIs were checked against both upstream version branches; final repository CI remains the compatibility gate.
- **Status at PR opening:** code-complete; final-head CI pending; not pilot-verified. The authorized target-site preflight and controlled-record permission matrix remain mandatory.
- **Independent release blocker / revisit criteria:** no authorized target-site session or sanitized discovery record is available. Resume site acceptance only when an authorized Frappe v16.5 staging window, approved full SHA, named technical/business/security owners and dedicated active synthetic test accounts are available. Then attach the alias-only preflight output and separately verify record-level User Permissions, ownership, shares, list/API/report/export/dashboard behavior, D1/D2 native-report reconciliation, Helpdesk SLA and operational recovery/rollback. Do not infer any of these from CI.


## PR #120 — real-Frappe effective-user permission smoke added (2026-11-03)

- **Finding:** the first PR #120 final head passed all four workflows, including Bench v15/v16 and pinned Frappe 16.5.0, but the new effective-user probe was exercised only by mocked unit tests. The Bench workflows did not call the probe against real Frappe User and DocType metadata.
- **Decision (ADR-093):** add a CI-only `allow_tests`-guarded fixture that provisions disposable Sales User, Sales Manager, System Manager and Employee accounts with random throwaway passwords, runs the production preflight, and checks complete result types/status and identity non-disclosure.
- **Implementation:** `crm_signals.ci.verify_effective_user_preflight` is invoked in both the v15/v16 Bench matrix and the pinned v16.5.0 workflow. It creates no business documents, returns aliases/counts only and refuses to run unless `allow_tests` is enabled.
- **Status:** code-complete; final-head CI for the additional real-Frappe smoke is pending. The original PR #120 head `ac444d5` had all four workflows successful, but that result does not cover this follow-up commit.
- **Scope:** CI fixture and workflow wiring only; no production runtime behavior, schema, dependency, metric or site configuration changes.
- **Remaining gate:** final-head Python 3.10–3.14, Quality, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 checks must pass. The synthetic CI fixture is compatibility evidence only; authorized target-site permission and controlled-record acceptance remain open.


### PR #120 CI triage — complexity guard

- **Observed:** Quality Checks on head `51c8e6d` failed in lint with `C901 verify_effective_user_preflight is too complex (19 > 15)`. Other workflows were still running; this was a deterministic code-quality failure, not a Frappe runtime result.
- **Decision:** keep the same integration coverage and split validation into profile-level and report-level helpers. Do not suppress the complexity rule.
- **Correction:** refactored the fixture into `_validate_effective_user_preflight_profile`, `_validate_effective_user_preflight_report` and a short orchestration function. A fresh final-head Quality and full integration matrix is required.


### PR #120 input-validation hardening

- **Finding:** `_effective_user_permissions` treated every falsey value as “not supplied” before validating the input type. An empty list/string could therefore be reported as an unavailable optional probe instead of rejected as malformed configuration.
- **Decision:** only `None` or an empty dictionary means the optional mapping was omitted. Reject all non-dictionary values before testing whether the mapping is empty.
- **Implementation:** added regression coverage for falsey non-mappings (`[]`, empty string and `0`). This is a focused input-contract correction; final-head CI must rerun.


### PR #120 account-type validation hardening

- **Finding:** role membership and enabled status alone could accept a Website User carrying a sales role, even though the CRM Signals Desk is intended for System Users.
- **Decision:** require `User.user_type == System User` before effective DocType/field permission checks. Reject Website Users as `user_type_not_system`; do not run permission checks for them.
- **Implementation:** add a regression test for an enabled Website User with the Sales User role; assert the probe rejects it without returning account identity. Extend the real-Frappe CI fixture to assert every synthetic profile is a System User.
- **Status:** code-complete; final-head CI must rerun after this change.


## PR #120 merged — effective-user permission preflight (2026-11-03)

- **Merge:** `a778c47b5078ac69dd89bdcd3ecab41de09b8072`; final tested head: `e95efccec019df3fbadd1703f34c5682340b7f58`.
- **CI:** all 18 final-head check runs passed, including Quality/lint, Security/Semgrep, Python 3.10–3.14, Bench v15/v16 with Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. The real-Frappe effective-user probe step passed on Bench v15, Bench v16 and pinned v16.5.0.
- **Implementation:** optional read-only `effective_user_permissions` matrix checks explicit active System User accounts for DocType and required-field read access; rejects Administrator, Website User, disabled, duplicate and invalid-role accounts; emits aliases and outcomes only. ADR-092/093 record the scope and compatibility test.
- **Status:** code-complete and reference-stack CI-verified. It is not pilot-verified and does not test record-level User Permissions, ownership, shares, list/API/report/export/dashboard visibility.
- **Next gate:** authorized Frappe v16.5 staging with approved full SHA, named technical/business/security owners and synthetic test accounts. Complete controlled-record permission tests, D1/D2 native-report reconciliation by currency, Helpdesk SLA acceptance, deployment/rollback, operational recovery and desktop/mobile visual UAT. No staging evidence is connected to this review.



## PR #122 opening snapshot — synthetic record list-visibility preflight (2026-11-03)

- **Reviewed main:** \`8543da5c2270a816608ba23927a6ee35571e5bde\`. PR #120's 18 final-head checks passed. PR #121 is merged; its post-merge Quality Checks, Security Scanning and Bench Integration/E2E workflows all completed successfully (runs 41594704324, 41594704313 and 41594704329). Live open-PR and open-issue searches returned zero before this branch.
- **Finding:** ADR-092/093 verifies active synthetic account identity, role boundaries, DocType read and required-field read, but leaves row-level list visibility entirely manual. That is the next useful P0 operator aid; V Vault and A Analysis remain blocked by signed D1/D2 semantics and retention/source-visibility approvals, so they must not be started on provisional metrics.
- **Decision (ADR-094):** add an optional \`test_records\` mapping only for explicitly supplied synthetic System Users and exact synthetic record names. Temporarily switch to each user and call Frappe's permission-filtered \`get_list\` with an exact name filter and \`fields=["name"]\`. Return non-sensitive labels and booleans only; never return record names or business fields. Missing and inaccessible records both report false. Bound input to 50 records per profile and 100 total, and allow only the preflight's known business DocTypes.
- **Implementation:** the read-only preflight now reports per-profile/per-DocType list visibility when \`test_records\` is supplied; restores the previous session user in a \`finally\` block; fails closed on query/session errors; and skips list queries when DocType read is denied/unavailable. Unit tests cover visible/invisible results, name/identity non-disclosure, permission denial, error restoration and malformed/bounded input. The disposable real-Frappe CI fixture creates one synthetic CRM Signal, checks it as System Manager, and rolls it back.
- **Scope:** optional diagnostic and CI-only fixture; no schema, dependency, metric, dashboard or site-configuration changes. The command remains non-whitelisted and read-only. It does not establish direct form/API/report/export/print/dashboard access or pilot acceptance.
- **Status at PR opening:** code-complete; final-head CI pending. Require Python 3.10–3.14, Quality, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 before merge.
- **Release blocker / revisit criteria:** no authorized Frappe v16.5 staging session or approved synthetic site records are connected to this review. Run the optional probe only after the approved SHA and exact versions are confirmed on staging. Continue to require direct form/API/report/export/print/dashboard tests, D1/D2 native-report reconciliation by currency, Helpdesk SLA, operational recovery, backup/restore/rollback and visual UAT. No pilot verification is claimed.
