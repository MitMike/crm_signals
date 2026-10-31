# Changelog

This changelog records user-visible and operationally significant changes. It is not a substitute for commit history.

## 2026-10-31 — Mainline baseline (documentation snapshot; not a tagged release)

This entry retrospectively records the capabilities present on `main` at commit [`b55cce6`](https://github.com/MitMike/crm_signals/commit/b55cce6469bbe7c1603c49175651eafa7259d879). It does not claim that a formal product release or production rollout occurred.

### Added

- Frappe app packaging metadata and the module/DocType layout required by the repository's documented Pilot discovery contract.
- CRM Signals DocType, authenticated signal ingestion, event hooks, scoped notifications, linked-party permission logic and scheduled digest.
- Native CRM Signals Desk Console.
- S.A.H.D.E.V. dashboard D1 Sales Compass and D2 Billing Realization.
- Billing metrics for submitted invoices, customer receipts, separate POS receipts, current open receivables and overdue invoices.
- Specifications-first development guidance, a vertical-slice roadmap, quality-gate documentation and security-scanning documentation.
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
