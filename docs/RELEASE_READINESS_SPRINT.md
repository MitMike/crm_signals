# CRM Signals — Release-readiness completion sprint

**Started:** 2026-11-01  
**Latest main:** [d0cb54f](https://github.com/MitMike/crm_signals/commit/d0cb54fe4d5f7f2cb3bbf9cbcc14fee9a8662d98); latest application feature baseline: [c5720bf](https://github.com/MitMike/crm_signals/commit/c5720bfb3fbe8b554ec6febd549a8d5e58acc1d7); latest permission-test baseline: [70aa4d8](https://github.com/MitMike/crm_signals/commit/70aa4d8953cc8a69d1317aad1c72654f05a1b29e); latest application-code/digest privacy fix: [a63866f](https://github.com/MitMike/crm_signals/commit/a63866f99fd9f67c5c680e57987abf47c1247377); latest UI fix: [b1f4ad7](https://github.com/MitMike/crm_signals/commit/b1f4ad71f368c346ce16126501982cfe2233c2b9) (PR #84 dashboard inset; CI-verified, visual UAT outstanding). PR #165 merged from exact head 3162597; its four required final-head workflows passed. Post-merge main Quality [41920151879](https://github.com/MitMike/crm_signals/actions/runs/41920151879), Security [41920151933](https://github.com/MitMike/crm_signals/actions/runs/41920151933) and Bench [41920152015](https://github.com/MitMike/crm_signals/actions/runs/41920152015) were still running at this review.
**Decision register:** [ADR-046](DECISIONS.md#adr-046--run-release-readiness-as-an-evidence-gated-sprint)  
**Operating rule:** no item is complete without the evidence listed here. CI evidence and target-site evidence are separate.

- [x] [PR #76](https://github.com/MitMike/crm_signals/pull/76) change-aware CI merged as `cec49e7`; final head `d6a6300` passed all 19 check runs, including Quality, Security/Semgrep, Python 3.10/3.11/3.12/3.14, Bench v15/v16 + Playwright and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. Required contexts and fail-closed path gates are preserved.

- [x] [PR #79](https://github.com/MitMike/crm_signals/pull/79) adds bug/fix evidence registers and records BUG-2026-001 / FIX-2026-001; Quality, Security and Bench v15/v16 passed. Merged as 7904a70. The dashboard fix and UAT closure remain separate.
- [x] PR #84 dashboard inset fix merged as `b1f4ad7`; final head `f0e1909` passed Quality, Security, Bench v15/v16 and pinned v16.5.0. Desktop/mobile UAT after asset/cache refresh remains open.
- [x] PR #85 GME workspace label merged as `5cc4308`; final head `b09a0cb` passed Quality, Security, Bench v15/v16 and pinned v16.5.0. Technical identifiers/routes are unchanged.
- [x] PR #88 upload-artifact v7 merged as `de8e78b`; final head `eed57d6` passed Quality, Security, Bench v15/v16 + Playwright and pinned v16.5.0.
- [x] PR #89 documentation/ADR-075 skip-path reconciliation merged as `ac6b253`; final head `0967290` passed Quality, Security and Bench Integration/E2E.
- [x] PR #7 setup-uv v7 merged as `331492c`; final head `a72c82c` passed all 18 check runs, including the supported Frappe v15/v16 Bench + Playwright and pinned v16.5.0 lane.
- [x] PR #8 setup-node v7, PR #94 setup-python v7 and PR #96 flit-core `>=3.4,<5` are merged after refreshed final-head checks. PR #96's ADR-081 wheel/sdist build and isolated-install coverage passed on Python 3.10 and 3.14. The former open-maintenance-PR statement in this historical sprint snapshot is superseded by the current repository snapshot below.
- [ ] PRs #75/#78 and #80/#81 are closed unmerged; #75/#78 are superseded by #85/#84. The optional regression-review template was not merged and is not a release gate.

- [x] **P0 — Pin before install (ADR-077; PR #82 merged as `ac030b1`, CI-verified):** direct clone with `--origin upstream`, detach/verify the approved full SHA, then run `bench setup requirements crm_signals` before site install/migration/build. Final head `ef4dc09` passed Quality, Security, Frappe v15/v16 Bench + Playwright and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. Authorized staging rehearsal remains open.

## Sprint sequence

### 0. Active PR triage — current review queue

- [x] Merge [PR #32](https://github.com/MitMike/crm_signals/pull/32) for D3 standard Frappe Helpdesk metrics. Final head `93b536abef331d8b34b5b7b570fbb280a996bfb2` passed Python 3.10/3.11/3.12/3.14, lint/static, Semgrep and Bench v15/v16; merge commit `43fddfbbc46cac277a48c840251a7a2c963a8eb5`.
- [x] [PR #38](https://github.com/MitMike/crm_signals/pull/38) audited Failed-row replay merged as `1640bdd496706a7f297b0984f1fd1d9695307147`; Quality, Security and Bench v15/v16 passed. The action is POST-only, requires System Manager plus outbox read access, preserves attempt history and audit Comment, and confirms before replay.
- [x] [PR #50](https://github.com/MitMike/crm_signals/pull/50) exact Frappe v16.5.0/ERPNext v16.5.0/Helpdesk v1.28.0 Bench lane merged as `24a9b8d3d178682a68df418f5cd29582644056c8`; exact target job and required v15/v16 matrix passed.
- [x] [PR #45](https://github.com/MitMike/crm_signals/pull/45) per-company quotation thresholds merged as `ff434bdf407d1d61842d81fae16e04b4b9b483d5`; all 16 required checks passed, including Bench v15/v16. The child-table controller and currency-mismatch regression coverage are included.
- [x] [PR #49](https://github.com/MitMike/crm_signals/pull/49) fixes the child-row Currency field's Company-base-currency fetch/display binding; all required checks passed and the change is merged as `2e9eb89b8ed5618ca3e50e6bc0b2c867c516e17b`.
- [x] [PR #44](https://github.com/MitMike/crm_signals/pull/44) source-document notification permission check merged as `48622c08700032566051978076f49bc807c381e7` after Quality, Security and Bench v15/v16 passed.
- [x] [PR #36](https://github.com/MitMike/crm_signals/pull/36) merged as `e57d94ea`; ADR-049 sets Frappe v16.5 as the primary target while retaining v15/v16 CI coverage.
- [x] [PR #42](https://github.com/MitMike/crm_signals/pull/42) merged D3 field-level permission hardening as `17eca3f6cb493fb8729632e0902c07ccb776b6a5`; Quality, Security and Bench v15/v16 passed.
- [x] [PR #57](https://github.com/MitMike/crm_signals/pull/57), [PR #59](https://github.com/MitMike/crm_signals/pull/59) and [PR #61](https://github.com/MitMike/crm_signals/pull/61) merged Explorer core adapters, Desk entry points, five-context Playwright coverage and operator runbook safeguards. PR #61 final head `902b38e4dd4713461acfb12dc837f5b2b84da7d8` passed all required v15/v16 checks and the pinned Frappe v16.5.0 lane; merge commit `6ef9642b63c24053fb437f67d9d4fb47e360c80a`.
- [x] [PR #68](https://github.com/MitMike/crm_signals/pull/68) reconciles D1/D2 fixture status across the plan, progress and operator records; final-head checks passed and it merged as 2cc7725.
- [x] PR #70 read-only target-site preflight report (ADR-068) merged as 13341b7 after all final-head required checks and the pinned v16.5.0 lane passed. Target-site execution and effective user acceptance remain open; static DocPerm rows are not effective permission proof.
- [x] [PR #69](https://github.com/MitMike/crm_signals/pull/69) adds a real ERPNext POS Profile/Mode of Payment and submitted POS invoice settlement to the disposable D2 fixture (ADR-070); synchronized final head `33b750a` passed all 15 required/target checks and merged as `efe7872`. Target-site native-report reconciliation remains open.
- [x] [PR #71](https://github.com/MitMike/crm_signals/pull/71) adds permission-gated High-Value Quote source Quotation drill-down (ADR-069/071/072). Exact Prettier 3.9.10 output was applied after the CI diff diagnostic; final head `df0c273` passed Quality, Security, Python 3.10/3.11/3.12/3.14, Bench v15/v16 including Playwright, and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. Merged as `c5720bf`. Target-site persona and permission-revocation acceptance remains open.
- [x] [PR #73](https://github.com/MitMike/crm_signals/pull/73) reconciles the merged H-AC11 status and ADR-073 across the project records; final head `446e2bc` passed Quality, Security, Python 3.10/3.11/3.12/3.14 and Bench v15/v16. Merged documentation-only as `51798f2`.
- [x] [PR #5](https://github.com/MitMike/crm_signals/pull/5) upgrades `actions/checkout` from v4 to v7. The refreshed final head `8856f35` passed all 17 checks, including Quality, Security, Python, dependency audits, Bench v15/v16 and pinned Frappe v16.5.0 / Helpdesk 1.28.0; merged as `00e997c`.
- [x] [PR #74](https://github.com/MitMike/crm_signals/pull/74) pins target-site installation/upgrade to an approved full commit SHA, verifies the detached checkout, synchronizes dependencies from that tree, and updates the acceptance kit. Final-head Quality, Security, Bench v15/v16 and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 checks passed; merged as 1b57003. This does not constitute a target-site deployment or pilot acceptance.
- [x] [PR #65](https://github.com/MitMike/crm_signals/pull/65) fixes D2 source-permission independence: Payment Entry receipts remain visible when Sales Invoice access is denied, and partial invoice results are cleared after a query-level PermissionError. Final head `315a49a52f70ecb888e6d9cc91a4c1f4e51535d7` passed Quality, Security/Semgrep, Python 3.10/3.11/3.12/3.14, Bench v15/v16 and pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0; merged as `0cfeda4fb39f79722fdf733abd06a3460ebcdd4d`.

**Merge gate:** all required checks pass on the final PR head; review threads resolved; no target-site claims inferred from CI.

### 1. Target-site acceptance kit — source-independent preparation

- [x] Prepare the site inventory, permission, finance reconciliation, webhook, scheduler/mail/realtime and backup/restore/rollback templates in `docs/TARGET_SITE_ACCEPTANCE.md`.
- [x] Update the operator guides for the confirmed Frappe v16.5 target, exact patch/app-version capture, Company-specific threshold configuration and D3 Helpdesk field-level permission tests.
- [ ] Review the guide with the pilot operator and adjust only where the actual site differs.

**Gate:** documentation is prepared; no target-site item is closed until performed on the intended site.

### 2. Target-site acceptance — requires intended environment and business owners

- [ ] Run Frappe Pilot import and record installed versions/apps.
- [ ] Confirm Company currency and quotation-threshold policy, including multi-company behavior.
- [ ] Confirm Opportunity statuses, terminal Lead statuses, stale-Lead semantics, timezone, digest time and recipients.
- [ ] Execute permission parity tests for all relevant roles and access paths.
- [ ] Reconcile invoices, Payment Entry receipts, POS receipts and receivables against native reports, grouped by currency.
- [ ] Validate webhook credentials, rate limits, monitoring and rotation.
- [ ] Validate scheduler, mail queue, realtime routing and per-recipient permissions.
- [ ] Execute backup, restore, migration and rollback rehearsal; record exact revisions and outputs.

**Gate:** all P0 evidence recorded and reviewed; exceptions have owner, mitigation and due date.

### 3. D3 Service Resolution/SLA

- [x] Implement and merge the standard Frappe Helpdesk adapter in PR #32; CI passed on Frappe v15/v16.
- [x] Use aggregate-only metrics, native resolution/SLA fields and independent ticket/SLA DocType permission checks.
- [ ] Verify exact Frappe v16.5, ERPNext and Helpdesk versions on the pilot site.
- [ ] Verify Sales User/Manager field-level access for `status_category`, `resolution_date`, `resolution_time`, `sla` and `agreement_status`; field-level fail-closed correction merged in PR #42; pilot-site permission evidence remains.
- [ ] Confirm active SLA working days/hours, holiday list and timezone against the Monday–Saturday assumption.
- [ ] Run staging fixtures for Open, Paused, Resolved, no-SLA, Fulfilled, Failed and due states; verify privacy-safe aggregate payloads.

**Gate:** D3 CI is not pilot acceptance. Site version, permissions and SLA calendar must be evidenced.

### 4. H Highlights

- [x] Implement high-value Quotation event generation and stable source identity.
- [ ] Confirm each enabled Company has an explicitly approved non-negative threshold in its base currency; use the legacy fallback only when the currency matches exactly.
- [ ] Add the admin-managed VIP allowlist and validate escalation recipient permissions/cooldown behavior.

- [ ] Keep proposal-link tracking disabled until privacy/consent, retention and first-party link behavior are approved.
- [ ] If tracking is approved, implement opaque expiring/revocable tokens, stable event IDs, scanner classification and non-invasive diagnostics.
- [ ] Add Bench v15/v16 and Playwright coverage.

### 5. E, V and A roadmap

- [x] E Explorer core API, Desk UI and five-context route/stale-response Playwright coverage are merged and CI-verified; pilot role/field acceptance and optional-source inventory remain.
- [ ] V Vault remains blocked until D1/D2 metrics are reconciled and source visibility, retention/deletion and audited pruning are approved.
- [ ] A Analysis remains blocked until Sales/Finance sign off D1/D2 target-site reconciliation, currency/date/filter semantics and source permissions; use a versioned server-owned registry and deterministic intents only.

## Current blockers and known evidence

- PR #63 is merged and CI-verified: it executes the real D1/D2 query path on Frappe v15/v16 and pinned v16.5.0 without creating business records, and restricts Bench push runs to `main` to avoid duplicate PR-branch matrices. It is not a financial reconciliation or target-site permission test.
- PR #65 is merged and CI-verified: Payment Entry receipt access is independent from Sales Invoice access, including query-level invoice permission exceptions. It does not replace target-site role validation or financial reconciliation.
- PR #67 merged as `84ab2ce0b4ce1a9614882635e4c085092cf2a0c5` after final head `cfd7c5ec64786e394374d31ba7b89354565a2070` passed all required Quality, Security, Python, Frappe v15/v16 Bench and pinned v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 checks. Its fixture is CI-verified: its disposable D1/D2 fixture checks submitted Sales Invoices/Payment Entry, INR/USD currency bases, overdue/POS/receipt deltas and a real Payment Entry-only reader. Synthetic records/permissions are rolled back. PR #69 additionally exercises ERPNext POS payment allocation and settlement through the normal Sales Invoice lifecycle; browser checkout/POS Opening-Closing and target-site native-report reconciliation remain outside CI.

- The current main baseline is `de8e78b`; PR #82 pin-before-install, PR #84 dashboard inset, PR #85 GME workspace label and PR #88 upload-artifact v7 are merged and CI-verified. D1/D2, D3, Explorer and H-AC11 remain CI-verified; target-site acceptance and dashboard visual UAT remain open.
- PR #38 replay is merged after both Frappe v15/v16 Bench jobs passed.
- PR #45 threshold feature is merged; only target-site Company-by-Company amount and fallback approval remains.
- PR #36 ADR-049 is merged; its final required checks passed.
- D3 field-level guard PR #42 is merged; target-site Sales role and SLA-calendar acceptance remain open.
- No target Frappe site is connected to this work. Pilot evidence for versions, Company policy, role/field permissions, finance reconciliation, SLA calendar and operations remains outstanding.

## Evidence log

| Date | Work | Evidence | Status |
|---|---|---|---|
| 2026-11-02 | PR #89 docs/ADR-075 skip-path | Final head `0967290` passed Quality, Security and Bench Integration/E2E; merged as `ac6b253` | Complete — CI verified |
| 2026-11-02 | PR #7 setup-uv v7 | Final head `a72c82c` passed all 18 check runs, including v15/v16 Bench + Playwright and pinned v16.5.0; merged as `331492c` | Complete — CI verified |
| 2026-11-02 | PR #32 D3 merge | Final head `93b536ab` passed all 16 check runs; merge commit `43fddfb` | Complete — CI verified |
| 2026-11-02 | PR #38 replay review | Replaced unsupported `frappe.has_role` / `get_comments` assumptions, strengthened authorization and verified replay on Bench v15/v16; merged as `1640bdd4` | Complete — CI verified |
| 2026-11-02 | PR #45 threshold merge | Company-specific amounts/currencies, exact-currency fallback and mismatch suppression merged; all required checks passed | Complete — CI verified |
| 2026-11-02 | ADR-049 target baseline | Frappe v16.5 confirmed; v15/v16 matrix retained | Complete — merged |
| 2026-11-02 | D3 field-level permissions | Fail-closed field permission guard merged in PR #42 and passed v15/v16 CI | Complete — CI verified |
| 2026-11-02 | Explorer API/Desk/browser slice | PR #57/#59/#61; five context routes, late-response suppression and operator runbook safeguards; final head `902b38e4dd4713461acfb12dc837f5b2b84da7d8` passed all required checks and pinned Frappe v16.5.0 lane | Complete — CI verified; pilot acceptance open |
| 2026-11-02 | D2 independent source permissions | PR #65 final head `315a49a52f70ecb888e6d9cc91a4c1f4e51535d7` passed all required checks plus pinned Frappe v16.5.0 lane; merged as `0cfeda4fb39f79722fdf733abd06a3460ebcdd4d` | Complete — CI verified; target-site role acceptance open |
| 2026-11-02 | D1/D2 synthetic aggregate fixture | Final head `cfd7c5ec` passed all required checks; merged as `84ab2ce`; POS settlement/native-report reconciliation explicitly excluded | Complete — CI verified; target-site acceptance open |


## 2026-11-03 maintenance update

PR #97 merged as `b18f504` after Quality, Security and Bench Integration/E2E passed. PR #96 was refreshed onto that main head. The flit-core v4 compatibility change now has a direct artifact gate in Quality Checks: build wheel and sdist with flit-core v4, install each in a clean environment and import the package on Python 3.10 and 3.14. Final-head CI for PR #96 is pending; its earlier pre-refresh checks are not merge evidence. Frappe v15/v16 Bench + Playwright and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation remain required.

The application and operator guides remain code-complete and reference-stack CI-verified where stated above. The release decision remains **not approved for production sign-off** until the target-site preflight, real-user permission matrix, D1/D2 native-report reconciliation, Helpdesk SLA calendar, operational recovery and backup/restore/rollback rehearsal are recorded. Dashboard desktop/mobile visual UAT also remains open.


## 2026-11-03 current repository snapshot — after PR #109

- [x] PR #109 merged as [`94d14f5`](https://github.com/MitMike/crm_signals/commit/94d14f56a526670d2c0ecb150ab9f08b4f034389) from final head `d8b65eedc45c05947409f9781a9caaee848aa4ba`. All 18 final-head checks passed: Quality/lint, Python 3.10–3.14, Security/Semgrep, Bench v15/v16 including Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. The real-Git regression proves the clean SHA and untracked-dirty rejection behavior.
- [x] PR #110 release-document reconciliation merged as `fe7dca4`; all 13 final-head checks completed (11 success, two expected runtime-selector skips).
- [x] No open repository issues were returned at this review.
- [ ] **P0 target-site gate remains open:** authorized Frappe v16.5 staging, exact installed app inventory and approved SHA, effective-role permissions, D1/D2 native-report reconciliation by currency, Helpdesk SLA calendar, scheduler/mail/realtime/webhook recovery, backup/restore/rollback rehearsal and dashboard desktop/mobile visual UAT.
- **Release decision:** not approved for production sign-off. The application and operator guide are code-complete and reference-stack CI-verified where recorded; no pilot verification is claimed. A green CI run does not close a target-site gate.


## 2026-11-03 current repository snapshot — after PR #110

- [x] PR #109 real-Git clean/dirty preflight regression merged as `94d14f5`; all 18 final-head checks passed.
- [x] PR #110 release-document reconciliation merged as `fe7dca4`; all 13 final-head checks completed, with 11 successes and two expected docs-only runtime-selector skips.
- [x] Live open-PR and open-issue queries returned zero immediately after PR #110 merged.
- [ ] **P0 target-site acceptance remains open:** authorized Frappe v16.5 staging, exact installed app inventory and approved SHA, effective-role permissions, D1/D2 native-report reconciliation by currency, Helpdesk SLA calendar, scheduler/mail/realtime/webhook recovery, backup/restore/rollback rehearsal and dashboard desktop/mobile visual UAT.
- **Release decision:** not approved for production sign-off. D1/D2/D3/Explorer and the operator procedures are code-complete and reference-stack CI-verified where recorded; no pilot verification is claimed. Green CI is not target-site evidence.


## 2026-11-05 repository snapshot — after PR #162; PR #163 open

- Main `25b3d76e4e548bbed8a429d24ef26087798ada36`; PR #162 merged; PR #163 is the sole open PR; open issues: 0.
- Quality [41893249731](https://github.com/MitMike/crm_signals/actions/runs/41893249731), Security [41893249689](https://github.com/MitMike/crm_signals/actions/runs/41893249689), and Bench Integration/E2E [41893249676](https://github.com/MitMike/crm_signals/actions/runs/41893249676) All three passed on main. Quality lint/static and Python 3.10/3.11/3.12/3.14 unit jobs passed; Semgrep passed; Bench v15/v16 integration and validation passed, v16 Playwright E2E passed, and v15 Playwright E2E was skipped by its matrix setting.
- PR #163 adds AST parsing of Python examples embedded in the standalone support-configuration and D3 SLA-discovery HTML guides. CI parses only; it does not execute site commands, open a Bench console or mutate a site. No new ADR is required.
- **P0 target-site gate remains open:** authorized Frappe v16.5 staging, exact installed app inventory and approved full SHA, effective-role permissions, D1/D2 native-report reconciliation by currency, Helpdesk SLA calendar, scheduler/mail/realtime/webhook recovery, backup/restore/rollback rehearsal and dashboard desktop/mobile visual UAT.
- **Release decision:** not approved for production sign-off. Code-complete and reference-stack CI-verified status remains distinct from pilot verification; no pilot verification is claimed.

## 2026-11-05 repository snapshot — PR #163 merged; operator HTML syntax follow-up

- Main is [ba348e6](https://github.com/MitMike/crm_signals/commit/ba348e6526a4d6d5844d56bfc3b8ac388efd4c52); PR #163 merged; PR #164 was closed unmerged as a duplicate; open PRs: 0; open issues: 0 at this review.
- PR #163 exact final head [17bdf9e](https://github.com/MitMike/crm_signals/commit/17bdf9efd14e67ed586c9140d28ea6dad8def425) passed all four required workflows: Quality [41898150244](https://github.com/MitMike/crm_signals/actions/runs/41898150244), Security [41898150223](https://github.com/MitMike/crm_signals/actions/runs/41898150223), supported Frappe v15/v16 Bench integration and validation [41898150235](https://github.com/MitMike/crm_signals/actions/runs/41898150235), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 [41898150300](https://github.com/MitMike/crm_signals/actions/runs/41898150300).
- Post-merge main Quality [41903297571](https://github.com/MitMike/crm_signals/actions/runs/41903297571), Security [41903297622](https://github.com/MitMike/crm_signals/actions/runs/41903297622) and Bench [41903297576](https://github.com/MitMike/crm_signals/actions/runs/41903297576) all passed. Main Quality ran lint/static and Python 3.10/3.11/3.12/3.14; main Bench ran v15/v16 integration and validation. The push-event change detector was skipped, but the integration jobs still executed and passed.
- **Decision:** the first PR #163 regression only recognized Python snippets by leading `import`/`from` statements and did not validate the Bash command blocks in the same HTML guides. The follow-up PR explicitly labels every `<pre>` block as `bash` or `python`, checks the expected per-guide block counts, parses every Python block with AST and runs `bash -n` on every Bash block. Snippets are syntax-checked only; CI never executes operator commands or site-discovery code. No ADR is required because this is documentation metadata and test coverage only.
- **Release boundary unchanged:** Frappe v15/v16 compatibility and the pinned Frappe 16.5.0 reference lane remain CI-verified; actual target-site installation, permissions, D1/D2 reconciliation, D3 SLA, mail, webhook, worker/realtime, recovery and desktop/mobile visual acceptance remain pilot work. H remains partial; Vault and Analysis remain unimplemented and approval-gated. Production is not approved.


## 2026-11-05 active operator-guide validation PR #165 — operator HTML code-block language and syntax validation

- [x] Add explicit language labels to every `<pre>` example in the Frappe v16.5 support-configuration and D3 SLA-discovery HTML guides.
- [x] Static contract test discovers every block, enforces expected per-guide language counts, AST-parses Python examples and runs `bash -n` for Bash examples.
- [x] Focused local validation passed: all three embedded Python examples parse and all six embedded Bash examples pass `bash -n`.
- [x] Correct the support scripts' console-output separators to use actual newline escapes instead of printing literal `\\n`; static coverage rejects the old form.
- [ ] Final-head Quality, Security, Frappe v15/v16 Bench and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 checks must pass before merge.
- **Decision:** language metadata is explicit; syntax-check only and never execute site commands/snippets in CI. No runtime/schema/permission/dependency change and no new ADR.
- **Release boundary:** this improves operator-documentation integrity, not target-site acceptance or pilot verification.


## 2026-11-05 repository snapshot — PR #165 merged

- Main is [d0cb54f](https://github.com/MitMike/crm_signals/commit/d0cb54fe4d5f7f2cb3bbf9cbcc14fee9a8662d98); PR #165 was squash-merged from exact final head [3162597](https://github.com/MitMike/crm_signals/commit/3162597dec7e25d9790ced05d3c6792951fddd63). Open pull requests: 0; open issues: 0 at this review.
- All four required PR #165 final-head workflows passed: Quality [41908983613](https://github.com/MitMike/crm_signals/actions/runs/41908983613), Security/Semgrep [41908983421](https://github.com/MitMike/crm_signals/actions/runs/41908983421), supported Frappe v15/v16 Bench + Playwright [41908983574](https://github.com/MitMike/crm_signals/actions/runs/41908983574), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 [41908983460](https://github.com/MitMike/crm_signals/actions/runs/41908983460).
- The merged operator-guide contract labels every HTML pre block as Bash or Python, requires the expected per-guide counts, AST-parses all three Python examples, runs bash -n on all six shell examples, and rejects the literal-backslash-n output regression. CI parses but never executes site commands or discovery scripts.
- Post-merge main runs are not yet complete at this snapshot: Quality [41920151879](https://github.com/MitMike/crm_signals/actions/runs/41920151879) and Security [41920151933](https://github.com/MitMike/crm_signals/actions/runs/41920151933) are in progress; Bench [41920152015](https://github.com/MitMike/crm_signals/actions/runs/41920152015) is queued/in progress. Do not record these main runs as passed until completion.
- Decision: no runtime/product change is safe without the outstanding target-site/business evidence. Keep the current operator HTML examples syntax-only in CI; no new ADR is required.
- Release boundary: Frappe v15/v16 compatibility and the pinned Frappe 16.5.0 reference stack are CI-verified. Actual target-site installation, effective permissions, D1/D2 native-report reconciliation, D3 SLA calendar, digest/mail, webhook, worker/realtime, recovery, backup/restore/rollback and desktop/mobile visual acceptance remain not pilot-verified. H remains partial; Vault and Analysis remain approval-gated. Production is not approved.
