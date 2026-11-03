# Changelog

### Read-only preflight source identity — PR #103 (merged and CI-verified as `5dbda02`)

- Extend the server-side target-site preflight to report the exact CRM Signals Git commit SHA only for a clean checkout, using bounded, fixed read-only Git queries; dirty, unavailable or malformed revisions fail closed.
- Add regression tests for clean/dirty checkout, valid SHA, Git failure without stderr disclosure, timeout, missing Git and invalid output. Update the administrator guide and target-site acceptance kit to require an exact match with the approved release SHA.
- Final head `fc7f0ae381267d04d7db9f14ec888d965c7fe828` passed all 18 check runs, including Quality/Python 3.10–3.14, Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. Squash-merged as `5dbda0291358350d5a720127a7d526145d3e3c60`. No target-site or pilot verification is implied.

### setup-uv v7 dependency update — PR #7 (merged and CI-verified as `331492c`)

- Updated `astral-sh/setup-uv@v6` to `@v7` in the Frappe v15/v16 Bench and pinned Frappe v16.5.0 workflows.
- Final head `a72c82c` passed all 18 check runs, including Quality, Security/Semgrep, Python 3.10/3.11/3.12/3.14, Bench v15/v16 + Playwright and the pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lane.
- Merged as `331492c5be1e5e32105e6d64b710d2e861c0111a`. No application code or lockfile changed.

This changelog records user-visible and operationally significant changes. It is not a substitute for commit history. Entries do not imply a production release unless explicitly stated.

### GME CRM Signals workspace label — PR #85 (merged and CI-verified as `5cc4308`)
- Change only the workspace display label/title to GME CRM Signals while preserving technical identifiers, routes, icon, links and shortcuts.
- Final head `b09a0cb` passed Quality, Security, Bench v15/v16 and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. No separate app-launcher tile is implied.

## Unreleased — Transactional signal outbox, durable realtime retry, D3 Helpdesk, Highlights, Explorer and D1/D2 CI contracts (PR #26, #32, #54, #57, #59, #60, #63, #65, #67, #69, #70, #71)

### Bug/fix evidence registers — PR #79 (merged as 7904a70)
- Add durable bug and fix registers with stable IDs, root-cause/reproduction evidence, regression prevention, and separate merged/CI-verified/UAT-verified states.
- Record the dashboard horizontal-inset regression as BUG-2026-001 / FIX-2026-001; PR #84 restored 24px horizontal padding and is merged/CI-verified. Desktop/mobile UAT after asset/cache refresh remains open.

### Dashboard horizontal inset — PR #84 (merged and CI-verified as `b1f4ad7`)
- Restore 24px horizontal padding and add a static regression assertion. Final head `f0e1909` passed Quality, Security, Bench v15/v16 and pinned Frappe v16.5.0. Desktop/mobile UAT remains outstanding.

### Regression-review PR template — PRs #80/#81 (closed unmerged)
- The optional checklist was not merged. The bug/fix registers themselves are present from PR #79. The template is not a required release gate.

### Change-aware CI execution — PR #76 (merged and CI-verified as cec49e7)
- Preserve stable required-check names while selecting Python, Bench and pinned Frappe v16.5.0 execution by changed runtime paths.
- Fail closed in the lint, Python and Bench gates if path detection fails; cover workflow definitions, workspace/DocType JSON, patches/fixtures, manifests, requirements, app config and module metadata.
- Restrict Quality push runs to main while retaining path-aware checks on every PR, preventing duplicate full feature-branch push runs.
- Final head d6a6300 passed all 19 check runs: Quality, Security/Semgrep, Python 3.10/3.11/3.12/3.14, Bench v15/v16 + Playwright and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. Merged as cec49e7.


### Immutable target-site deployment pin — PR #74 (merged as 1b57003)
- Require the approved full commit SHA and detached checkout for first installs and upgrades.
- The first-install order was subsequently found unsafe because Bench `get-app` installs the package/dependencies before returning; PR #82 corrects the sequence and adds supported-version Bench coverage. Do not use the old first-install snippet until that PR is CI-verified.

### Pin-before-install operator sequence — PR #82 (merged and CI-verified as `ac030b1`)
- Replace the unsafe `bench get-app` first-install sequence with direct clone using remote `upstream`, detach and verify the approved full SHA, then run `bench setup requirements crm_signals` before site installation, migration or build.
- Correct upgrade instructions to inspect the Bench-created `upstream` remote rather than assuming `origin`.
- Final head `ef4dc09` passed Quality, Security, Frappe v15/v16 Bench + v16 Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. Target-site staging rehearsal remains separate.

