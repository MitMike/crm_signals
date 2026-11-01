# CRM Signals — Release-readiness completion sprint

**Started:** 2026-11-01  
**Last reviewed:** 2026-11-02  
**Baseline:** `main` at `ff434bdf407d1d61842d81fae16e04b4b9b483d5`  
**Decision register:** [ADR-046](DECISIONS.md#adr-046--run-release-readiness-as-an-evidence-gated-sprint)  
**Operating rule:** no item is complete without the evidence listed here. CI evidence and target-site evidence are separate.

## Sprint sequence

### 0. Active PR triage — current review queue

- [x] Merge [PR #32](https://github.com/MitMike/crm_signals/pull/32) for D3 standard Frappe Helpdesk metrics. Final head `93b536abef331d8b34b5b7b570fbb280a996bfb2` passed Python 3.10/3.11/3.12/3.14, lint/static, Semgrep and Bench v15/v16; merge commit `43fddfbbc46cac277a48c840251a7a2c963a8eb5`.
- [x] [PR #38](https://github.com/MitMike/crm_signals/pull/38) audited Failed-row replay merged as `1640bdd496706a7f297b0984f1fd1d9695307147`; Quality, Security and Bench v15/v16 passed. The action is POST-only, requires System Manager plus outbox read access, preserves attempt history and audit Comment, and confirms before replay.
- [ ] Complete [PR #46](https://github.com/MitMike/crm_signals/pull/46) exact Frappe v16.5.0/ERPNext v16.5.0/Helpdesk v1.30.2 Bench lane; the first v1.31.1 attempt failed on the missing Notification Type controller and ADR-056 records the corrected pin.
- [x] Complete [PR #45](https://github.com/MitMike/crm_signals/pull/45) per-company quotation thresholds. Final head `84783d15` passed all 16 required checks and merged as `ff434bdf`. Pilot approval/configuration for each Company remains.
- [x] [PR #44](https://github.com/MitMike/crm_signals/pull/44) source-document notification permission check merged as `48622c08700032566051978076f49bc807c381e7` after Quality, Security and Bench v15/v16 passed.
- [x] [PR #36](https://github.com/MitMike/crm_signals/pull/36) merged as `e57d94ea`; ADR-049 sets Frappe v16.5 as the primary target while retaining v15/v16 CI coverage.
- [x] [PR #42](https://github.com/MitMike/crm_signals/pull/42) merged D3 field-level permission hardening as `17eca3f6cb493fb8729632e0902c07ccb776b6a5`; Quality, Security and Bench v15/v16 passed.

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
- [ ] Verify Sales User/Manager field-level access for `status_category`, `resolution_date`, `resolution_time`, `sla` and `agreement_status`; field-level fail-closed correction merged in PR #42.
- [ ] Confirm active SLA working days/hours, holiday list and timezone against the Monday–Saturday assumption.
- [ ] Run staging fixtures for Open, Paused, Resolved, no-SLA, Fulfilled, Failed and due states; verify privacy-safe aggregate payloads.

**Gate:** D3 CI is not pilot acceptance. Site version, permissions and SLA calendar must be evidenced.

### 4. H Highlights

- [x] Implement high-value Quotation event generation and stable source identity.
- [x] Merge PR #45 Company-specific threshold rows; verify every enabled Company uses a matching base-currency threshold or approved fallback during pilot acceptance.
- [ ] Add the admin-managed VIP allowlist and validate escalation recipient permissions/cooldown behavior.

- [ ] Keep proposal-link tracking disabled until privacy/consent, retention and first-party link behavior are approved.
- [ ] If tracking is approved, implement opaque expiring/revocable tokens, stable event IDs, scanner classification and non-invasive diagnostics.
- [ ] Add Bench v15/v16 and Playwright coverage.

### 5. E, V and A roadmap

- [ ] E Explorer only after installed activity integrations and source identities are inventoried.
- [ ] V Vault only after metric definitions, source visibility and retention are approved.
- [ ] A Analysis only after a versioned server-owned metric registry exists; generated SQL/Python remains prohibited.

## Current blockers and known evidence

- `main` baseline is `ff434bdf407d1d61842d81fae16e04b4b9b483d5`; PR #32 D3, PR #38 replay, PR #42 field guard, PR #44 source permission and PR #45 thresholds are merged and CI-verified.
- PR #38 replay is merged after both Frappe v15/v16 Bench jobs passed.
- PR #45 threshold implementation merged as `ff434bdf`; Quality, Security and Bench v15/v16 passed on final head `84783d15`.
- PR #46 first failed at Helpdesk v1.31.1 post-install; ADR-056 pins v1.30.2 for Frappe v16.5.0 and the rerun is pending.
- PR #36 ADR-049 is merged; its final required checks passed.
- D3 field-level guard PR #42 is merged; target-site Sales role and SLA-calendar acceptance remain open.
- No target Frappe site is connected to this work. Pilot evidence for versions, Company policy, role/field permissions, finance reconciliation, SLA calendar and operations remains outstanding.

## Evidence log

| Date | Work | Evidence | Status |
|---|---|---|---|
| 2026-11-02 | PR #32 D3 merge | Final head `93b536ab` passed all 16 check runs; merge commit `43fddfb` | Complete — CI verified |
| 2026-11-02 | PR #38 replay implementation | Final head `8e4c58dc` passed Quality, Security and Bench v15/v16; merged as `1640bdd4` | Complete — CI verified |
| 2026-11-02 | PR #45 threshold implementation | Final head `84783d15` passed all 16 required checks; merged as `ff434bdf` | Complete — CI verified |
| 2026-11-02 | PR #46 exact target CI | Helpdesk v1.31.1 failed at post-install Notification Type controller; ADR-056 pins v1.30.2 for exact v16.5.0 lane | Validation pending |
| 2026-11-02 | ADR-049 target baseline | Frappe v16.5 confirmed; v15/v16 matrix retained | Complete — merged |
| 2026-11-02 | D3 field-level permissions | Fail-closed field permission guard merged in PR #42 and passed v15/v16 CI | Complete — CI verified |
