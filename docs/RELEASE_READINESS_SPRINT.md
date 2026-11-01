# CRM Signals — Release-readiness completion sprint

**Started:** 2026-11-01  
**Last reviewed:** 2026-11-02  
**Baseline:** `main` at `e57d94ea3090cfa50c5270a673e14c19ec6acbe3`  
**Decision register:** [ADR-046](DECISIONS.md#adr-046--run-release-readiness-as-an-evidence-gated-sprint)  
**Operating rule:** no item is complete without the evidence listed here. CI evidence and target-site evidence are separate.

## Sprint sequence

### 0. Active PR triage — current review queue

- [x] Merge [PR #32](https://github.com/MitMike/crm_signals/pull/32) for D3 standard Frappe Helpdesk metrics. Final head `93b536abef331d8b34b5b7b570fbb280a996bfb2` passed Python 3.10/3.11/3.12/3.14, lint/static, Semgrep and Bench v15/v16; merge commit `43fddfbbc46cac277a48c840251a7a2c963a8eb5`.
- [ ] Complete [PR #38](https://github.com/MitMike/crm_signals/pull/33) audited Failed-row replay. Earlier Bench failures exposed unsupported `frappe.has_role` and `Document.get_comments` assumptions; replaced them with `frappe.get_roles` and a Comment query. The action is POST-only, requires System Manager plus outbox read access, preserves attempt history and confirms before replay. Latest Bench run is pending.
- [ ] Complete [PR #40](https://github.com/MitMike/crm_signals/pull/40) per-company quotation thresholds. Added the missing child-table controller after Bench install exposed it; added mismatch-currency regression coverage. Quality and Security passed on the rebased PR #40 head; Bench v15/v16 is running.
- [ ] Complete [PR #39](https://github.com/MitMike/crm_signals/pull/39) source-document notification permission check. Quality and Security passed; Bench v15/v16 is pending.
- [ ] [PR #36](https://github.com/MitMike/crm_signals/pull/36) merged as `e57d94ea`; ADR-049 sets Frappe v16.5 as the primary target while retaining v15/v16 CI coverage.
- [ ] Validate the D3 field-level permission guard on branch `fix/d3-field-permission-awareness`. Standard Helpdesk uses permlevels 7/8 and Frappe may silently drop fields the user cannot read.

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
- [ ] Verify Sales User/Manager field-level access for `status_category`, `resolution_date`, `resolution_time`, `sla` and `agreement_status`; field-level fail-closed correction is in review.
- [ ] Confirm active SLA working days/hours, holiday list and timezone against the Monday–Saturday assumption.
- [ ] Run staging fixtures for Open, Paused, Resolved, no-SLA, Fulfilled, Failed and due states; verify privacy-safe aggregate payloads.

**Gate:** D3 CI is not pilot acceptance. Site version, permissions and SLA calendar must be evidenced.

### 4. H Highlights

- [x] Implement high-value Quotation event generation and stable source identity.
- [ ] Merge PR #34 Company-specific threshold rows; verify every enabled Company uses a matching base-currency threshold or approved fallback.
- [ ] Add the admin-managed VIP allowlist and validate escalation recipient permissions/cooldown behavior.

- [ ] Keep proposal-link tracking disabled until privacy/consent, retention and first-party link behavior are approved.
- [ ] If tracking is approved, implement opaque expiring/revocable tokens, stable event IDs, scanner classification and non-invasive diagnostics.
- [ ] Add Bench v15/v16 and Playwright coverage.

### 5. E, V and A roadmap

- [ ] E Explorer only after installed activity integrations and source identities are inventoried.
- [ ] V Vault only after metric definitions, source visibility and retention are approved.
- [ ] A Analysis only after a versioned server-owned metric registry exists; generated SQL/Python remains prohibited.

## Current blockers and known evidence

- `main` baseline is `43fddfbbc46cac277a48c840251a7a2c963a8eb5`; PR #32 D3 is merged and CI-verified.
- PR #33 replay Bench rerun is pending after two evidence-based compatibility fixes; do not merge until both Frappe v15/v16 jobs pass.
- PR #34 threshold Quality Checks passed on the latest head; Bench v15/v16 rerun is pending after the child-table controller and currency-mismatch test fixes.
- PR #36 ADR-049 Quality and Security passed; fresh Bench v15/v16 run is pending after an earlier required-check cancellation prevented merge.
- D3 field-level guard has Python/lint/security checks passing; Bench v15/v16 is pending.
- No target Frappe site is connected to this work. Pilot evidence for versions, Company policy, role/field permissions, finance reconciliation, SLA calendar and operations remains outstanding.

## Evidence log

| Date | Work | Evidence | Status |
|---|---|---|---|
| 2026-11-02 | PR #32 D3 merge | Final head `93b536ab` passed all 16 check runs; merge commit `43fddfb` | Complete — CI verified |
| 2026-11-02 | PR #33 replay review | Bench exposed `frappe.has_role` and `get_comments` API assumptions; fixes and stronger authorization are committed | Validation pending |
| 2026-11-02 | PR #34 threshold review | Bench exposed missing child-table controller; controller and mismatch-currency test added | Validation pending |
| 2026-11-02 | ADR-049 target baseline | Frappe v16.5 confirmed; v15/v16 matrix retained | Validation pending |
| 2026-11-02 | D3 field-level permissions | Upstream Helpdesk permlevels 7/8 and Frappe field filtering verified; fail-closed correction added | Bench validation pending |
