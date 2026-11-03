# CRM Signals — Deferred follow-ups and production acceptance

This file records known work that is intentionally not represented as complete. Revisit an item when its trigger or dependency is satisfied.

**Ownership convention:** P0 target-site items belong to the site administrator/implementation lead with the relevant security or finance owner; P1 engineering items belong to CRM Signals maintainers; site-specific configuration items belong to the Sales Manager/business owner; P2 roadmap items belong to the product owner. Close an item only with the evidence described below.

## P0 — required before production sign-off

- [ ] **Target-site preflight and acceptance.** Use the updated evidence template in [Target-Site Acceptance Kit](TARGET_SITE_ACCEPTANCE.md), including the staging-only Redis Socket.IO outage, worker restart, scheduler recovery and permission-revocation checks. Record the exact Frappe v16.5 patch/build, ERPNext and Helpdesk app versions, installed apps, Company currencies, timezone, workflows, custom fields and role matrix. Run Pilot import, migrate, scheduler, email, realtime, dashboard and rollback smoke tests.

  **Current blocker / revisit criteria (reviewed 2026-11-03):** Repository access is available, but no target-site session or sanitized discovery record is connected to this work. The read-only preflight now reports the exact CRM Signals Git SHA at `framework.crm_signals_source.commit_sha` only when the checkout is clean (ADR-086); require an exact match to the approved release SHA and stop if the checkout is dirty, unavailable or mismatched. Revisit when an authorized operator supplies the preflight output, exact `bench version` and installed-app inventory, Company base currencies, timezone, workflows, role/field permissions and active Helpdesk SLA calendar, and an approved staging site with synthetic test users/data is available. Finance/business/security owners must approve Company thresholds, SLA interpretation, webhook controls and retention policy. Until then, do not infer live-site values or pilot results from reference-stack CI.
- [ ] **Permission parity.** Verify Sales User, Sales Manager, System Manager and non-sales users across list, direct form, API, report, export and print. Notifications are not an authorization grant. Realtime recipients must be able to read the CRM Signal, linked Lead/Customer and originating source DocType; PR #44 adds the source-document check. The scheduled digest queries Leads and Quotations separately under each recipient's user context; confirm both paths with the target site's actual permissions.
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



## Real-Git nested-parent regression — PR #107 pending (2026-11-03)

- [ ] **PR #107:** [test: exercise real parent-repository discovery in preflight](https://github.com/MitMike/crm_signals/pull/107). The new test creates a committed temporary parent repository and nested Bench-style app path, then verifies the real preflight rejects the enclosing Git root.
- **Decision:** ADR-088 supplements mocked root-mismatch coverage with a real Git integration test because the failure mode depends on Git's upward repository discovery.
- **Revisit criteria:** If any final-head Python/Quality/Security/Bench/pinned lane fails, inspect its job log and correct the test/environment issue before merge. If Git is unavailable in a supported CI environment, make that prerequisite explicit rather than silently skipping the regression. This test is not pilot verification.


## Real-Git nested-parent regression — PR #107 merged (2026-11-03)

- [x] **PR #107:** merged as [`a472f19`](https://github.com/MitMike/crm_signals/commit/a472f1981f758ce7b6233d95fc0682fe69d7a304) from final head `a47c3975eebe52dccb918a1056cf30d818cdcae4`. All 19 final-head check runs passed across Quality/Python 3.10–3.14, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0.
- **Decision:** ADR-088 adds a real temporary parent Git repository and nested Bench-style package test to prove Git's upward discovery is rejected by the production preflight helper. This complements deterministic mocked failure-path tests.
- **Status:** code-complete and reference-stack CI-verified; no runtime change; not pilot-verified.
- [ ] **Release blocker:** target-site acceptance remains blocked until an authorized Frappe v16.5 staging session, approved full SHA, named technical/business owners and test accounts are available. Then collect dashboard screenshots, effective-role permission results, D1/D2 reconciliation, Helpdesk SLA evidence, scheduler/mail/realtime/webhook recovery and backup/restore/rollback results. Do not treat green CI as site acceptance.