### Upload-artifact v7 dependency update — PR #88 (merged and CI-verified as `de8e78b`)
- Upgrade the two workflow upload sites from `actions/upload-artifact@v4` to `@v7`.
- Final head `eed57d6` passed Quality, Security, Frappe v15/v16 Bench + Playwright and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. The project uses GitHub-hosted runners; future self-hosted runners must meet the action's Node 24 requirements.

### D2 POS invoice settlement fixture — PR #69 (merged and CI-verified as efe7872)
- Create a disposable POS Profile and company-specific Mode of Payment, then submit an `is_pos` Sales Invoice through ERPNext's normal lifecycle.
- Assert ERPNext-calculated `paid_amount` settles `grand_total`; keep the setup and invoice inside the fixture rollback boundary.
- This does not simulate browser checkout, POS Opening/Closing, cash drawers or inventory movements; target-site native-report reconciliation remains separate.

### High-Value Quote source drill-down — PR #71 (merged; CI-verified)
- Return source_doctype/source_name only when the current user can read both CRM Signal source fields, the signal is a High-Value Quote sourced from Quotation, and the exact Quotation is readable.
- Suppress other source identifiers and fail closed on permission/metadata errors; the Desk row opens the Quotation while retaining existing party/Signal fallbacks.
- Add API permission-denial tests and Playwright coverage for the Console source route. ADR-072's failure-only CI diagnostic emitted the exact Prettier 3.9.10 diff; its three wrapping changes were applied in commit `91fc89c`. Final head `df0c273` passed Quality, Security, Python 3.10/3.11/3.12/3.14, Bench v15/v16 including Playwright, and the pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lane. Merged as `c5720bf`. Target-site role acceptance remains open.

### Read-only target-site preflight report — PR #70 (merged and CI-verified as 13341b7)
- Add a non-whitelisted Bench command to inventory installed app versions when importable, site timezone, Company currencies and threshold source/currency, active Lead/Opportunity workflow states, relevant DocType fields/Select options/permlevels and static DocPerm rows.
- Omit recipient email addresses, credentials and business-document rows; perform no writes.
- Add tests for exact-currency threshold behavior, workflow/field metadata, missing Helpdesk fields and recipient-address omission.
- Record ADR-068 and document the command in the administrator guide and target-site acceptance kit. All final-head required checks, including the pinned Frappe v16.5.0 lane, passed before merge. Target-site execution remains pending; no pilot verification is claimed.

### D2 independent source permissions — PR #65
- Keep Payment Entry customer receipts available when Sales Invoice read access is denied, as required by the D2 source contract.
- Clear partial Sales Invoice metrics after a permission exception and continue with the independent, permission-aware Payment Entry query.
- Add regression tests for Sales Invoice denied / Payment Entry allowed and for a query-level invoice permission exception after partial invoice results.
- Final-head Quality, Security/Semgrep, Python 3.10/3.11/3.12/3.14, Bench v15/v16 and pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 checks passed; merged as `0cfeda4`. No role grants or financial calculation changes.

### D1/D2 synthetic aggregate-value fixture — PR #67
- Add disposable Bench records for Lead/Opportunity and submitted Sales Invoice/Payment Entry aggregate-delta assertions.
- Verify INR/USD pipeline and invoice currency groups, party-account-currency receivables, overdue drill-down, POS-shaped paid totals and independent Payment Entry-only read access.
- Roll back all synthetic records and temporary permissions. The POS row models persisted aggregate fields only; POS settlement, native-report reconciliation and target-site role acceptance remain separate.
- Final head `cfd7c5ec64786e394374d31ba7b89354565a2070` passed all required checks on Frappe v15/v16 and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0; merged as `84ab2ce0b4ce1a9614882635e4c085092cf2a0c5`.

### D1/D2 real query-contract smoke — PR #63
- Execute the read-only Sales Compass API against installed ERPNext DocTypes in the Frappe v15/v16 Bench matrix and pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane.
- Verify Lead, Opportunity, Sales Invoice and Payment Entry response sections and required availability/shape contracts without creating business records or writing to the database.
- Restrict Bench workflow push runs to `main` while retaining PR and manual-dispatch validation, preventing duplicate feature-branch Bench runs.
- Final-head Quality, Security, Semgrep, Python, Bench v15/v16 and pinned-target checks passed. Merge commit: `0a7de966`.
- This is schema/query compatibility evidence only; target-site permission acceptance and D1/D2 native-report financial reconciliation remain open.


### H Highlights quotation contract — PR #60
- Add unit regressions for Company-base-currency threshold equality, below-threshold suppression, transaction-currency message display and fail-closed behavior when a foreign-currency Quotation has no base total.
- Align the H specification with the implemented Company-currency comparison and distinguish the shipped high-value Quotation alert from deferred VIP escalation and proposal-link tracking.
- Record ADR-061: do not invent VIP trigger/recipient policy, and do not implement proposal tracking before privacy/consent and retention approval.

