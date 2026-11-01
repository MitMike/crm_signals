# Changelog

This changelog records user-visible and operationally significant changes. It is not a substitute for commit history. Entries do not imply a production release unless explicitly stated.

## Unreleased — Transactional signal outbox (PR #26)

### Added
- Persist Quotation and Opportunity source events in a dedicated idempotent outbox with scheduled retries, bounded exponential backoff and a terminal Failed state visible to System Managers.
- Add Bench coverage for delivery recovery, retry exhaustion, batch fairness, concurrent outbox processing, concurrent duplicate enqueue and immutable outbox permissions.

### Changed
- Abort a Quotation submit or Opportunity update if its outbox event cannot be persisted in the source transaction. Failures to materialize the CRM Signal after persistence remain retryable and do not block the source document.
- Keep outbox payload and delivery state read-only to administrators; inspect failures through the outbox and Error Log.

### Operational note
- Terminal Failed rows can be requeued only through the audited System Manager action above. Realtime notification retry remains separate and is not provided by the signal outbox.

### Audited terminal Failed-row replay — merged in PR #38

- Add a POST-only System Manager action requiring CRM Signal Outbox read permission, with an explicit confirmation dialog.
- Lock and replay only Failed rows; preserve original attempt count and last error, record replay count/actor/time and an audit Comment, then enqueue the same idempotent worker after commit.
- If enqueue fails, the row remains Pending for the scheduled worker; direct outbox status editing remains unavailable.
- PR #38 head `8e4c58dc3b2434559450651c3d3a4a649a034d3a` passed Quality, Security and Bench v15/v16. Merge commit: `1640bdd496706a7f297b0984f1fd1d9695307147`.

### Per-company quotation thresholds — in PR #45 review

- Add an optional Company-specific threshold table and derive each row's currency from Company metadata.
- Compare Quotation base totals to the matching Company threshold; use the legacy site-wide threshold only when currencies match exactly. No implicit FX conversion.
- Add tests for per-company selection, currency mismatch suppression and exact-currency fallback.


### D3 Service Resolution/SLA — merged in PR #32

- Add aggregate-only Frappe Helpdesk metrics from standard `HD Ticket` and `HD Service Level Agreement` metadata: rolling ticket creation/resolution cohorts, current Open/Paused backlog, native resolution duration and Fulfilled/Failed SLA outcomes.
- Check ticket and SLA DocType read permissions independently; do not return ticket identifiers, subjects, comments, contact details or raw records to the dashboard.
- Keep due/paused SLA states out of the Fulfilled/Failed compliance denominator and count tickets without an SLA separately.
- Final PR #32 head `93b536abef331d8b34b5b7b570fbb280a996bfb2` passed Python 3.10/3.11/3.12/3.14, lint/static, Semgrep and Bench v15/v16. Merge commit: `43fddfbbc46cac277a48c840251a7a2c963a8eb5`.
- PR #42 merged a fail-closed field-level guard that checks the current user's permitted HD Ticket field names and marks affected measures unavailable instead of returning zero. Target-site app-version, Sales read-only role and active SLA calendar acceptance remain open.

### Realtime source-document authorization — in PR #44 review

- Require read access to the originating Quotation/Opportunity as well as the linked Lead/Customer and CRM Signal before queuing a notification that may contain source-derived values.
- Fail closed for partially populated source DocType/name pairs; regression tests prove a Lead reader without Quotation access receives no source-derived notification.


## 2026-11-01 — Concurrent API idempotency and digest delivery hardening (merged in PR #23)

### Changed
- Recover the winning CRM Signal with a current locking read after a concurrent unique-key collision, preventing repeatable-read snapshots from hiding the row that another request committed.
- Serialize daily digest recipient claims with a lock on the CRM Signals Settings singleton and recheck the per-recipient/date marker before each queue request.
- Update system-owned digest markers through `Document.db_set` so operational status changes do not rerun unrelated administrator Settings validation; the Email Queue row and marker remain in one transaction.

### Added
- Deterministic two-connection Bench coverage for concurrent API requests and two overlapping digest workers.

