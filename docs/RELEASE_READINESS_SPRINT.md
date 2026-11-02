# CRM Signals — Release-readiness completion sprint

**Started:** 2026-11-01  
**Last reviewed:** 2026-11-02  
**Latest main:** `1b57003df50df8a5f52cfe9866ed9bcba769bc67` (PR #74 immutable deployment revision procedure merged and CI-verified); **latest functional baseline:** `c5720bfb3fbe8b554ec6febd549a8d5e58acc1d7`  
**Decision register:** [ADR-046](DECISIONS.md#adr-046--run-release-readiness-as-an-evidence-gated-sprint)  
**Operating rule:** no item is complete without the evidence listed here. CI evidence and target-site evidence are separate.

- [ ] [PR #76](https://github.com/MitMike/crm_signals/pull/76) change-aware CI: initial workflow-only and temporary runtime-path checks passed, but ADR-075 adds fail-closed detector handling and package/build path coverage. Require fresh final-head Quality, Security, Bench v15/v16 and pinned v16.5.0 checks before merge.

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

- `main` baseline after PR #67 is `84ab2ce0b4ce1a9614882635e4c085092cf2a0c5`; PR #32 D3, PR #38 replay, PR #42 field guard, PR #44 source permission, PR #57/#59/#61 Explorer, PR #61 operator-runbook safeguards, PR #62 status reconciliation, PR #63 D1/D2 query smoke, PR #65 independent D2 source permissions, PR #66 documentation reconciliation and PR #67 D1/D2 synthetic fixture are merged and CI-verified; target-site acceptance remains open.
- PR #38 replay is merged after both Frappe v15/v16 Bench jobs passed.
- PR #45 threshold feature is merged; only target-site Company-by-Company amount and fallback approval remains.
- PR #36 ADR-049 is merged; its final required checks passed.
- D3 field-level guard PR #42 is merged; target-site Sales role and SLA-calendar acceptance remain open.
- No target Frappe site is connected to this work. Pilot evidence for versions, Company policy, role/field permissions, finance reconciliation, SLA calendar and operations remains outstanding.

## Evidence log

| Date | Work | Evidence | Status |
|---|---|---|---|
| 2026-11-02 | PR #32 D3 merge | Final head `93b536ab` passed all 16 check runs; merge commit `43fddfb` | Complete — CI verified |
| 2026-11-02 | PR #38 replay review | Replaced unsupported `frappe.has_role` / `get_comments` assumptions, strengthened authorization and verified replay on Bench v15/v16; merged as `1640bdd4` | Complete — CI verified |
| 2026-11-02 | PR #45 threshold merge | Company-specific amounts/currencies, exact-currency fallback and mismatch suppression merged; all required checks passed | Complete — CI verified |
| 2026-11-02 | ADR-049 target baseline | Frappe v16.5 confirmed; v15/v16 matrix retained | Complete — merged |
| 2026-11-02 | D3 field-level permissions | Fail-closed field permission guard merged in PR #42 and passed v15/v16 CI | Complete — CI verified |
| 2026-11-02 | Explorer API/Desk/browser slice | PR #57/#59/#61; five context routes, late-response suppression and operator runbook safeguards; final head `902b38e4dd4713461acfb12dc837f5b2b84da7d8` passed all required checks and pinned Frappe v16.5.0 lane | Complete — CI verified; pilot acceptance open |
| 2026-11-02 | D2 independent source permissions | PR #65 final head `315a49a52f70ecb888e6d9cc91a4c1f4e51535d7` passed all required checks plus pinned Frappe v16.5.0 lane; merged as `0cfeda4fb39f79722fdf733abd06a3460ebcdd4d` | Complete — CI verified; target-site role acceptance open |
| 2026-11-02 | D1/D2 synthetic aggregate fixture | Final head `cfd7c5ec` passed all required checks; merged as `84ab2ce`; POS settlement/native-report reconciliation explicitly excluded | Complete — CI verified; target-site acceptance open |