### Explorer core timeline API — PR #57 (merged; CI verified)
- Add read-only CRM Signal, Quotation and Opportunity adapters for Lead/Customer-centered activity timelines.
- Resolve Lead, Customer, Opportunity, CRM Signal and High-Value Quote contexts through permission-aware reads; re-check source-document access before returning a Desk route.
- Check field-level read access for every context, filter, source and summary field; fail closed when Frappe would otherwise omit a required field.
- Return metadata-only summaries with deterministic ordering and bounded snapshot pagination; do not copy message bodies, amounts, recordings or attachments.
- Defer Communication/Event/ToDo and call/WhatsApp adapters until the target-site provider and schema inventory is recorded (ADR-059).


### Explorer Desk timeline UI — PR #59 (merged as `6b381fe`; final-head CI verified)
- Add a role-restricted Customer Activity Timeline page and Activity Timeline buttons on Lead, Customer, Opportunity and CRM Signal forms; High-Value Quote signals open the Highlight context.
- Add GET cursor paging, refresh, safely escaped metadata summaries, source navigation and distinct source states.
- Ignore late responses from earlier contexts when users navigate while a request is still in flight.
- Add static contract coverage and Playwright coverage for authenticated Lead-context paging and source drill-down; optional provider adapters and pilot role acceptance remain deferred.
- Final PR head `4bc7893513253d40ee60bb3a00b7c70827041eb9` passed all eight required ruleset contexts and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane.
### Realtime notification reliability
- Add a per-recipient delivery ledger with a stable SHA-256 ID, bounded retry/backoff and permission rechecks before each publish attempt.
- Add the stable ID to realtime payloads and suppress duplicate alerts within the active Desk session.
- Report `Attempted` as queued for after-commit publication only; Redis delivery, browser receipt and human acknowledgement remain unconfirmed.
- Target-site Redis outage, worker-restart and scheduler acceptance remain open.

### Added
- Persist Quotation and Opportunity source events in a dedicated idempotent outbox with scheduled retries, bounded exponential backoff and a terminal Failed state visible to System Managers.
- Add Bench coverage for delivery recovery, retry exhaustion, batch fairness, concurrent outbox processing, concurrent duplicate enqueue and immutable outbox permissions.
- Add a beginner-friendly D3 Support & SLA discovery guide with a metadata-only Bench script, business-calendar/permission/retention questions, KPI sign-off and an interactive completion checklist.

### Changed
- Abort a Quotation submit or Opportunity update if its outbox event cannot be persisted in the source transaction. Failures to materialize the CRM Signal after persistence remain retryable and do not block the source document.
- Keep outbox payload and delivery state read-only to administrators; inspect failures through the outbox and Error Log.

### Operational note
- Terminal Failed rows can be replayed only through the POST-only, System Manager/read-permission-gated action merged in PR #38; attempt history and an audit Comment are preserved. Realtime notification retry remains separate and is not provided by the signal outbox.

### Exact Frappe v16.5.0 / Helpdesk v1.28.0 compatibility lane — merged in PR #50

- Pin Frappe v16.5.0, ERPNext v16.5.0, Helpdesk v1.28.0 and the exact Telephony commit.
- Install the real Helpdesk app in Bench and verify HD Ticket / HD Service Level Agreement DocTypes, required fields, permlevels and the Frappe permitted-field API.
- Fix the D3 Helpdesk availability guard to check the physical `creation` system column with `frappe.db.has_column`; add a regression test where `Meta.has_field("creation")` is false but the database column exists.
- The inspected Helpdesk v1.29.0/v1.30.2/v1.31.1 desk manifests require `@framework/ui` from `frappe/ui`, absent in the unmodified Frappe v16.5.0 tag; v1.31.1 also requires `Notification Type`. The exact reference lane therefore pins v1.28.0.
- Keep moving v15/v16 coverage and the v16 Playwright E2E lane.

### Per-company quotation thresholds — merged in PR #45

- Add optional Company-specific threshold rows with an explicitly approved non-negative amount and currency derived from Company metadata.
- Use the legacy site-wide threshold only when its currency exactly matches the Company's base currency; never perform implicit FX conversion.
- If a Company's base currency changes, require the administrator to remove/re-add the row and enter a newly approved amount.
- PR #49 binds the Currency field to the child row's fetched Company base currency so the symbol/value displays correctly before saving.

### D3 Service Resolution/SLA — merged in PR #32

