# Changelog

This changelog records user-visible and operationally significant changes. It is not a substitute for commit history. Entries do not imply a production release unless explicitly stated.

## 2026-11-01 — Main branch protection verified

### Confirmed
- Active ruleset Protect main (ID 26282133) targets refs/heads/main.
- Pull requests and eight strict, up-to-date required CI contexts are enforced.
- Review-thread resolution is required; the approval count is zero to avoid deadlocking a single maintainer.
- Branch deletion and force pushes are blocked; merge, squash and rebase are allowed.
- No bypass actors are configured. Emergency recovery requires an authorized administrator to edit and restore the ruleset.
- Dependency Security Audit remains active and passing but is not one of the eight required contexts.

### Validation
- GitHub branch API reports main as protected.
- GitHub ruleset API returned the active ruleset and complete rule list.
- [Issue #12](https://github.com/MitMike/crm_signals/issues/12) closed after verification.

## 2026-11-01 — D1/D2 metric safety corrections (merged in PR #17)

### Changed
- D1 active Lead/Opportunity metrics, Opportunity stages and active pipeline now report unavailable when required status metadata is absent instead of counting every record as active.
- D2 return-sensitive Sales Invoice measures require is_return; invoiced, POS receipts, outstanding receivables and overdue measures do not run when return identity cannot be established.
- The dashboard distinguishes missing metadata from successful zero counts and ordinary permission-denied states.
- Payment Entry receipt metrics remain independent of Sales Invoice return metadata.

### Validation
- Added regression tests for missing Lead status, Opportunity status and Sales Invoice is_return metadata.
- Merged as [fed496f](https://github.com/MitMike/crm_signals/commit/fed496f230f5ca88af25d663bc61fe4d748f5f83). Quality, Semgrep, Bench v15 and Bench v16 with authenticated Playwright passed on the final PR head.

## 2026-11-01 — Dependency security and CI hardening (merged; not a product release)

### Added
- Weekly Dependabot updates for Python packages, npm tooling dependencies and GitHub Actions.
- Automated Python dependency audits with pip-audit and npm dependency audits with moderate-or-higher findings treated as failures.

### Changed
- Updated Playwright test tooling to 1.64.1 and ESLint to 10.14.0.
- Pinned the vulnerable transitive minimatch dependency to patched 11.0.1.
- Added a complete npm lockfile v3 and use npm ci in Quality Checks and Dependency Security Audit.
- Updated security and engineering quality documentation.

### Validation
- PR #11 merged as [05ad767](https://github.com/MitMike/crm_signals/commit/05ad767f6b62814cca5b7d0c1e233a2f690baa77).
- All four PR gates passed on the final PR head: [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41232087717), [Bench Integration and E2E](https://github.com/MitMike/crm_signals/actions/runs/41232087747), [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41232087776) and [Dependency Security Audit](https://github.com/MitMike/crm_signals/actions/runs/41232087748).
- Post-merge Quality Checks and Security Scanning passed on main. The fresh post-merge Bench validation was still running when this entry was prepared.

This entry records engineering maintenance, not a formal release or production rollout.

## 2026-11-01 — Specifications and engineering governance (documentation work)

### Added
- Full specifications for CRM Signals core/access, event routing, daily digest, D1 Sales Compass, D3 Service Resolution/SLA, H Highlights, A Analysis, E Explorer and V Vault.
- A complete specifications catalogue with acceptance criteria and test mapping.
- A dependency-ordered delivery plan with stages, exit criteria, definition of done and target-site release blockers.
- Durable ADRs for dependency security, target-site acceptance, configurable business semantics, event idempotency, D3 source discovery, proposal-link privacy, adapter-based Explorer, append-only Vault snapshots and constrained Analysis queries.

### Clarified
- The CRM Signal is_read flag is a shared team acknowledgement in v1, not a per-user read receipt.
- D3 does not assume a ticket DocType or SLA schema; the target site's installed support system must be discovered first.
- Proposal-link tracking remains gated on privacy/consent review and stable event identity.
- Vault snapshot scheduling remains disabled until retention and source-visibility policy are explicitly approved.
- Analysis uses a server-owned metric/query registry; generated SQL is not permitted.

These are project planning and specification changes. They do not claim that the planned D3/H/A/E/V features are implemented.

## 2026-10-31 — Mainline baseline (documentation snapshot; not a tagged release)

This entry retrospectively records the capabilities present on main at commit [b55cce6](https://github.com/MitMike/crm_signals/commit/b55cce6469bbe7c1603c49175651eafa7259d879). It does not claim that a formal product release or production rollout occurred.

### Added
- Frappe app packaging metadata and the module/DocType layout required by the repository's documented Pilot discovery contract.
- CRM Signals DocType, authenticated signal ingestion, event hooks, scoped notifications, linked-party permission logic and scheduled digest.
- Native CRM Signals Desk Console.
- S.A.H.D.E.V. dashboard D1 Sales Compass and D2 Billing Realization.
- Billing metrics for submitted invoices, customer receipts, separate POS receipts, current open receivables and overdue invoices.
- Specifications-first development guidance, vertical-slice roadmap, quality-gate documentation and security-scanning documentation.
- Automated quality checks, Bench integration and Playwright E2E workflows, pre-commit hooks, Semgrep scanning and Dependabot configuration.
- Project progress and decision tracking documents.

### Important behavior and data semantics
- Dashboard reads are permission-aware; unavailable sources are not represented as zero.
- Monetary measures remain grouped by the relevant source currency.
- Payment Entry receipts and POS receipts are displayed separately. Payment Entry receipts include allocated and advance/unallocated receipts and are not described as invoice-allocated cash.
- Open receivables use party-account currency, matching the ERPNext outstanding balance basis.

### Validation recorded
On the baseline commit, GitHub Actions reported success for [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41227467943), [Bench Integration and E2E](https://github.com/MitMike/crm_signals/actions/runs/41227467937) and [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41227467867).

Production/target-site acceptance is not implied by these CI results. See [Project Progress](docs/PROGRESS.md) for outstanding validation and repository-protection actions.
