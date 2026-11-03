# CRM Signals — Deferred follow-ups and production acceptance

This file records known work that is intentionally not represented as complete. Revisit an item when its trigger or dependency is satisfied.

**Ownership convention:** P0 target-site items belong to the site administrator/implementation lead with the relevant security or finance owner; P1 engineering items belong to CRM Signals maintainers; site-specific configuration items belong to the Sales Manager/business owner; P2 roadmap items belong to the product owner. Close an item only with the evidence described below.

## P0 — required before production sign-off

- [ ] **Target-site preflight and acceptance.** Use the updated evidence template in [Target-Site Acceptance Kit](TARGET_SITE_ACCEPTANCE.md), including the staging-only Redis Socket.IO outage, worker restart, scheduler recovery and permission-revocation checks. Record the exact Frappe v16.5 patch/build, ERPNext and Helpdesk app versions, installed apps, Company currencies, timezone, workflows, custom fields and role matrix. Run Pilot import, migrate, scheduler, email, realtime, dashboard and rollback smoke tests.

  **Current blocker / revisit criteria (reviewed 2026-11-03):** Repository access is available, but no target-site session or sanitized discovery record is connected to this work. The read-only preflight reports the exact CRM Signals Git SHA only for a clean app checkout. PR #120 adds an optional alias-only DocType/field probe; PR #122 adds a bounded alias/label-only list-visibility probe for exact synthetic records using permission-filtered `frappe.get_list`. Neither discovers/selects users or returns record names/business fields. PR #126 adds real-Frappe calls to `frappe.client.get` and `frappe.client.get_list` for the same linked-restricted/unlinked-owned pair; these are direct Python method-wrapper tests, not HTTP transport/authentication or browser form tests. The list probe still returns false for both missing and inaccessible records. Direct authenticated HTTP, browser form, report/export/print/dashboard acceptance remains staging work. Revisit when an authorized operator supplies the approved-SHA-matched preflight output, exact `bench version` and installed-app inventory, Company base currencies, timezone, workflows, active Helpdesk SLA calendar and controlled-record permission evidence from an approved Frappe v16.5 staging site. Finance/business/security owners must approve Company thresholds, SLA interpretation, webhook controls and retention policy. Until then, do not infer live-site values or pilot results from reference-stack CI.