- Add aggregate-only Frappe Helpdesk metrics from standard `HD Ticket` and `HD Service Level Agreement` metadata: rolling ticket creation/resolution cohorts, current Open/Paused backlog, native resolution duration and Fulfilled/Failed SLA outcomes.
- Check ticket and SLA DocType read permissions independently; do not return ticket identifiers, subjects, comments, contact details or raw records to the dashboard.
- Keep due/paused SLA states out of the Fulfilled/Failed compliance denominator and count tickets without an SLA separately.
- Final PR #32 head `93b536abef331d8b34b5b7b570fbb280a996bfb2` passed Python 3.10/3.11/3.12/3.14, lint/static, Semgrep and Bench v15/v16. Merge commit: `43fddfbbc46cac277a48c840251a7a2c963a8eb5`.
- PR #42 merged a fail-closed field-level guard that checks the current user's permitted HD Ticket fields and marks affected measures unavailable instead of returning zero. PR #44 additionally requires read access to the originating source DocType before source-derived notification content is queued. Target-site app-version, Sales read-only role and active SLA calendar acceptance remain open.

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


### Explorer browser coverage and operator runbook hardening — PR #61 (merged as `6ef9642`; final-head CI verified)
- Add Playwright coverage for all five supported timeline context routes and for discarding a late response after the user changes context.
- Correct the deployment runbook to require Company-specific base-currency thresholds (or an exact-currency legacy fallback) and add Explorer role/context smoke tests.
- Final head `902b38e4dd4713461acfb12dc837f5b2b84da7d8` passed all eight required contexts and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane.
- Keep target-site role/field-permission acceptance and optional-provider discovery separate from CI verification.


### 2026-11-03 — Preflight source identity hardening (PR #105)
- Verify Git's top-level directory is the CRM Signals repository root derived from the imported package path before checking cleanliness or reading `HEAD`; reject enclosing Bench/monorepo roots with `repository_root_mismatch`.
- Add regression coverage for matching and parent repository roots. Preserve bounded read-only Git commands, dirty-tree rejection, full-SHA validation and non-disclosing failure reasons.
- Update the administrator guide, target-site acceptance kit and deployment runbook with the exact release-identity stop condition.
- PR #105 merged as [`db95812`](https://github.com/MitMike/crm_signals/commit/db958124bca6a6704a75f606629c22444716f5b9); all 19 final-head checks passed, including Python 3.10–3.14, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 validation. Target-site pilot acceptance remains outstanding.


### 2026-11-03 — Real-Git preflight parent-repository regression (PR #107)
- Add a temporary committed parent repository and nested Bench-style CRM Signals package path to exercise Git's real upward repository discovery.
- Assert the read-only preflight rejects the enclosing root with `repository_root_mismatch` instead of reporting the parent's SHA. Existing mocked failure-path coverage remains unchanged.
- No runtime code or site configuration changes; final-head CI is required before merge.


### 2026-11-03 — Real-Git preflight parent-repository regression (PR #107)
- Add an isolated integration regression that creates a committed enclosing Git repository and a nested Bench-style CRM Signals package path without child Git metadata.
- Invoke the real preflight source-revision helper and assert it rejects the enclosing repository with `repository_root_mismatch`, rather than reporting the parent's SHA.
- PR #107 merged as [`a472f19`](https://github.com/MitMike/crm_signals/commit/a472f1981f758ce7b6233d95fc0682fe69d7a304); all 19 final-head check runs passed across Python, Quality, Security, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 validation.
- No runtime behavior or site configuration changed. Target-site pilot acceptance remains outstanding.


### 2026-11-03 — Real-Git clean/dirty preflight source identity regression (PR #109)
- Add an integration test that commits a temporary CRM Signals package and verifies the preflight returns the exact clean Git SHA.
- Add an untracked Python override and verify the preflight fails closed with `working_tree_dirty` without querying `HEAD`.
- Complements ADR-087 root matching, ADR-088 enclosing-parent rejection and mocked error-path tests; no runtime behavior or target-site configuration changes.
- PR #109 requires final-head Python, Quality, Security, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 validation before merge.


### 2026-11-03 — Real-Git clean/dirty preflight regression merged (PR #109)
- PR #109 merged as [`94d14f5`](https://github.com/MitMike/crm_signals/commit/94d14f56a526670d2c0ecb150ab9f08b4f034389) from final head `d8b65eedc45c05947409f9781a9caaee848aa4ba`.
- All 18 final-head checks passed across Quality, Python 3.10–3.14, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0.
- The test proves the read-only preflight returns the real SHA for a clean checkout and rejects an untracked Python override without querying `HEAD`.
- Test-only; no runtime or site configuration change. Not pilot verification.
