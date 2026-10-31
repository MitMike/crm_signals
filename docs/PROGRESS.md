# Project Progress

**Last reviewed:** 2026-11-01  
**Repository:** [MitMike/crm_signals](https://github.com/MitMike/crm_signals)  
**Main baseline:** [fed496f](https://github.com/MitMike/crm_signals/commit/fed496f230f5ca88af25d663bc61fe4d748f5f83)

This is the operational status record. [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) is the delivery roadmap; [DECISIONS.md](DECISIONS.md) is the durable decision register; [specs/](../specs/) contains the feature contracts.

## Current status

| Workstream | Status | Remaining acceptance |
|---|---|---|
| CRM Signals core | Implemented baseline | Idempotency, validated settings, recipient read checks, deployment controls and target-site role tests |
| Signals Console | Implemented baseline | Target-site role and workflow smoke tests |
| D1 Sales Compass | Implemented; PR #17 merged | Target-site terminal-status semantics and workflow validation |
| D2 Billing Realization | Implemented; PR #17 merged | Financial reconciliation and role validation on the intended site |
| D3 Service Resolution/SLA | Specified; implementation gated | Discover installed support app, ticket DocType and SLA semantics before choosing an adapter |
| H Highlights | Specified; partial quote event exists | Configurable settings, event idempotency, verified proposal events and privacy approval |
| E Explorer | Specified; planned | Inventory actual installed integrations; implement source adapters only for verified sources |
| V Vault | Specified; planned | Approve metric registry, source visibility and retention before scheduling snapshots |
| A Analysis | Specified; planned | Build approved metric/query registry; do not execute model-generated SQL |
| Dependency/security hardening | Merged in PR #11 | Continue routine Dependabot and audit maintenance |
| Full specifications and roadmap | Merged in PR #16 | Keep docs aligned as slices are implemented |
| D1/D2 correctness hardening | Merged in PR #17 | Continue Stage 1 settings/idempotency and target-site acceptance |
| Main branch ruleset | Verified active | Maintain stable check names and update ruleset when workflows change |

## Merged delivery and validation

### Stage 0 — dependency security and reproducible CI

[PR #11](https://github.com/MitMike/crm_signals/pull/11) merged as [05ad767](https://github.com/MitMike/crm_signals/commit/05ad767f6b62814cca5b7d0c1e233a2f690baa77).

- Weekly Dependabot for pip, npm and GitHub Actions.
- Patched Playwright 1.64.1, ESLint 10.14.0 and minimatch 11.0.1 override.
- Complete npm lockfile v3 committed; CI uses npm ci.
- Python pip-audit and npm audit with moderate-or-higher failures.
- Security/quality documentation updated.

Final PR checks passed:
- [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41232087717)
- [Bench Integration and E2E](https://github.com/MitMike/crm_signals/actions/runs/41232087747)
- [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41232087776)
- [Dependency Security Audit](https://github.com/MitMike/crm_signals/actions/runs/41232087748)

Post-merge main checks for that change also passed: Quality [41232593555](https://github.com/MitMike/crm_signals/actions/runs/41232593555), Security [41232593543](https://github.com/MitMike/crm_signals/actions/runs/41232593543), and Bench v15/v16 [41232593526](https://github.com/MitMike/crm_signals/actions/runs/41232593526).

### Specifications, roadmap and decisions

[PR #16](https://github.com/MitMike/crm_signals/pull/16) merged as [b4ee3cf](https://github.com/MitMike/crm_signals/commit/b4ee3cfacf0b3aeee31789af6732d400fb455f95).

- Added full specifications for CRM Signals core/access, events/notifications, daily digest, D1, D3, H, A, E and V. Existing D2 specification retained and strengthened.
- Rewrote IMPLEMENTATION_PLAN.md with staged delivery order, dependencies, priorities, exit criteria and definition of done.
- Reconciled README, CHANGELOG, specs index and S.A.H.D.E.V. roadmap.
- Extended DECISIONS.md through ADR-024.

### Stage 1 metric correctness

[PR #17](https://github.com/MitMike/crm_signals/pull/17) merged as [fed496f](https://github.com/MitMike/crm_signals/commit/fed496f230f5ca88af25d663bc61fe4d748f5f83).

D1 changes:
- Lead active count is unavailable when Lead.status metadata is missing; the independent 30-day Lead creation count remains available.
- Opportunity active count and stage distribution are unavailable without Opportunity.status.
- Active pipeline requires status, amount and currency metadata so terminal Opportunities can be excluded and unlike currencies stay separate.
- Opportunity total count and recent records remain available where their independent fields and permissions permit.
- Desk UI distinguishes unavailable metadata from a valid zero or permission denial.

D2 changes:
- Invoiced, POS receipt, current outstanding and overdue Sales Invoice measures require Sales Invoice.is_return.
- If is_return is missing, the API does not run a Sales Invoice aggregate without the return-exclusion filter. Affected measures return unavailable with an explanation.
- Customer Receive Payment Entry receipts remain independent of Sales Invoice return metadata.

Regression tests cover missing Lead status, Opportunity status and Sales Invoice is_return. The E2E fixtures were updated for the explicit availability flags, and browser coverage verifies the unavailable states.

Final PR #17 checks passed on the latest head:
- Quality Checks, including all four Python versions and strict Prettier.
- Security Scanning (Semgrep).
- Bench v15.
- Bench v16, including authenticated Playwright E2E.

Post-merge on main, Quality Checks [41235445359](https://github.com/MitMike/crm_signals/actions/runs/41235445359) and Security Scanning [41235430899](https://github.com/MitMike/crm_signals/actions/runs/41235430899) passed. Fresh post-merge Bench runs [41235445479](https://github.com/MitMike/crm_signals/actions/runs/41235445479) and [41235430985](https://github.com/MitMike/crm_signals/actions/runs/41235430985) were still running their v15/v16 validation when this snapshot was written.

## Main branch protection — verified 2026-11-01

GitHub confirms active ruleset [Protect main](https://github.com/MitMike/crm_signals/rules/26282133), ID 26282133, targeting refs/heads/main.

- Pull requests required; no bypass actors.
- Strict/up-to-date required checks: Lint and static checks; Python unit tests (3.10), (3.11), (3.12), (3.14); Semgrep static security analysis; Bench v15 / Python 3.11; Bench v16 / Python 3.14 / authenticated Playwright E2E.
- Review threads must be resolved.
- Required approving review count is zero (solo maintainer); code-owner and last-push approval are not required.
- Branch deletion and non-fast-forward updates (force pushes) are blocked.
- Allowed merge methods: merge, squash and rebase.
- No bypass actors. Emergency recovery requires an authorized administrator to edit the ruleset temporarily, document the reason and restore enforcement immediately.
- Dependency Security Audit runs on dependency PRs, weekly and manually, but is not one of the eight required contexts.

[Issue #12](https://github.com/MitMike/crm_signals/issues/12) was closed after API verification. Keep the eight required job names stable and revise the ruleset if workflows are renamed.

## Outstanding gates

### Stage 1 — core and release hardening

- [ ] Add source DocType, source document and stable source event identity to CRM Signals; enforce idempotent writes for hook/webhook retries.
- [ ] Add validated CRM Signals Settings for high-value quotation threshold, Opportunity trigger statuses, Lead stale window, digest time and approved escalation recipients.
- [ ] Use Company/source currency rather than hard-coded INR symbols in quote and digest messages.
- [ ] Verify recipients can read the linked party before sending user-targeted alerts.
- [ ] Verify list, direct form, report, export and API permission parity for Sales User, Sales Manager and non-sales users.
- [ ] Confirm digest wording, timezone, recipient set and duplicate-run behavior.
- [ ] Complete D2 reconciliation against native ERPNext invoice/payment reports on the intended site.
- [ ] Complete deployment runbook, TLS/rate limiting, credential rotation, backup and rollback checks.

### Target-site acceptance

The following facts must be discovered on the intended site; do not infer them from CI:
- Frappe/ERPNext versions and installed support/communication apps.
- Company default currency and site timezone.
- Opportunity workflow/status values and terminal Lead statuses.
- Support ticket DocType, resolution timestamp, SLA deadline/outcome, pause behavior and business calendar.
- Custom roles, DocType customizations, permission rules and actual financial totals.
- Privacy/consent and retention policy for proposal tracking and historical snapshots.

### Later vertical slices

- [ ] D3: complete source discovery and business-owner approval before adapter implementation.
- [ ] H: make quote rules configurable; proposal-link tracking remains disabled until privacy/consent review.
- [ ] E: implement only adapters for installed/configured sources with stable event IDs.
- [ ] V: keep scheduled snapshots disabled until metric registry, source visibility and retention policy are approved.
- [ ] A: execute only server-owned, versioned, permission-aware metric queries; no arbitrary/generated SQL.

## Update protocol

Update this file when code is merged, validation changes, a blocker is found or a target-site gate is completed. Record the commit SHA and CI evidence. Never mark work complete based only on source code existing or mocked unit tests passing.

For every feature delivery:
1. Update the spec before implementation.
2. Define source fields, metric semantics, permission rules, unavailable states and edge cases.
3. Map acceptance criteria to unit, Bench integration and browser E2E tests as applicable.
4. Record consequential choices in DECISIONS.md.
5. Update CHANGELOG.md for user-visible or operationally significant changes.
6. Reconcile this status document after merge and validation.