- [ ] **Permission parity.** Verify Sales User, Sales Manager, System Manager and non-sales users across list, direct form, API, report, export and print. PR #122 checks exact synthetic-record list visibility and PR #126 now verifies the standard `frappe.client.get` / `get_list` wrappers against a real Sales User User Permission fixture. Direct authenticated HTTP/cookie/routing behavior, browser form loading, report/export/print and dashboard paths still require live tests. Notifications are not an authorization grant. Realtime recipients must be able to read the CRM Signal, linked Lead/Customer and originating source DocType; PR #44 adds the source-document check. The scheduled digest queries Leads and Quotations separately under each recipient's user context; confirm both paths with the target site's actual permissions.
- [ ] **D2 financial reconciliation.** Compare invoices, Payment Entry receipts, separate POS receipts and party-account-currency receivables to native ERPNext reports, by currency.
- [ ] **Webhook operations.** Provision a dedicated integration System User, least-privilege create access, TLS, gateway rate limiting, monitoring, secret rotation and secure secret storage.
- [x] **Pin-before-install command correction (ADR-074/077; PR #82 merged as `ac030b1`, CI-verified).** The unsafe post-`bench get-app` SHA checkout is replaced by direct clone with `--origin upstream`, detach and verify the approved full SHA, then `bench setup requirements crm_signals` before site install/migration/build. Upgrade instructions inspect the Bench-created `upstream` remote rather than assuming `origin`. Final head `ef4dc09` passed Quality, Security, Frappe v15/v16 Bench + v16 Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. **Still open:** execute the sequence in an authorized staging Bench and record the exact SHA, versions and output; CI is not target-site or pilot verification.
- [ ] **Target-site deployment rehearsal.** The generic backup, migration, smoke-test and rollback procedure is documented in [Deployment Runbook](DEPLOYMENT_RUNBOOK.md); execute it with the intended site's actual backup, restore, app revision and process manager before sign-off.

## Repository maintenance

- [x] **PR #89 documentation/ADR-075 skip-path reconciliation:** merged as `ac6b253`; final head `0967290` passed Quality, Security and Bench Integration/E2E. This confirms the docs-only selector path while stable required contexts pass.
- [x] **PR #7 setup-uv v7:** merged as `331492c`; final head `a72c82c` passed all 18 check runs, including Quality, Security/Semgrep, Python 3.10/3.11/3.12/3.14, Frappe v15/v16 Bench + Playwright and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0.
- [x] **Historical dependency queue (reviewed against main `331492c`; superseded):** PR #8 setup-node v7 merged as `63c2734`; PR #10 setup-python v7 closed unmerged and was superseded by PR #94 (`926619b`); PR #9 flit-core `>=3.4,<5` closed unmerged and was superseded by PR #96 (`d0ab24b`). Do not reuse their stale-head checks; see the later maintenance snapshot for final verification.
- [x] **Upload-artifact v7 (PR #88):** merged as `de8e78b`; final head `eed57d6` passed Quality, Security, Bench v15/v16 + Playwright and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. PRs #6 and #87 were closed unmerged; #88 is the verified replacement.
- [x] **GME workspace label (ADR-076; PR #85):** merged as `5cc4308` after all four final-head workflows passed on `b09a0cb`. Only workspace label/title changed; technical identifiers and routes were preserved.
- [x] **Dashboard inset fix (BUG-2026-001 / FIX-2026-001; PR #84):** merged as `b1f4ad7`; final head `f0e1909` passed Quality, Security, Bench v15/v16 and pinned v16.5.0. **Still open:** rebuild/refresh the intended UAT site's assets/cache and capture desktop/mobile evidence before marking UAT-verified.
- [ ] **Closed UI/governance PRs:** #75 and #78 were closed unmerged and superseded by #85/#84. #80/#81 were closed unmerged; the optional regression-review template was not merged and is not a release gate.

## P1 — engineering reliability improvements

- [x] **Change-aware CI (ADR-075; PR #76 merged as `cec49e7`).** Final head `d6a6300` passed all 19 check runs, including Quality, Security/Semgrep, four Python versions, Bench v15/v16 + Playwright and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. Required check names remain stable, detector failures fail closed, runtime/package/workflow/workspace/migration selectors are protected by static tests, and Quality feature-branch duplicate push runs are removed. PR #85 exercised workspace JSON together with `tests/test_static_contracts.py`; all four workflows passed on final head `b09a0cb`. Because the PR changed both a Python/test path and a workspace metadata path, Python and Bench ran. This verifies the combined runtime/metadata route, not the Python skip path. PR #89 is docs-only and is the clean revisit trigger for confirming successful path detection skips Python/Bench execution while stable required contexts pass; workspace JSON must continue to trigger Bench and pinned validation.

- [x] **H-AC11 High-Value Quote source drill-down (ADR-069/071/072; PR #71):** merged as `c5720bf`; final head `df0c273` passed Quality, Security, Python 3.10/3.11/3.12/3.14, Frappe v15/v16 Bench Integration/E2E including Playwright, and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. The exact Prettier 3.9.10 diff was emitted by the failure-only CI diagnostic and applied in commit `91fc89c`; the formatting check remained blocking and passed on the final head. **Still open for pilot:** verify the source link with target-site Sales User, Sales Manager and non-sales personas, including source-permission revocation; CI is not pilot acceptance. PR #72's duplicate POS/preflight documentation was closed as superseded by #71; its evidence is retained under ADR-070 for POS settlement and ADR-068 for preflight.
- [x] **Read-only target-site preflight report (ADR-068; PR #70):** merged as 13341b756e2d2a92c9432f3c50ac77594e2483e9 after all final-head required Quality, Security, Python, Frappe v15/v16 Bench and pinned v16.5.0 checks passed. The non-whitelisted Bench command reports app versions when importable, Company base currencies and threshold source/amount/currency, site timezone, active Lead/Opportunity workflows, relevant DocType fields/Select options/permlevels and static DocPerm rows. It omits recipient addresses and business-document rows and performs no writes. **Still open as P0 acceptance:** run it on the authorized target site, complete real-user permission tests, finance/native-report reconciliation and SLA/operations rehearsal.

- [x] **D2 real POS settlement fixture (ADR-070; PR #69):** merged as `efe78729881390cacba343749364ceccdcb7ffb2`; synchronized final head `33b750a` passed all 15 checks, including Quality, Security/Semgrep, Python 3.10/3.11/3.12/3.14, Bench v15/v16 + Playwright and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. The fixture creates a disposable POS Profile and company-specific Mode of Payment, submits an `is_pos` Sales Invoice through ERPNext and asserts ERPNext-calculated paid/grand-total settlement. Browser checkout, POS Opening/Closing, cash-drawer and inventory workflows remain out of scope; target-site native-report reconciliation and role acceptance remain P0.

- [x] **D1/D2 real query-contract smoke in Bench CI (PR #63).** Merged as `0a7de966`; the read-only Sales Compass API executes against installed ERPNext DocTypes on Frappe v15/v16 and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane. Quality, Security, Semgrep, Python, Bench and pinned-target checks passed. This is compatibility evidence only, not a financial-value fixture or target-site reconciliation.

- [x] **D2 independent source-permission fix (PR #65).** Merged as `0cfeda4`. Payment Entry customer receipts now run even when Sales Invoice access is denied; regression tests cover both the split-permission case and a query-level invoice `PermissionError` after a partial invoice result. Final-head Quality, Security/Semgrep, Python 3.10/3.11/3.12/3.14, Bench v15/v16 and pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 checks passed. The P0 target-site role matrix and native-report reconciliation remain open; CI does not prove the pilot's actual permissions or totals.

- [x] **D1/D2 synthetic aggregate-value fixture (PR #67; merged as `84ab2ce`; final-head CI-verified):** The fixture provisions a disposable setup-wizard Company/chart, Customer, Item, Lead, Opportunities, submitted Sales Invoices and an allocated Payment Entry on Frappe v15/v16 and the pinned v16.5.0 stack. It asserts aggregate deltas, INR/USD Opportunity and invoice grouping, party-account-currency receivables, overdue/POS/receipt filters and a real split-permission user. The POS row models persisted aggregate fields only; it does not test POS settlement. All synthetic records and temporary permissions are rolled back. Target-site native-report reconciliation and Sales User/Manager permission acceptance remain separate open gates.

- [x] **Explorer backend field-permission review and merge (PR #57).** The final head `dda6eb88c0e8735645018de60275d9cf55d2d99d` passed Quality Checks, Security Scanning, Frappe v15/v16 Bench + Playwright and the pinned Frappe v16.5.0/ERPNext v16.5.0/Helpdesk v1.28.0 lane; merged as `ba631720`. The earlier cancelled-check head was not bypassed.

- [x] **Exact target CI (PR #50 merged):** the pinned lane installs Frappe `v16.5.0`, ERPNext `v16.5.0`, Telephony commit `9447577500a25d242088398157b72c654fa34b20` and Helpdesk `v1.28.0`, then verifies HD Ticket/HD Service Level Agreement schema and permlevels, runs the real D3 aggregate API smoke test, and exercises CRM Signals install/upgrade. Trigger it for app/test changes, not docs-only changes; retain the existing v15 and moving v16 matrix. PR #50 merged as `24a9b8d3d178682a68df418f5cd29582644056c8` after the final-head exact target lane passed Helpdesk install/schema/role, D3 aggregate smoke, CRM Signals upgrade, full asset build and Bench tests, and the required v15/v16 matrix passed. Pilot-site app versions and live acceptance remain. The inspected Helpdesk v1.29.0/v1.30.2/v1.31.1 desk manifests link `@framework/ui` to the absent `frappe/ui` package; the v1.30.2 exact run failed during its after-migrate asset build. Helpdesk v1.31.1 additionally expects the absent `Notification Type` DocType. Use v1.28.0 as the reference unless the exact Frappe build supplies these dependencies.


- [x] **Durable signal outbox and audited replay.** PR [#26](https://github.com/MitMike/crm_signals/pull/26) merged as `b0364a74affa823977af74d1907781d1533e60c0`; PR [#38](https://github.com/MitMike/crm_signals/pull/38) merged as `1640bdd496706a7f297b0984f1fd1d9695307147`. Source event/outbox persistence is transactional; delivery is queued after commit; bounded retries, scheduled recovery and a System Manager-visible Failed state are included. Terminal Failed-row replay is POST-only, System Manager + outbox-read-gated, preserves attempts and records actor/time/comment. **Remaining:** verify scheduler, failure monitoring, replay and backup/restore on the pilot site. Durable realtime retry is tracked in the next item and is not part of the transactional event outbox.
- [x] **Implementation and CI verification for durable realtime retry (PR #54 merged).** The per-recipient ledger, stable delivery ID, bounded retry, permission recheck and active-session client deduplication are merged as `37ce6003c9459f1b391de5dff8354e4bfc04cb9b`. Final synchronized head `f1cbd3e92946a4a5513b7555396cada4491fdd3e` passed all eight required ruleset contexts (Python 3.10/3.11/3.12/3.14, lint/static, Semgrep, Bench v15/v16) and the pinned Frappe v16.5.0/ERPNext v16.5.0/Helpdesk v1.28.0 lane. Earlier test triage corrected signal-scoped realtime mock assertions and isolated the scheduler fixture with a unique synthetic recipient; the final v15/v16 Bench and Playwright suites passed. This is code/test CI verification, not pilot verification. PR #55 merged the staging acceptance procedure; execution on the approved target-site staging environment remains open.
- [ ] **Pilot acceptance for durable realtime retry.** On the target Frappe v16.5 site, inject Redis unavailability and a worker restart; prove the minute scheduler retries pending/attempted deliveries, stable IDs suppress duplicate toasts after reconnect, and permission revocation cancels later attempts. Record scheduler/worker logs and the resulting delivery-ledger states. Revisit after the pilot site and an authorized test user are available.
- [x] **Digest concurrency proof.** PR #23 merged as `d75b7f3`. The Settings-singleton row lock and per-recipient marker recheck passed the two-worker Bench test on Frappe v15 and v16; v16 Playwright also passed. Live scheduler topology, mail-provider behavior and recipient policy still require target-site validation.
- [x] **API idempotency contract coverage.** Bench-backed tests cover same-user duplicate POST deduplication, one notification per event, cross-user source namespacing, unique-key enforcement, legacy null keys and the deterministic two-connection insert race. The race test and migration rehearsal passed on Frappe v15 and v16 in PR #23/#21; quality, security and v16 Playwright checks also passed. Broader HTTP gateway/load testing remains a separate optional stress test.

## P1 — site-specific configuration decisions

- [x] **Multi-company threshold policy.** PR #45 merged as `ff434bdf407d1d61842d81fae16e04b4b9b483d5`; PR #49 merged the child-row Currency `options`/`fetch_from` correction as `2e9eb89b8ed5618ca3e50e6bc0b2c867c516e17b`, so the Company base currency displays correctly. Each enabled Company still needs an explicitly approved non-negative threshold in its base currency; the legacy site-wide threshold is used only on an exact base-currency match. No implicit FX conversion. Target-site Company-by-Company amount approval and currency-change reapproval remain.
- [ ] **Opportunity and Lead semantics.** Confirm the exact trigger statuses and terminal Lead statuses from the live site's workflows. Confirm the Lead modified timestamp is an acceptable proxy for attention.
- [ ] **Digest policy.** Confirm timezone, delivery time, additional recipients, mail-queue behavior and stale window with the Sales Manager/business owner.

## P2 — S.A.H.D.E.V. roadmap

- [ ] **D3 target-site acceptance:** the standard Frappe Helpdesk adapter merged in PR #32 and passed Frappe v15/v16 CI. Record the exact target Frappe v16.5 patch, ERPNext and Helpdesk versions; verify Sales User/Manager HD Ticket and SLA DocType plus field-level read permissions; confirm each active SLA's Monday–Saturday schedule, hours, holiday list and timezone. The field-level fail-closed guard merged in PR #42; CI is not site acceptance.
- [ ] **H Highlights — business policy:** High-value Quotation alerts and per-Company threshold implementation are in place; the new regression tests cover threshold equality, below-threshold suppression and missing currency basis (PR #60). Confirm Company amounts/currency and Lead/Customer recipient behavior on the target site. Do not add VIP allowlist/escalation fields until the product owner approves the triggering events, priority/threshold effect, recipient rules and cooldown (ADR-061).
- [ ] **H Highlights — proposal tracking:** first-party proposal-link tracking remains disabled until privacy/consent, lawful basis, data minimization, scanner classification, retention period and deletion process are approved. Then implement opaque expiring/revocable tokens, stable event IDs, human/automated/unclassified classification and 24-hour recipient cooldown. No arbitrary external URL tracking.
- [ ] **E Explorer — pilot and optional sources:** PR #57's core API, PR #59's Desk page/form actions and PR #61's browser/operator hardening are merged. PR #61 merged as `6ef9642b63c24053fb437f67d9d4fb47e360c80a`; final head `902b38e4dd4713461acfb12dc837f5b2b84da7d8` passed all eight required contexts (Python 3.10/3.11/3.12/3.14, lint/static, Semgrep, Bench v15/v16) and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane. Playwright verifies all five GET context routes and stale-response suppression; the deployment runbook now covers Company-currency thresholds and Explorer role/context smoke tests. The [Target-Site Acceptance Kit](TARGET_SITE_ACCEPTANCE.md#10-e-explorer-activity-timeline-acceptance) remains the pilot gate: execute real Sales User/Manager and non-sales record/field-permission checks, record installed optional providers and exact schemas, and verify the live source-state/pagination/timezone behavior before adding optional adapters.
- [ ] **V Vault — blocked pending metric and policy acceptance:** do not implement snapshot scheduling until D1/D2 definitions are reconciled against native ERPNext reports and signed by Sales/Finance; the reporting population and source-visibility policy are approved; and the retention period, deletion process, pruning owner and audit evidence are recorded. Revisit when the target-site record contains signed metric IDs/versions, currency/date semantics, source permission matrix, retention schedule and an approved dry-run pruning boundary. Then implement append-only, idempotent aggregate snapshots. Add D3/H only after their source contracts are separately accepted.
- [ ] **A Analysis — blocked pending D1/D2 target-site reconciliation:** do not expose query intents until Sales/Finance reconcile D1/D2 definitions with native ERPNext reports and approve currency basis, date windows, filters, groupings and source permissions. Revisit when the target-site record contains approved metric IDs/versions, native-report variance sign-off, allowed filters/groupings, source DocType/field permission matrix and metric owners. Then build the server-owned versioned registry and deterministic intent templates. Register D3/H only after their own acceptance. Arbitrary generated SQL/Python remains prohibited.

## Operating rule

Do not close a follow-up because code compiles or a mocked unit test passes. Close it only with evidence from the relevant unit/Bench/E2E tests and, for site-dependent items, a recorded target-site validation result.


## P2 — Dependency maintenance

- [x] **PR #7 — setup-uv v7:** merged as `331492c` after all 18 final-head checks passed.
- [x] **PR #8 — setup-node v7:** merged after refreshed final-head checks passed.
- [x] **PR #94 — setup-python v7:** merged as `926619b` after all final-head checks passed.
- [x] **PR #97 — maintenance documentation reconciliation:** merged as `b18f504` after final-head Quality, Security and Bench Integration/E2E passed.
- [x] **PR #96 — flit-core v4 build-system range:** merged as `d0ab24b6a50184af99f4af638ae64ddd9a22d08a` after all 20 final-head check runs passed on `349bf71b0687c77e830fb8b054cedacabb16f61b`. The v4 wheel and sdist built, installed in clean environments and imported on Python 3.10 and 3.14; the full Python 3.10/3.11/3.12/3.14, Security/Semgrep, dependency audit, Frappe v15/v16 Bench + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lanes passed.
- [ ] **Target-site pilot acceptance:** collect the sanitized read-only preflight and installed app/full-SHA inventory, then validate effective permissions, D1/D2 financial reconciliation by currency, Helpdesk SLA calendar, scheduler/mail/realtime/webhook operations, and backup/restore/rollback rehearsal.
- [ ] **Dashboard visual UAT:** after an approved staging asset refresh, capture desktop/mobile screenshots confirming the horizontal inset and close BUG-2026-001/FIX-2026-001 only with evidence.

This snapshot supersedes older dependency queue entries above. Never merge stale PR heads or bypass required checks.


## Current repository maintenance snapshot — 2026-11-03 (after PR #96)

- [x] **PR #96 — flit-core v4:** merged as `d0ab24b6a50184af99f4af638ae64ddd9a22d08a`. Final head `349bf71b0687c77e830fb8b054cedacabb16f61b` passed all 20 checks, including wheel/sdist build and clean-environment install/import with flit-core v4 on Python 3.10 and 3.14, full Python 3.10/3.11/3.12/3.14 tests, Security/Semgrep and dependency audits, Frappe v15/v16 Bench + Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0.
- [x] **Maintenance queue:** no open pull requests remained immediately after the merge (live open-PR search returned zero).
- [ ] **Dashboard visual UAT:** obtain approved staging asset refresh and desktop/mobile screenshots; close BUG-2026-001/FIX-2026-001 only with evidence.
- [ ] **Target-site pilot acceptance:** still requires authorized staging access, exact installed app/full-SHA inventory, effective permission tests, D1/D2 reconciliation by currency, active Helpdesk SLA calendar, scheduler/mail/realtime/webhook checks and backup/restore/rollback rehearsal.

This snapshot supersedes the older dependency queue entries above. A green CI result is reference-stack verification only; it is not target-site or pilot verification.


## Post-merge verification — 2026-11-03

- [x] PR #98 merged as `1a27166bfe988c860b3527af5bba9a0299e1e30f`; all 13 final-head checks completed successfully.
- [x] Docs-only path detection skipped runtime Python/Bench execution as designed; Python tests, lint/static, Semgrep, Bench v15/v16 validation and v16 Playwright completed successfully.
- [x] Live open-PR search returned zero immediately after merge.
- [ ] Dashboard visual UAT: obtain staging desktop/mobile evidence before closing BUG-2026-001/FIX-2026-001.
- [ ] Target-site pilot: collect authorized v16.5 staging inventory, effective-role tests, D1/D2 reconciliation, Helpdesk SLA evidence, operational recovery and backup/restore/rollback rehearsal.


## P1 — dashboard visual regression prevention

- [x] **BUG-2026-001 / FIX-2026-001 automated guard (ADR-083/084; PR #100):** merged as 9c4febf8180ef295b48ea18b1ac5fddc164ff34f from final head 50759954b8801fb8edd7194fea354c3521b457f1. All 18 final-head check runs passed, including Bench v15/v16 and the v16 Playwright desktop/mobile computed-padding assertion. This closes the automated regression-prevention task only; staging visual UAT remains open.


## Latest repository snapshot — after PR #100 (2026-11-03)

- [x] PR #100 merged; all 18 final-head check runs passed on 50759954b8801fb8edd7194fea354c3521b457f1. Merge commit: 9c4febf8180ef295b48ea18b1ac5fddc164ff34f.
- [x] Open pull-request search returned zero. No CI failure or stale open PR is currently awaiting action.
- [ ] **Dashboard visual UAT (revisit trigger):** proceed only when an authorized staging site is available, the approved full CRM Signals SHA is deployed, and the operator has completed the documented asset build/cache refresh. Capture 1440px desktop and 390px mobile screenshots with the SHA, browser, role and timestamp; record the observed inset. Keep BUG-2026-001/FIX-2026-001 UAT-open until evidence is reviewed.
- [ ] **Target-site pilot (revisit trigger):** proceed when an authorized Frappe v16.5 staging window and named technical/business owners are available. Collect exact app/build inventory, effective permissions, D1/D2 reconciliation, active Helpdesk SLA calendar, operational recovery and backup/restore/rollback evidence. No production change without the site's approved change control.
- [ ] **Deferred product slices:** Vault/Analysis require signed D1/D2 metric and source-permission contracts plus retention/deletion policy; VIP escalation requires approved membership, trigger, recipient and cooldown; proposal tracking requires privacy/consent and retention approval; optional Explorer adapters require provider/version/schema/identity/permission inventory. Revisit only when those exact inputs are recorded in the target-site acceptance record and the relevant product owner approves them.

A green reference CI result is not a substitute for any of these site-specific gates.



## Latest repository review — 2026-11-03 (main `5dbda02`, after PR #103)

- [x] PR #100 dashboard inset browser guard merged as `9c4febf`; all 18 final-head checks passed, including Bench v15/v16 and v16 Playwright.
- [x] PR #101 target-site visual-UAT kit and documentation reconciliation merged as `0772afde`.
- [x] PR #102 stale dependency follow-up reconciliation merged as `135e648`; all 16 final-head check runs completed: 15 succeeded and the integration-test change detector was skipped as expected for the documentation-only diff.
- [x] PR #103 read-only source SHA preflight merged as `5dbda0291358350d5a720127a7d526145d3e3c60`; all 18 final-head check runs passed, including Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0.
- [x] Live open-PR search returned zero after PR #103 merged.
- [x] **Read-only preflight SHA capture (ADR-086):** code-complete and CI-verified. It reports a full SHA only for a clean checkout; operators must match it to the approved release SHA.
- [ ] **Dashboard visual UAT and target-site pilot:** still blocked by the absence of an authorized staging session and target-site evidence. The exact revisit criteria above remain unchanged.

The PR's CI result does not establish that a customer site has the approved SHA, clean checkout, rebuilt assets, correct effective permissions, reconciled D1/D2 figures, validated Helpdesk SLA, or passed recovery/rollback rehearsal. No pilot verification is claimed.


## Preflight repository-root identity hardening — merged (2026-11-03)

- [x] **PR #105:** merged as [`db95812`](https://github.com/MitMike/crm_signals/commit/db958124bca6a6704a75f606629c22444716f5b9) from final head `fd2161dc933fbaf74fd5a50a5261e5f1501b283e`. All 19 final-head check runs passed: Quality/lint, Python 3.10/3.11/3.12/3.14, Security/Semgrep, Bench v15/v16 + Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0.
- **Evidence/decision:** ADR-087 requires `git rev-parse --show-toplevel` from the imported package directory to resolve to the CRM Signals repository root. Git otherwise searches parent directories and could return an unrelated enclosing repository's SHA. A mismatch fails closed before cleanliness and `HEAD` checks. Unit coverage verifies both the expected root and rejection of a parent root.
- **CI triage:** initial Python 3.11 and 3.12 runs each exposed one stale test assertion for the added root-check call. The corrected final head passed all required contexts; no application behavior failure remained.
- **Status:** code-complete and reference-stack CI-verified; not pilot-verified.
- [ ] **Independent release blocker:** target-site visual UAT and pilot acceptance still require an authorized Frappe v16.5 staging session, approved SHA, named owners and the evidence listed in `TARGET_SITE_ACCEPTANCE.md`. No pilot verification is claimed.



## Real-Git nested-parent regression — PR #107 opening checklist (2026-11-03)

- **At PR opening:** [PR #107](https://github.com/MitMike/crm_signals/pull/107) created a committed temporary parent repository and nested Bench-style app path, then verified the real preflight rejects the enclosing Git root. Final merge and CI evidence are recorded in the later PR #107 section below.
- **Decision:** ADR-088 supplements mocked root-mismatch coverage with a real Git integration test because the failure mode depends on Git's upward repository discovery.
- **Revisit criteria at PR opening:** If any final-head Python/Quality/Security/Bench/pinned lane failed, inspect its job log and correct the test/environment issue before merge. If Git is unavailable in a supported CI environment, make that prerequisite explicit rather than silently skipping the regression. This test is not pilot verification.


## Real-Git nested-parent regression — PR #107 merged (2026-11-03)

- [x] **PR #107:** merged as [`a472f19`](https://github.com/MitMike/crm_signals/commit/a472f1981f758ce7b6233d95fc0682fe69d7a304) from final head `a47c3975eebe52dccb918a1056cf30d818cdcae4`. All 19 final-head check runs passed across Quality/Python 3.10–3.14, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0.
- **Decision:** ADR-088 adds a real temporary parent Git repository and nested Bench-style package test to prove Git's upward discovery is rejected by the production preflight helper. This complements deterministic mocked failure-path tests.
- **Status:** code-complete and reference-stack CI-verified; no runtime change; not pilot-verified.
- [ ] **Release blocker:** target-site acceptance remains blocked until an authorized Frappe v16.5 staging session, approved full SHA, named technical/business owners and test accounts are available. Then collect dashboard screenshots, effective-role permission results, D1/D2 reconciliation, Helpdesk SLA evidence, scheduler/mail/realtime/webhook recovery and backup/restore/rollback results. Do not treat green CI as site acceptance.


## Real-Git clean/dirty source identity regression — PR #109 opening snapshot (merged; see below)

- **PR #109 at opening:** [test: exercise real clean and dirty preflight Git states](https://github.com/MitMike/crm_signals/pull/109). The test initializes a temporary CRM Signals repository, commits the package, checks that preflight returns the exact real SHA, then adds an untracked Python file and checks that preflight fails closed with `working_tree_dirty` without reading `HEAD`.
- **Decision:** ADR-089 complements ADR-087/088 by exercising both real clean and dirty Git behavior; mocked tests remain responsible for deterministic error injection.
- **Revisit criteria:** if a final-head Python/Quality/Security/Bench/pinned lane fails, inspect the exact job log and fix the test/environment issue before merge. If Git is absent in any supported CI lane, make that prerequisite explicit rather than silently skipping the integration test. No runtime or site configuration change is included.
- **Status at PR opening:** code-complete; CI pending; not pilot-verified. Final merge evidence is recorded below. The separate target-site acceptance blocker remains unchanged.


## Real-Git clean/dirty source identity regression — PR #109 merged (2026-11-03)

- [x] **PR #109:** merged as [`94d14f5`](https://github.com/MitMike/crm_signals/commit/94d14f56a526670d2c0ecb150ab9f08b4f034389) from final head `d8b65eedc45c05947409f9781a9caaee848aa4ba`.
- [x] All 18 final-head check runs passed: Quality/lint, Python 3.10–3.14, Security/Semgrep, Bench v15/v16 including Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0.
- [x] The real-Git test returned the exact clean temporary repository SHA, then rejected an untracked Python override as `working_tree_dirty` without querying `HEAD`.
- **Decision:** ADR-089 closes the real clean/dirty Git behavior gap; retain the mocked timeout, missing-Git, command-failure and invalid-SHA tests for deterministic failure injection.
- **Status:** code-complete and reference-stack CI-verified; test-only; not pilot-verified.
- [ ] **Release blocker / revisit criteria:** proceed only when an authorized Frappe v16.5 staging window, approved full SHA, named technical/business owners and test accounts are available. Then collect exact installed app inventory, dashboard desktop/mobile screenshots after approved asset rebuild/cache refresh, effective-role permission results, D1/D2 finance reconciliation by currency, Helpdesk SLA evidence, scheduler/mail/realtime/webhook recovery and backup/restore/rollback rehearsal. No target-site evidence is available from repository CI.


## PR #110 release-document reconciliation — merged (2026-11-03)

- [x] **PR #110:** merged as [`fe7dca4`](https://github.com/MitMike/crm_signals/commit/fe7dca402293faa1e7e60f147d53adaef63009d6) from final head `f4904b7bd88725017f5f2254de9ceb3c123163cc`.
- [x] All 13 final-head check runs completed: 11 succeeded and two runtime selectors were skipped as expected for documentation-only changes.
- [x] Reconciled the plan, progress, follow-ups, release sprint, production-audit snapshot, changelog and README's D3 prerequisite. D3 implementation is complete; Helpdesk target-site version/schema/field permissions and SLA calendar validation remain pilot gates.
- **Status:** documentation complete; no runtime/site configuration change; reference CI-verified; not pilot-verified.
- [ ] **Next action / revisit criteria:** no further repository feature work is justified by the current evidence. Resume target-site acceptance only when an authorized Frappe v16.5 staging window, approved full SHA, named technical/business owners and test accounts are available. Then collect exact installed app inventory, dashboard desktop/mobile screenshots after approved asset rebuild/cache refresh, effective-role permission results, D1/D2 finance reconciliation by currency, Helpdesk SLA evidence, scheduler/mail/realtime/webhook recovery and backup/restore/rollback rehearsal. If new code or documentation changes, add their specific evidence and retest criteria in a focused PR.


## PR #111 merged — release-document reconciliation (2026-11-03)

- [x] PR #111 merged as [`166ca6b`](https://github.com/MitMike/crm_signals/commit/166ca6b2cc9838ffd68c551b327ee41d2a5316b4); all 11 applicable final-head checks passed and two docs-only runtime selectors were skipped. The main commit's 17 checks later completed with 16 success and one expected selector skip.
- **Current main:** `166ca6b2cc9838ffd68c551b327ee41d2a5316b4`; no open PRs or issues were found in the live repository query.

## README pinned first-install path — PR #112 merged

- [x] **Documentation consistency fix (ADR-090):** remove the moving `bench get-app --branch main` example. The README now clones directly into `apps/crm_signals`, detaches and verifies the approved full SHA, then runs `bench setup requirements crm_signals` and site installation/migration/build/restart. Existing upgrades link to the Administrator Guide and Deployment Runbook.
- **Scope:** documentation and static-test-only; no runtime or dependency changes. The root quick-start now agrees with the detailed operator procedure, and the Python contract test protects the pin-before-requirements ordering.
- [ ] **Still open — staging rehearsal:** execute both first-install and upgrade sequences on an authorized Frappe v16.5 staging Bench; record the exact approved/deployed SHA, `bench version`, installed-app inventory, command output, migration, asset build, restart and rollback evidence.
- **Revisit criteria:** staging rehearsal can begin only when an authorized Frappe v16.5 staging window, approved full SHA, named technical owner and site/Bench operator are available. Do not infer success from repository CI.


- [x] PR #112 merged as [`d2e1d87`](https://github.com/MitMike/crm_signals/commit/d2e1d873a8f257545596379e179aeb3e4de40dd4); all 18 final-head checks passed, including Quality, Python, Security, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0.
- [ ] **Still open — staging first-install/upgrade rehearsal:** record approved/deployed SHA, `bench version`, installed-app inventory, command output, migration, asset build, restart and rollback evidence on an authorized Frappe v16.5 Bench.
 
## D3 operator-guide correction

- [x] Both D3 HTML guides now describe the implemented standard Helpdesk adapter and require separate approval before any custom/different ticket source is scoped.
- [x] Static regression coverage protects both the existing-adapter status and custom-source approval boundary.
- [x] **Final-head CI:** PR #117 merged after all 35 final-head checks passed, including Quality, Python 3.10–3.14, Security, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0.
- [ ] **Target-site D3 acceptance:** verify installed versions, exact required fields, effective Sales read permissions, active SLA calendar/holidays/timezone, pause/resume and native outcomes in authorized staging.
- **Revisit criteria:** custom adapter work only after exact DocType/field/lifecycle/relationship/identity metadata and support, security and business approval are supplied.


- [x] **CI defect corrected:** Python 3.11 and 3.12 each found one stale setup-guide promise (125 passed, 36 skipped, 1 failed). The page now describes configuring the existing adapter, separate custom-source approval and the correct footer; the static contract test protects both.
- [x] **Re-run final-head checks:** PR #117's corrected head passed the full 35-check matrix; earlier failing runs remain recorded as historical evidence.


- [x] **Second CI defect corrected:** Python 3.11, 3.12 and 3.14 each found one stale test expectation (125 passed, 36 skipped, 1 failed). The guide's new wording was correct; the test expected an obsolete phrase. The assertion now checks "custom sources require separate approval and scope".
- [x] **Final verification:** the corrected PR #117 head passed all 35 checks; PR #117 merged as 93e7e16.


## PR #117 merged — D3 operator guide (2026-11-03)

- [x] PR #117 merged as 93e7e16 (merge commit 93e7e16271d727476618b4981498ad901835bad4); all 35 final-head check runs passed.
- [x] D3 setup and discovery guides now match the implemented standard adapter; custom/different ticket sources require separate support, security and business approval.
- [ ] Target-site D3 acceptance: on authorized Frappe v16.5 staging, verify exact Helpdesk version/schema, effective Sales field permissions, active SLA calendar/holidays/timezone, pause/resume behavior and native metric outcomes.
- [ ] Release acceptance: rehearse first install/upgrade and rollback; reconcile D1/D2 against native ERPNext reports by currency; complete dashboard desktop/mobile visual UAT; test scheduler, mail, realtime, webhook and worker recovery; record backup/restore evidence.
- Revisit criteria: begin only with an authorized staging window, approved full SHA, named technical owner, site/Bench operator, support/security/business owners and representative test accounts. Do not infer pilot acceptance from CI.


## PR #118 merged — documentation reconciliation

- [x] PR #118 merged as 3cb9f017b1694727f0b1729d5e2af9a7913a7715; all 11 applicable final-head checks passed and two docs-only runtime selectors were skipped.
- [x] PR #117's D3 guide change remains code-complete and reference-stack CI-verified, not pilot-verified.
- [ ] Target-site D3 acceptance, first-install/upgrade/rollback, D1/D2 native-report reconciliation, dashboard visual UAT and operational recovery remain open.
- Revisit only when authorized Frappe v16.5 staging, approved full SHA, named technical/business owners and representative test accounts are available.


## Effective-user permission preflight — PR #120 opening snapshot (2026-11-03)

- **Decision (ADR-092):** keep the default preflight read-only and identity-safe; accept only explicit aliases mapped to dedicated active synthetic accounts. Validate the Sales User, Sales Manager, System Manager and non-sales role boundaries. Use Frappe's user-aware DocType permission and permitted-field APIs. Reject Administrator, disabled, duplicate and incorrectly assigned accounts; never return usernames or email addresses.
- **Implementation:** the report's optional `effective_user_permissions` section contains per-profile DocType read and required-field read results, plus status/error type only. No business-document rows are queried. The Administrator Guide, Deployment Runbook and Target-Site Acceptance Kit now document the optional `bench execute --kwargs` call and output limits.
- **Tests added:** permitted/denied DocType and field outcomes, disabled and Administrator rejection, no-user unavailable state, unknown profile rejection and identity non-disclosure.
- **Status at PR opening:** code-complete; CI pending; not pilot-verified. Frappe v15/v16 final-head validation is required before merge.
- **Revisit criteria:** if Python/Quality/Security/Bench/pinned v16.5 CI fails, inspect the exact final-head job and correct it before merge. If the permission API differs between v15 and v16, keep the helper version-compatible or fail closed; do not substitute static DocPerm for the user-aware check. Target-site acceptance still requires row-level controlled-record tests and the complete P0 release checklist.


## Effective-user preflight real-stack validation — PR #120

- [x] Initial unit coverage exercises mocked allow/deny, role validation, disabled/Administrator/duplicate account rejection and identity non-disclosure.
- [x] Added a disposable-site Bench smoke that creates synthetic users only when `allow_tests` is enabled and calls the production preflight on real Frappe metadata.
- [x] PR #120 final-head verification: all 18 checks passed across Quality, Security/Semgrep, Python 3.10–3.14, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0; merged as `a778c47`.
- [ ] On authorized staging, run the optional probe with approved synthetic accounts and separately verify controlled-record User Permissions, ownership, shares, list/API/report/export and dashboard behavior. CI does not satisfy this gate.


## Effective-user probe account-type boundary — PR #120

- [x] Require enabled Frappe System Users; reject Website Users even if they carry a sales role.
- [x] Add unit regression coverage and assert System User type in the real-Frappe disposable CI fixture.
- [x] Final-head Python, Quality, Security, Bench v15/v16 and pinned v16.5.0 checks all passed; PR #120 merged as `a778c47`.
- [ ] Keep controlled-record and actual Desk/API/report/export/dashboard acceptance as target-site gates.


## PR #120 merged — effective-user preflight CI verification

- [x] PR #120 merged as `a778c47b5078ac69dd89bdcd3ecab41de09b8072` from final head `e95efccec019df3fbadd1703f34c5682340b7f58` after all 18 final-head checks passed.
- [x] Real-Frappe permission probe passed in Bench v15, Bench v16 and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 workflows.
- [x] Operator guide, deployment runbook and target-site acceptance kit document the alias-only probe and its DocType/field-only boundary.
- [ ] Authorized target-site acceptance: controlled-record User Permissions, ownership, shares, list/API/report/export/dashboard behavior; exact deployed SHA and versions; D1/D2 native-report reconciliation; Helpdesk SLA; deployment/rollback; scheduler/mail/realtime/webhook/worker recovery; backup/restore; desktop/mobile visual UAT.
- **Revisit criteria:** proceed only with an authorized Frappe v16.5 staging window, approved full SHA, named technical/business/security owners and dedicated synthetic System Users. Do not infer site acceptance from disposable Bench CI.



## PR #122 session restoration review correction
- [x] Keep the original Frappe session restoration attempt in a common `finally` even when `frappe.set_user(test_user)` mutates the session and then raises.
- [x] Add regression coverage for mutate-then-raise, no record query, partial/fail-closed result and name/message non-disclosure.
- [x] Final-head CI passed after the session-restoration correction: Quality/Python, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 (runs 41603744414, 41603744435, 41603744404 and 41603744511); PR #122 merged as `de16ead`.
- [ ] On authorized Frappe v16.5 staging, validate supplied synthetic record visibility against an approved role/record matrix; separately test direct form, API, report, export, print and dashboard behavior.
- **Revisit criteria:** if restoration fails, treat the probe as partial and stop acceptance; investigate Frappe session semantics rather than directly mutating session internals. Do not infer target-site acceptance from CI.


## PR #122 merged — synthetic-record list visibility (2026-11-03)

PR [#122](https://github.com/MitMike/crm_signals/pull/122) merged as [de16ead](https://github.com/MitMike/crm_signals/commit/de16ead6ed2f155e83189196755048a264c2ec74) from final head [5339d71](https://github.com/MitMike/crm_signals/commit/5339d7135ff87902974dc2d038051e101434389e).

All four final-head workflows completed successfully: Quality Checks (run 41603744414), Security Scanning/Semgrep (41603744435), Bench Integration and E2E (41603744404), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation (41603744511). The Quality run passed the configured Python 3.10, 3.11, 3.12 and 3.14 test jobs plus lint/static checks. Bench v15/v16 integration passed, including the v16 Playwright job. The pinned lane passed the real-Frappe synthetic-record visibility probe, D1/D2 aggregate/permission checks, Helpdesk schema and D3 aggregate checks, schema upgrade, asset build, Python tests and Frappe integration tests.

The first Python run had five failures from a stale helper signature; it was corrected and the final-head matrix passed. A separate review correction ensured a frappe.set_user call that mutates session state and then raises still flows through the restoration finally; the final-head regression verifies restoration is attempted, no list query runs and record names/exception messages are not disclosed. No failing head was merged.

The optional preflight is code-complete and reference-stack CI-verified, not pilot-verified. It checks bounded permission-filtered list visibility for exact supplied synthetic records and returns labels/booleans only. Direct form, REST API, report, export, print and dashboard access remain separate acceptance paths. Authorized Frappe v16.5 staging, approved release SHA, named owners and controlled synthetic records are still required for pilot acceptance, alongside D1/D2 native-report reconciliation, Helpdesk SLA, deployment/rollback, operational recovery, backup/restore and desktop/mobile UAT.


## PR #124 opening snapshot — real Sales User record-filter preflight regression (2026-11-03)

- **Reviewed main:** `c9df68e3728fe675e4eb3b4d5dafaf8b4d29fcc6` (PR #122 and PR #123 merged; no open PRs or issues at branch creation).
- **Finding:** PR #122's real-Frappe preflight smoke proves a System Manager can list a synthetic CRM Signal, but does not invoke the new `test_records` path for a restricted Sales User. The existing Bench permission test already creates a Sales User, a linked Lead excluded by a User Permission, and an unlinked signal owned by that user.
- **Decision (ADR-095):** reuse that controlled fixture to call `get_site_preflight_report(test_users=..., test_records=...)` and assert the probe reports the linked/restricted signal as false and the unlinked/owned signal as true. Assert the result is checked, the original session user is restored, and neither record name nor user identity is returned.
- **Scope:** integration-test-only; no runtime behavior, schema, dependency or site configuration change. The existing Bench v15/v16 + Playwright and pinned Frappe 16.5.0 workflows execute the integration test suite.
- **Status at opening:** code-complete; final-head Quality, Python, Security/Semgrep, Bench v15/v16 and pinned Frappe 16.5.0 checks pending. Not pilot-verified.
- **Revisit criteria:** if Frappe v15/v16 returns a different list result, inspect the real `crm_signal_query` and User Permission behavior; do not weaken the expected false/true boundary or replace permission-filtered `get_list` with `get_all`. Authorized target-site direct form/API/report/export/print/dashboard tests remain separate.


## PR #124 merged — real Sales User record-filter preflight regression (2026-11-03)

PR #124 merged as [af94b14](https://github.com/MitMike/crm_signals/commit/af94b14038250b75ebc849e424779432d57dee98) from final head [0c7a6bf](https://github.com/MitMike/crm_signals/commit/0c7a6bfc77c3ee9df7189007c0326491906aca76). All four final-head workflows passed: Quality Checks (run 41614477641, configured Python 3.10/3.11/3.12/3.14 jobs and lint/static checks), Security Scanning/Semgrep (41614477907), Bench Integration and E2E (41614477805; Frappe v15 and v16 integration passed, with v16 Playwright passed), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation (41614477749). The real-Frappe Sales User fixture confirmed a linked CRM Signal excluded by the Lead User Permission is not visible while an unlinked signal owned by the same user remains visible. The report returned checked status, restored the original session user and disclosed neither user nor record names.

This is integration-test and documentation evidence only; no runtime behavior, schema, dependency, metric or site configuration changed. The preflight's list-visibility result is code-complete and reference-stack CI-verified, not pilot-verified. On authorized Frappe v16.5 staging, repeat the approved synthetic role/record matrix and separately test direct form, REST API, report, export, print and dashboard paths. D1/D2 native-report reconciliation by currency, D3 Helpdesk SLA, first-install/upgrade, backup/restore/rollback, scheduler/mail/realtime/webhook/worker recovery and desktop/mobile UAT remain release gates.


## PR #125 merged — operator record-visibility acceptance (2026-11-03)

PR #125 merged as [7029747](https://github.com/MitMike/crm_signals/commit/70297474aadb2f4628da2268e10771cd74683e5c). Quality Checks, Security Scanning and the Bench Integration/E2E workflow completed successfully; the Bench runtime selectors were skipped as expected for a documentation-only change. The implementation plan, progress, follow-ups, ADR-095 and changelog now record PR #124's final-head verification. The Administrator Guide, Target-Site Acceptance Kit and Deployment Runbook now include the exact Sales User linked-restricted/unlinked-owned CRM Signal fixture and expected list-visibility result. No runtime behavior or site configuration changed.


## PR #126 opening snapshot — direct document/list API permission regression (2026-11-03)

- **Reviewed main:** `70297474aadb2f4628da2268e10771cd74683e5c` (PR #124 and PR #125 merged; no open PRs or issues at branch creation).
- **Finding:** The existing Sales User fixture and PR #124 cover permission-filtered list visibility through `frappe.get_list` and the preflight. The acceptance guide separately requires direct API reads, but no real-Frappe test invokes the standard single-document/list API wrappers for the same linked-restricted/unlinked-owned pair.
- **Decision (ADR-096):** invoke `frappe.client.get` and `frappe.client.get_list` while switched to the synthetic Sales User. Require denial for the linked CRM Signal, success for the unlinked owned signal, and list output containing only the unlinked signal. Restore the original session user in `finally`.
- **Scope:** integration-test and operator-guide coverage only; no runtime, schema, dependency or site configuration change. Direct HTTP authentication/routing and browser form behavior remain staging checks.
- **Status at opening:** code-complete; final-head Quality/Python, Security, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 validation pending. Not pilot-verified.


### PR #126 first CI triage — Ruff import ordering

- **Observed:** Quality Checks lint failed on head `a5998ec` with Ruff `I001` for the local `frappe.client` import in the integration test helper. The Python 3.11/3.12/3.14 unit jobs passed; Python 3.10 and the Frappe integration/pinned workflows were still running at triage.
- **Decision:** keep the test import-safe when Frappe is not installed by moving the two API wrapper imports into the module's existing guarded `try` block beside `import frappe` and `FrappeTestCase`. Do not suppress or relax Ruff's import-order rule.
- **Correction:** import `frappe.client.get` and `get_list` in the guarded Frappe block; remove the local import from the helper. A fresh final-head matrix is required.
- **Revisit criteria:** if Ruff still reports `I001`, use its exact `--fix` ordering while retaining the `ModuleNotFoundError` fallback; if Bench reports an API wrapper mismatch, inspect the pinned v15/v16 implementation and keep the denied/allowed assertions intact.


### PR #126 second CI triage — guarded import still fails Ruff I001

- **Observed:** Quality Checks on head `97ac553` failed the same Ruff `I001` at the guarded import block (`crm_signals/tests/test_notification_permissions.py:7`); the first attempted correction moved aliased `frappe.client` imports into the existing `try` block but did not satisfy Ruff's ordering rule.
- **Decision:** import the `frappe.client` module itself (`import frappe.client`) inside the existing guarded block and call `frappe.client.get` / `frappe.client.get_list`. This preserves the no-Frappe unit-test fallback and removes the aliased member import ordering ambiguity.
- **Correction:** replace the aliased imports and rerun the full final-head matrix. Do not suppress I001 or relax lint.
- **Revisit criteria:** if I001 persists, retrieve Ruff's exact `--fix` diff from the job or run the pinned Ruff 0.8.1 formatter against the file before another commit; if the integration test fails after lint passes, inspect the exact v15/v16 API result and keep the denied/allowed assertions intact.


### PR #126 review correction — restore session when the initial user switch raises

- **Finding:** final-head CI passed, but review found the API helper called `frappe.set_user(test_user)` immediately before its `try`. If that call changed session state and then raised, the `finally` restoration would not run.
- **Decision:** move the initial user switch inside the existing `try`, so every attempted switch is covered by restoration. Keep the original user captured before the switch and retain the denied/allowed API assertions.
- **Status:** the prior head `30a3890a994a3402b4efdf15732843f86a62b789` passed all four workflows (Quality/Python, Semgrep, Bench v15/v16 + Playwright, pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0). This correction creates a new head and requires a fresh complete matrix before merge.
- **Revisit criteria:** if the new matrix fails, inspect the exact v15/v16 API wrapper and session behavior. Do not move the switch back outside the `try`, bypass permissions, or weaken the linked-denied/unlinked-allowed assertions.


### PR #126 verification follow-up — completed 2026-11-03

PR #126 merged as `812aa1eb76fbabc0e7f73a664caa72a1e208feb6` from final head `24d12acb50613c25f71fc2d809b464e311ba7f3e`. All four final-head workflows passed: Quality/Python run `41634012616`, Security/Semgrep `41634012907`, Bench v15/v16 + v16 Playwright `41634012673`, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 `41634012853`.

- [x] Preserve the linked-restricted denied / unlinked-owned allowed assertions through `frappe.client.get` and list visibility through `frappe.client.get_list`.
- [x] Keep the initial `frappe.set_user` call inside `try/finally` and assert original session restoration.
- [x] Require all four corrected final-head workflows before merge; no failing head was merged.
- [ ] On authorized Frappe v16.5 staging, verify API-key/token authentication, HTTP status/response behavior, browser form loading and the approved role/record matrix. Continue report/export/print/dashboard checks and remaining P0 acceptance.
- **Revisit criteria:** if HTTP or browser tests differ from the Python method-wrapper outcomes, capture sanitized status/body and Frappe version, then inspect authentication, routing, document permission and form-loading paths without using Administrator credentials or weakening the record boundary.


## PR #128 merged — authenticated Sales User HTTP acceptance procedure (2026-11-03)

PR #128 merged as `85c492ea2c84444d7cc45c0d61706736fa972a83`. Quality/Python run `41639851748`, Security/Semgrep `41639851870` and Bench path-selector run `41639851663` all passed; runtime selectors were skipped as expected for documentation-only changes. The embedded Bash passed `bash -n`; ShellCheck was unavailable.

- [x] Add exact GET query parameters and expected outcomes for `frappe.client.get` and `frappe.client.get_list` using the linked-restricted/unlinked-owned synthetic CRM Signal pair.
- [x] Verify the API token identity against the explicitly expected dedicated Sales User; reject Administrator.
- [x] Keep the token header in a mode-0600 temporary curl config, require HTTPS, do not follow redirects, and remove private response files on exit.
- [ ] Execute on authorized Frappe v16.5 staging and record sanitized HTTP status/pass-fail evidence with the approved full SHA and installed versions.
- **Revisit criteria:** if status/response shape differs on the pinned site, capture sanitized status/error class and Frappe build, inspect the versioned method wrapper/auth mapping, and update the guide. Never use Administrator or accept a result that exposes the linked restricted record.


## PR #130 — browser-session Sales User permission E2E (2026-11-03)

- [x] Seed deterministic allowed/restricted Lead and linked-restricted/unlinked-owned CRM Signal fixtures for the dedicated E2E Sales User.
- [x] Assert the fixture itself exposes only the unlinked owned CRM Signal through permission-filtered `frappe.get_list` before browser tests.
- [x] Add Playwright same-origin session HTTP assertions for linked `frappe.client.get` 403, unlinked `get` 200 and list-only-unlinked.
- [x] Extend the pinned Frappe 16.5.0 workflow to run the Playwright suite; retain Bench v15/v16 and v16 Playwright coverage.
- [x] Refactor the fixture helper after the initial 102-line hard-limit failure and apply Prettier's exact formatting after the subsequent Quality run flagged the E2E spec.
- [x] Use lockfile-enforced `npm ci --ignore-scripts --no-audit --no-fund` for pinned-lane Playwright dependencies, consistent with Stage 0 and Quality Checks; keep browser installation explicit and protect it with a static contract test.
- [x] Mask both generated pinned-lane E2E passwords before writing them to GitHub Actions step outputs; protect masking order with the same static contract test.
- [ ] Require fresh final-head Quality/Security/Bench v15/v16 and pinned Frappe 16.5.0 Playwright workflows to pass after the npm-ci and credential-masking corrections; earlier heads do not count.
- [ ] On authorized target-site staging, separately execute the API-token smoke and test browser form route, REST resource, reports, exports, print and dashboard.
- **Revisit criteria:** if permission outcomes differ, inspect User Permission setup and CRM Signal query hooks on the exact Frappe build. If pinned E2E times out, profile the slow setup/install/browser steps before changing the timeout. Never use Administrator for Sales User assertions.


## PR #130 — pinned Frappe 16.5 Playwright login-route mismatch (2026-11-03)

- [x] Inspect the failed pinned workflow job and downloadable Playwright trace rather than retrying an unchanged run.
- [x] Confirm the focused test reached the shared login helper; the actual Frappe v16.5.0 form submitted POST /login with HTTP 200, while the helper listened only for POST /api/method/login.
- [x] Update the helper to accept the exact /login and /api/method/login POST paths while retaining response, session-cookie and redirect assertions.
- [x] Add a static regression guard for both exact paths and POST method.
- [ ] Require all four final-head workflows to pass on the corrected head; do not reuse the previous Bench or pinned results.
- [ ] After CI passes, merge PR #130 only if the branch is current and all required checks are green; then reconcile main progress records.
- **Evidence:** pinned workflow run 41643473834, job 125943109815; Playwright artifact 13233758446. The pinned job's setup, migration, permission fixtures, Python tests and Frappe integration tests passed before the login response waiter timed out.
- **Revisit criteria:** if the corrected run fails, inspect its Playwright trace for the exact POST pathname/status and determine whether the login itself failed or only the waiter predicate. Do not skip login or weaken the 403/200/list-only-unlinked assertions. Target-site API-token, browser form, report/export/print/dashboard and pilot acceptance remain separate.



### PR #130 — browser-session HTTP permission regression (closed 2026-11-03)

- [x] Correct the Frappe v16.5 login waiter to accept the observed successful `POST /login` route while retaining the `POST /api/method/login` route, session-cookie and Desk-navigation checks.
- [x] Replace version-sensitive browser role discovery with server-side `frappe.get_roles` fixture validation and exact `frappe.auth.get_logged_user` browser identity checks.
- [x] Replace the built-in Employee-role assumption with the deterministic CI-only `CRM Signals E2E Non-Sales` Desk role; retain Sales User and non-sales role-boundary assertions.
- [x] Pass all four final-head workflows on `42f8a38e751977e21168869c4010fcce901309ac`: Quality `41668745943`, Security `41668745937`, Bench v15/v16 + Playwright `41668746054`, and pinned Frappe 16.5.0 `41668745681`.
- [x] Merge PR #130 as `2b697b4d37a12b2e339bcf680ff808f23b97850f`; reconcile the implementation plan, progress, decisions and changelog.
- [ ] On authorized Frappe v16.5 staging, execute the API-token smoke with the dedicated Sales User; separately test the direct form route, REST resource, reports, exports, print and dashboard.
- **Evidence:** pinned run `41668745681` completed the `Run Playwright E2E` step successfully after all site setup, permission preflight, D1/D2, Helpdesk, schema upgrade, Python and Frappe integration tests; Bench run `41668746054` passed v15/v16 integration and v16 Playwright.
- **Revisit criteria:** if the live API-token or browser-form outcome differs from CI, capture sanitized status/error class, exact Frappe build and approved full SHA; inspect authentication, route, document permission and field-level behavior without using Administrator credentials or weakening the linked-denied/unlinked-allowed boundary.

### PR #131 — direct CRM Signal form-load permission regression

- [x] Confirm from the supported Frappe v16 form loader that the direct Desk form calls `frappe.desk.form.load.getdoc` with GET and that the loader invokes `doc.check_permission("read")` before returning the document.
- [x] Add the `Sales User CRM Signal form permission boundary` browser test that opens `/app/crm-signal/<name>` as the synthetic Sales User, expects 403 and no restricted message for the linked signal, and expects 200 plus the expected message for the unlinked owned signal.
- [x] Include the new test in the pinned Frappe 16.5.0 Playwright selector and add a static regression guard.
- [x] Replace `npm install` with lockfile-enforced `npm ci` in the supported v15/v16 Bench E2E workflow; extend static checks to require `npm ci` and pre-output password masking in both supported and pinned lanes.
- [x] Diagnose the first Python 3.11 static failure: the new guard expected the bare method name, but the spec matches the full `/api/method/frappe.desk.form.load.getdoc` pathname; correct the guard only.
- [ ] Pass final-head Quality/Python, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 workflows after the static-guard correction.
- [ ] Merge only after all required checks pass on the exact current head; then reconcile the main baseline and close this follow-up.
- [ ] Execute the direct form check on authorized Frappe v16.5 staging and retain sanitized evidence with the deployed full SHA and exact app versions.
- **Evidence:** Quality run `41675705153`, Python 3.11 job `126055881118`; 143 passed, 36 skipped, one static assertion failed before runtime/browser tests. The assertion mismatch is corrected on the branch; require a fresh full final-head matrix.
- **Revisit criteria:** if the form route does not trigger the expected GET loader or the permission status differs, inspect the Playwright trace and versioned Frappe router/loader. Do not accept a successful Desk shell response as document access and do not weaken the restricted/allowed record boundary.