### Validation
- PR #23 merged as [d75b7f3](https://github.com/MitMike/crm_signals/commit/d75b7f3591d2a863b0af6b8f88ad2a91e9bfd25f).
- [Bench Integration and E2E, Frappe v15/v16 + Playwright](https://github.com/MitMike/crm_signals/actions/runs/41300667892), [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41300667996) and [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41300667997) all passed on final PR head `7ed0860`.
- This is an engineering merge, not a production release. Target-site scheduler/mail, permission, currency, webhook and backup/rollback acceptance remains open.

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

## 2026-11-01 — D1/D2 metric safety corrections (merged in PR #17 as fed496f)

### Changed
- D1 active Lead/Opportunity metrics, Opportunity stages and active pipeline now report unavailable when required status metadata is absent instead of counting every record as active.
- D2 return-sensitive Sales Invoice measures require is_return; invoiced, POS receipts, outstanding receivables and overdue measures do not run when return identity cannot be established.
- The dashboard distinguishes missing metadata from successful zero counts and ordinary permission-denied states.
- Payment Entry receipt metrics remain independent of Sales Invoice return metadata.

### Validation
- Added regression tests for missing Lead status, Opportunity status and Sales Invoice is_return metadata.
- PR #17 merged as [fed496f](https://github.com/MitMike/crm_signals/commit/fed496f230f5ca88af25d663bc61fe4d748f5f83). CI passed on the merged head; target-site semantics and financial reconciliation remain separate acceptance gates.

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
- At the time this entry was prepared, the fresh post-merge Bench validation was still running. The subsequent PR #19 validation passed the full Frappe/ERPNext v15 and v16 Bench matrix, including the v16 Playwright suite (see the PR #19 validation entry below).

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


## 2026-11-01 — Source size and complexity guardrails (merged in PR #18)

### Added
- Graduated file-size thresholds: production source warns above 500 non-blank lines and fails above 800; test/E2E source warns above 800 and fails above 1,200.
- Python function-length checks, Ruff cyclomatic-complexity enforcement, and ESLint complexity/function-length enforcement.
- A standard-library checker, unit tests, pre-commit integration and a narrow exact-path exception registry.

### Validation
- PR #18 merged as [f51fbce](https://github.com/MitMike/crm_signals/commit/f51fbce19b7d1e84cfa6f3ab26118f2977a8fe40).
- Quality Checks [41242229437](https://github.com/MitMike/crm_signals/actions/runs/41242229437), Bench Integration/E2E [41242229451](https://github.com/MitMike/crm_signals/actions/runs/41242229451), Security Scanning [41242229463](https://github.com/MitMike/crm_signals/actions/runs/41242229463) and Dependency Security Audit [41242229456](https://github.com/MitMike/crm_signals/actions/runs/41242229456) passed on the PR head.
- This is engineering governance, not a product release.


## 2026-11-01 — Configurable Settings and core reliability (merged; not a product release)

### Added
- System Manager-only CRM Signals Settings singleton with Balanced, Sales Focused and Executive starter presets.
- Configurable event switches, quotation threshold/currency, Opportunity trigger statuses, digest time/stale window and additional enabled System User recipients.
- SHA-256 source-event identity with a unique database key; DocType validation derives the hash server-side, and optional webhook event IDs return the original signal on retry.
- Site-timezone digest scheduling, separate permission-filtered emails per recipient, transactional per-recipient queue tracking, transaction-currency amount labels, registered enabled-System-User recipient validation and per-recipient notification failure isolation.
- Administrator guide, settings/reliability spec, regression tests, Settings preset Playwright coverage and recorded ADR-026 through ADR-033.
- Realtime alerts now require both linked-party and CRM Signal read permission; unit and Bench-backed tests cover the authorization boundary (ADR-034).
- Align CRM Signal list and direct-document permissions so linked-signal ownership cannot bypass parent User Permissions; add unit and Bench regression coverage (ADR-035).
- Add a deployment/rollback runbook covering preflight, backups, migration, smoke tests, rollback and target-site evidence.
- Default the master switch and external ingestion to off until System Manager explicitly enables the reviewed configuration (ADR-036).
- Bound daily digest output to 100 Quotations and report truncation rather than creating unbounded email payloads (ADR-037).
- Add Bench-backed API idempotency and source-key tests for duplicate requests, notification dedupe, per-user namespaces and legacy null-key compatibility.
- Add a production-readiness audit with explicit P0/P1/P2 gates and follow-up ownership.

### Validation
- Merged in [PR #19](https://github.com/MitMike/crm_signals/pull/19) as [a495919](https://github.com/MitMike/crm_signals/commit/a49591947a89b011cc1770be176c1f11571b131b).
- Validated head: `a90315be7ef37e2dceeacb9b4e9b77d5d31df131`. [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41274491111), [Bench Integration and E2E](https://github.com/MitMike/crm_signals/actions/runs/41274491113) (Frappe/ERPNext v15 and v16, including v16 Playwright) and [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41274491117) passed; all 16 check-runs on that head succeeded.
- Target-site validation remains outstanding. This merge does not claim a production rollout or a formal product release.


### 2026-11-01 — CI compatibility and idempotency corrections (merged in PR #19)

- Correct the CRM Signal document-permission hook for Frappe v15/v16 argument and return-value differences without bypassing role-level DocType permissions.
- Recover from database unique-key races by reading the winning source-event row under a lock; cover the race path in a Bench-backed regression test.
- Verify authenticated API users have the minimum CRM Signal create permission; test idempotency at notification-dispatch level so recipient fan-out is not mistaken for duplicate dispatch.
- Correct the dashboard E2E Prettier formatting and remove the temporary CI diagnostic step.

Included in PR #19's merge commit [a495919](https://github.com/MitMike/crm_signals/commit/a49591947a89b011cc1770be176c1f11571b131b); the final v15/v16 Bench, quality and security checks passed.


### 2026-11-01 — E2E navigation and settings synchronization (merged in PR #19)

- Wait for Frappe Desk navigation after the session cookie is established, preventing subsequent test requests from racing the login redirect.
- Await the settings form's custom-preset model update and commit the integer field before asserting the preset change.

Included in PR #19's merge commit [a495919](https://github.com/MitMike/crm_signals/commit/a49591947a89b011cc1770be176c1f11571b131b); the final v16 Playwright suite passed.
