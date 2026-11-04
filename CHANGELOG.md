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


### 2026-11-03 — Release-document reconciliation merged (PR #110)
- PR #110 merged as [`fe7dca4`](https://github.com/MitMike/crm_signals/commit/fe7dca402293faa1e7e60f147d53adaef63009d6) from final head `f4904b7bd88725017f5f2254de9ceb3c123163cc`.
- All 13 final-head check runs completed: 11 succeeded and two runtime selectors were skipped as expected for documentation-only changes.
- Updated the implementation plan, progress, follow-ups, release-readiness sprint and historical production-audit notice; corrected README D3 acceptance wording.
- No runtime code or site configuration changed. Target-site pilot acceptance remains outstanding.


### 2026-11-03 — Release-document reconciliation merged (PR #111)
- PR #111 merged as [`166ca6b`](https://github.com/MitMike/crm_signals/commit/166ca6b2cc9838ffd68c551b327ee41d2a5316b4) from final head `30d44ffd48a1f39ef39d658a6bdc12b07f8130da`.
- All 13 final-head checks completed: 11 succeeded and two docs-only runtime selectors were skipped. The main commit subsequently completed all 17 check runs with 16 successes and one expected docs-only selector skip.
- The live repository review found no open pull requests or issues.

### 2026-11-03 — Pin the README first-install sequence before Bench setup (ADR-090 / PR #112)
- Replace the unsafe moving-branch `bench get-app ... --branch main` example with the established direct-clone, approved-SHA detach/verify, then `bench setup requirements crm_signals` sequence.
- Link existing-install upgrades to the Administrator Guide and Deployment Runbook so all operator entry points use the same verified procedure.
- Documentation and static-test-only; no runtime or dependency change. The static contract test protects the README's pin-before-requirements ordering. Authorized Frappe v16.5 staging rehearsal remains required and is not implied by CI.


### 2026-11-03 — README pin-before-install correction merged (PR #112 / ADR-090)
- PR #112 merged as [`d2e1d87`](https://github.com/MitMike/crm_signals/commit/d2e1d873a8f257545596379e179aeb3e4de40dd4) from final head `f68939ba5e2977ed62698e2a78084277fa091479`.
- All 18 final-head checks passed across Quality, Python 3.10–3.14, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation.
- README first-install instructions now pin and verify the approved full SHA before Bench dependency setup; the static test protects the sequence.
- Documentation/static-test only. Authorized target-site first-install and upgrade rehearsal remains outstanding; not pilot verification.

### 2026-11-03 — D3 guide implementation status and custom-source boundary (ADR-091)
- Clarify in both HTML guides that the standard Helpdesk adapter is implemented and custom/different ticket sources require a separately approved scope.
- Add static contract coverage for both guide statements.
- No runtime or site configuration change. D3 target-site acceptance remains outstanding.


### 2026-11-03 — D3 setup guide CI correction
- Python 3.11 and 3.12 each exposed one static-contract failure (125 passed, 36 skipped, 1 failed): a second stale promise to build a custom adapter remained in the guide's final workflow list.
- Replace that promise with existing-adapter validation/configuration steps, retain separate approval for custom sources, and correct the guide footer label.
- Extend static contract coverage to reject the stale promise and wrong footer. No runtime behavior or site configuration change; rerun the full final-head matrix before merge.


### 2026-11-03 — D3 guide static-test wording correction
- Python 3.11, 3.12 and 3.14 each exposed one stale assertion after the guide wording was corrected.
- Align the static test with the approved sentence that custom sources require separate approval and scope.
- Test-only correction; no runtime or site configuration change. Full final-head CI remains required.


### 2026-11-03 — D3 operator-guide correction merged (PR #117 / ADR-091)
- PR #117 merged as 93e7e16 (merge commit 93e7e16271d727476618b4981498ad901835bad4) from final head 2d7463f5e73bec3741ef9fb68d9b707b9bb1afc6.
- All 35 final-head checks passed: Python 3.10–3.14, Quality, Semgrep, Bench v15/v16 including Playwright, pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 and bench-validation selectors.
- Corrected both D3 operator guides and added static regression coverage for the existing adapter and custom-source approval boundary.
- No runtime code, dependencies, schema or site configuration changed. D3 pilot acceptance remains outstanding.


### 2026-11-03 — Post-PR117 documentation reconciliation merged (PR #118)
- PR #118 merged as 3cb9f017b1694727f0b1729d5e2af9a7913a7715.
- All 11 applicable final-head checks passed; two runtime selectors were skipped as expected for documentation-only changes.
- Updated project plan, progress, follow-ups, ADR-091 verification and changelog to record PR #117's 35/35 CI result and remaining target-site gates.
- No runtime code, dependencies, schema or site configuration changed.


### 2026-11-03 — Optional effective-user permission preflight (ADR-092 / PR #120)
- Extend the read-only Bench preflight with an optional alias-to-synthetic-User mapping for Sales User, Sales Manager, System Manager and non-sales profiles.
- Validate account activity and expected role boundary, then use Frappe's user-aware DocType and permitted-field APIs to report required read access. Reject Administrator, disabled, duplicate and invalid-role accounts; return profile aliases only and omit User identities.
- Update the Administrator Guide, Deployment Runbook and Target-Site Acceptance Kit. Add regression tests for allowed/denied DocType and field results, invalid accounts/profiles, default-unavailable behavior and identity non-disclosure.
- No schema, dependency, metric or site configuration changes. Row-level permissions and end-to-end site acceptance remain separate. PR #120 final-head CI is pending; no pilot verification is claimed.


### 2026-11-03 — Exercise effective-user preflight on real Frappe stacks (ADR-093 / PR #120)
- Add an `allow_tests`-guarded CI fixture that creates disposable synthetic Sales User, Sales Manager, System Manager and Employee accounts with random throwaway passwords.
- Invoke the production effective-user preflight against real Frappe metadata and assert complete DocType/field result shapes, valid roles, no permission API errors and no account-identity disclosure.
- Run the fixture in Frappe v15/v16 Bench and pinned Frappe v16.5.0 / ERPNext / Helpdesk CI. It is compatibility evidence only; target-site record-level permission acceptance remains separate.


### 2026-11-03 — Refactor effective-user CI fixture after lint feedback
- The first ADR-093 head failed Ruff C901 because the orchestration function exceeded the complexity limit (19 > 15).
- Split profile and report validation into focused helpers without relaxing lint rules; final-head CI must rerun.


### 2026-11-03 — Reject malformed falsey permission-probe input
- Treat only `None` and an empty dictionary as an omitted optional user mapping.
- Reject falsey non-mapping values and add regression coverage so malformed operator input cannot silently look like an intentionally unavailable probe.


### 2026-11-03 — Require System User accounts in effective-user preflight
- Reject enabled Website Users before DocType/field checks, even if they carry a sales role, because they cannot access Desk.
- Add a Website User regression test and extend the real-Frappe CI fixture to assert all synthetic profiles are System Users.


### 2026-11-03 — Effective-user permission preflight merged (PR #120 / ADR-092/093)
- PR #120 merged as [`a778c47`](https://github.com/MitMike/crm_signals/commit/a778c47b5078ac69dd89bdcd3ecab41de09b8072) from final head `e95efccec019df3fbadd1703f34c5682340b7f58`.
- All 18 final-head check runs passed: Quality/lint, Python 3.10–3.14, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. The real-Frappe effective-user preflight smoke passed on v15, v16 and pinned v16.5.0.
- The optional read-only probe reports DocType and required-field read outcomes for explicitly supplied active synthetic System Users, with alias-only output and no business-document rows. Website Users, Administrator, disabled, duplicate and invalid-role accounts are rejected.
- The probe and its CI fixture are code-complete and reference-stack CI-verified, not pilot-verified. Controlled-record permission, finance reconciliation, Helpdesk SLA, operational recovery, rollback and dashboard visual acceptance remain target-site gates.



### 2026-11-03 — Synthetic-record list-visibility preflight (ADR-094 / PR #122)
- Add an optional bounded \`test_records\` input to the non-whitelisted target-site preflight for exact synthetic record names grouped by profile, DocType and non-sensitive label.
- Temporarily switch to each explicitly supplied System User and call permission-filtered \`frappe.get_list\` with an exact name filter and \`fields=["name"]\`; return labels/booleans only. Missing and inaccessible records both report false.
- Enforce known-DocType, label, 50-record-per-profile and 100-record-total bounds; restore the prior session user and fail closed on query/session errors.
- Add unit tests and a disposable real-Frappe CI smoke using a synthetic CRM Signal that is rolled back. Update the Administrator Guide, Deployment Runbook and Target-Site Acceptance Kit.
- This checks list visibility only. Direct form/API/report/export/print/dashboard acceptance and all other target-site release gates remain open.



### 2026-11-03 — Restore preflight session after partial user-switch failure (PR #122 review)
- Keep original-session restoration in a common `finally` even when `frappe.set_user(test_user)` mutates session state and then raises.
- Add regression coverage for the mutate-then-raise path, fail-closed output and record-name/exception-message non-disclosure.
- Prior PR #122 head passed all four CI workflows; this correction requires a fresh final-head matrix. No schema, dependency, metric or site-configuration change.


## PR #122 merged — synthetic-record list visibility (2026-11-03)

PR [#122](https://github.com/MitMike/crm_signals/pull/122) merged as [de16ead](https://github.com/MitMike/crm_signals/commit/de16ead6ed2f155e83189196755048a264c2ec74) from final head [5339d71](https://github.com/MitMike/crm_signals/commit/5339d7135ff87902974dc2d038051e101434389e).

All four final-head workflows completed successfully: Quality Checks (run 41603744414), Security Scanning/Semgrep (41603744435), Bench Integration and E2E (41603744404), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation (41603744511). The Quality run passed the configured Python 3.10, 3.11, 3.12 and 3.14 test jobs plus lint/static checks. Bench v15/v16 integration passed, including the v16 Playwright job. The pinned lane passed the real-Frappe synthetic-record visibility probe, D1/D2 aggregate/permission checks, Helpdesk schema and D3 aggregate checks, schema upgrade, asset build, Python tests and Frappe integration tests.

The first Python run had five failures from a stale helper signature; it was corrected and the final-head matrix passed. A separate review correction ensured a frappe.set_user call that mutates session state and then raises still flows through the restoration finally; the final-head regression verifies restoration is attempted, no list query runs and record names/exception messages are not disclosed. No failing head was merged.

The optional preflight is code-complete and reference-stack CI-verified, not pilot-verified. It checks bounded permission-filtered list visibility for exact supplied synthetic records and returns labels/booleans only. Direct form, REST API, report, export, print and dashboard access remain separate acceptance paths. Authorized Frappe v16.5 staging, approved release SHA, named owners and controlled synthetic records are still required for pilot acceptance, alongside D1/D2 native-report reconciliation, Helpdesk SLA, deployment/rollback, operational recovery, backup/restore and desktop/mobile UAT.


## PR #124 opening snapshot — real Sales User record-filter preflight regression (2026-11-03)

- **Reviewed main:** `c9df68e3728fe675e4eb3b4d5dafaf8b4d29fcc6` (PR #122 and PR #123 merged; no open PRs or issues at branch creation).
- **Finding:** PR #122's real-Frappe preflight smoke proves a System Manager can list a synthetic CRM Signal, but does not invoke the new `test_records` path for a restricted Sales User. The existing Bench permission test already creates a Sales User, a linked Lead excluded by a User Permission, and an unlinked signal owned by that user.
- **Decision (ADR-095):** reuse that controlled fixture to call `get_site_preflight_report(test_users=..., test_records=...)` and assert the probe reports the linked/restricted signal as false and the unlinked/owned signal as true. Assert the result is checked, the original session user is restored, and neither record name nor user identity is returned.
- **Scope:** integration-test-only; no runtime behavior, schema, dependency or site configuration change. The existing Bench v15/v16 + Playwright and pinned Frappe 16.5.0 workflows execute the integration test suite.
- **Status at opening:** code-complete; final-head Quality, Python, Security/Semgrep, Bench v15/v16 and pinned Frappe 16.5.0 checks pending. Not pilot-verified.
- **Revisit criteria:** if Frappe v15/v16 returns a different list result, inspect the real `crm_signal_query` and User Permission behavior; do not weaken the expected false/true boundary or replace permission-filtered `get_list` with `get_all`. Authorized target-site direct form/API/report/export/print/dashboard tests remain separate.


## PR #124 merged — real Sales User record-filter preflight regression (2026-11-03)

PR #124 merged as [af94b14](https://github.com/MitMike/crm_signals/commit/af94b14038250b75ebc849e424779432d57dee98) from final head [0c7a6bf](https://github.com/MitMike/crm_signals/commit/0c7a6bfc77c3ee9df7189007c0326491906aca76). All four final-head workflows passed: Quality Checks (run 41614477641, configured Python 3.10/3.11/3.12/3.14 jobs and lint/static checks), Security Scanning/Semgrep (41614477907), Bench Integration and E2E (41614477805; Frappe v15 and v16 integration passed, with v16 Playwright passed), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation (41614477749). The real-Frappe Sales User fixture confirmed a linked CRM Signal excluded by the Lead User Permission is not visible while an unlinked signal owned by the same user remains visible. The report returned checked status, restored the original session user and disclosed neither user nor record names.

This is integration-test and documentation evidence only; no runtime behavior, schema, dependency, metric or site configuration changed. The preflight's list-visibility result is code-complete and reference-stack CI-verified, not pilot-verified. On authorized Frappe v16.5 staging, repeat the approved synthetic role/record matrix and separately test direct form, REST API, report, export, print and dashboard paths. D1/D2 native-report reconciliation by currency, D3 Helpdesk SLA, first-install/upgrade, backup/restore/rollback, scheduler/mail/realtime/webhook/worker recovery and desktop/mobile UAT remain release gates.


## PR #125 merged — operator record-visibility acceptance (2026-11-03)

PR #125 merged as [7029747](https://github.com/MitMike/crm_signals/commit/70297474aadb2f4628da2268e10771cd74683e5c). Quality Checks, Security Scanning and the Bench Integration/E2E workflow completed successfully; the Bench runtime selectors were skipped as expected for a documentation-only change. The implementation plan, progress, follow-ups, ADR-095 and changelog now record PR #124's final-head verification. The Administrator Guide, Target-Site Acceptance Kit and Deployment Runbook now include the exact Sales User linked-restricted/unlinked-owned CRM Signal fixture and expected list-visibility result. No runtime behavior or site configuration changed.


## PR #126 opening snapshot — direct document/list API permission regression (2026-11-03)

- **Reviewed main:** `70297474aadb2f4628da2268e10771cd74683e5c` (PR #124 and PR #125 merged; no open PRs or issues at branch creation).
- **Finding:** The existing Sales User fixture and PR #124 cover permission-filtered list visibility through `frappe.get_list` and the preflight. The acceptance guide separately requires direct API reads, but no real-Frappe test invokes the standard single-document/list API wrappers for the same linked-restricted/unlinked-owned pair.
- **Decision (ADR-096):** invoke `frappe.client.get` and `frappe.client.get_list` while switched to the synthetic Sales User. Require denial for the linked CRM Signal, success for the unlinked owned signal, and list output containing only the unlinked signal. Restore the original session user in `finally`.
- **Scope:** integration-test and operator-guide coverage only; no runtime, schema, dependency or site configuration change. Direct HTTP authentication/routing and browser form behavior remain staging checks.
- **Status at opening:** code-complete; final-head Quality/Python, Security, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 validation pending. Not pilot-verified.


### PR #126 first CI triage — Ruff import ordering

- **Observed:** Quality Checks lint failed on head `a5998ec` with Ruff `I001` for the local `frappe.client` import in the integration test helper. The Python 3.11/3.12/3.14 unit jobs passed; Python 3.10 and the Frappe integration/pinned workflows were still running at triage.
- **Decision:** keep the test import-safe when Frappe is not installed by moving the two API wrapper imports into the module's existing guarded `try` block beside `import frappe` and `FrappeTestCase`. Do not suppress or relax Ruff's import-order rule.
- **Correction:** import `frappe.client.get` and `get_list` in the guarded Frappe block; remove the local import from the helper. A fresh final-head matrix is required.
- **Revisit criteria:** if Ruff still reports `I001`, use its exact `--fix` ordering while retaining the `ModuleNotFoundError` fallback; if Bench reports an API wrapper mismatch, inspect the pinned v15/v16 implementation and keep the denied/allowed assertions intact.


### PR #126 second CI triage — guarded import still fails Ruff I001

- **Observed:** Quality Checks on head `97ac553` failed the same Ruff `I001` at the guarded import block (`crm_signals/tests/test_notification_permissions.py:7`); the first attempted correction moved aliased `frappe.client` imports into the existing `try` block but did not satisfy Ruff's ordering rule.
- **Decision:** import the `frappe.client` module itself (`import frappe.client`) inside the existing guarded block and call `frappe.client.get` / `frappe.client.get_list`. This preserves the no-Frappe unit-test fallback and removes the aliased member import ordering ambiguity.
- **Correction:** replace the aliased imports and rerun the full final-head matrix. Do not suppress I001 or relax lint.
- **Revisit criteria:** if I001 persists, retrieve Ruff's exact `--fix` diff from the job or run the pinned Ruff 0.8.1 formatter against the file before another commit; if the integration test fails after lint passes, inspect the exact v15/v16 API result and keep the denied/allowed assertions intact.


### PR #126 review correction — restore session when the initial user switch raises

- **Finding:** final-head CI passed, but review found the API helper called `frappe.set_user(test_user)` immediately before its `try`. If that call changed session state and then raised, the `finally` restoration would not run.
- **Decision:** move the initial user switch inside the existing `try`, so every attempted switch is covered by restoration. Keep the original user captured before the switch and retain the denied/allowed API assertions.
- **Status:** the prior head `30a3890a994a3402b4efdf15732843f86a62b789` passed all four workflows (Quality/Python, Semgrep, Bench v15/v16 + Playwright, pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0). This correction creates a new head and requires a fresh complete matrix before merge.
- **Revisit criteria:** if the new matrix fails, inspect the exact v15/v16 API wrapper and session behavior. Do not move the switch back outside the `try`, bypass permissions, or weaken the linked-denied/unlinked-allowed assertions.


### 2026-11-03 — PR #126 prior-head verification and session restoration correction
- The pre-correction head `30a3890a994a3402b4efdf15732843f86a62b789` passed Quality/Python, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 validation.
- Review found the initial API-test session switch sat outside `try`; move it inside so `finally` restores the original user even if the switch mutates then raises. The corrected head must rerun all four workflows before merge.


### 2026-11-03 — PR #126: direct API permission regression

- Added real-Frappe Sales User coverage for `frappe.client.get` and `frappe.client.get_list` using the linked-restricted/unlinked-owned CRM Signal pair; asserted denial, allowed read, filtered list and session restoration.
- Updated Administrator Guide, Deployment Runbook and Target-Site Acceptance Kit with the direct API acceptance boundary and retained HTTP/browser checks as staging requirements.
- Final-head Quality/Python, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 workflows all passed; merged as `812aa1eb76fbabc0e7f73a664caa72a1e208feb6`.
- Reference-stack CI verification only; not pilot or production acceptance.


### 2026-11-03 — PR #128: reproducible authenticated Sales User HTTP acceptance

- Added copy/paste HTTPS-only curl checks for authenticated identity, linked restricted document denial (403), unlinked owned document read (200) and permission-filtered list visibility.
- Added safe temporary credential/response handling and linked the procedure from the Administrator Guide.
- PR #128 merged as `85c492ea2c84444d7cc45c0d61706736fa972a83`; Quality/Python, Security/Semgrep and documentation-only Bench path-selector checks passed. The embedded Bash passed `bash -n` (ShellCheck unavailable). Must still be executed on authorized Frappe v16.5 staging. Not pilot verification.


### 2026-11-03 — PR #130: browser-session permission regression on Frappe v16 and pinned v16.5

- Added disposable Sales User/User Permission fixtures for a linked restricted CRM Signal and an unlinked owned signal.
- Added Playwright same-origin HTTP assertions for document denial, allowed read and filtered list visibility.
- Extended the pinned Frappe 16.5.0 workflow to run the focused Playwright permission test. The first lint run found a 102-line fixture helper above the 100-line hard limit; split the helper into focused functions without changing the threshold. The next Quality run flagged Prettier formatting; applied the exact formatter diff. Corrected final-head CI pending.


### 2026-11-03 — PR #130 workflow reproducibility correction

- Changed the pinned Frappe 16.5 Playwright dependency step from `npm install` to lockfile-enforced `npm ci --ignore-scripts --no-audit --no-fund`, consistent with Stage 0 and Quality Checks; retained the explicit Chromium install.
- Removed the duplicate ADR-098 decision block and recorded the correction/revisit criteria in the canonical ADR.
- Added a static contract regression that requires the pinned workflow to use `npm ci` before Playwright browser installation and rejects `npm install`.
- Prior head `7bd1837` had Quality and Security passed; Bench v15/v16 and pinned v16.5 were still running. All four workflows must run on the corrected head before merge. Not pilot-verified.

- Masked the pinned Frappe 16.5 E2E Sales User and Employee passwords with GitHub Actions `add-mask` before writing step outputs; added static regression assertions for masking order and lockfile-based npm installation.

- Wrapped the new pinned-workflow static contract test to stay within the configured Python line-length limit; lint enforcement remains unchanged.


### 2026-11-03 — PR #130 pinned Frappe 16.5 Playwright login-route correction (ADR-099)

- Final head 69383d989d7d0d3ee53e973c90a0934f00e81e90 passed Quality/Python, Security/Semgrep and Bench v15/v16 + Playwright. Pinned Frappe 16.5.0 setup, D1/D2/Helpdesk/schema checks, E2E fixture, Python tests and Frappe integration tests passed, but the focused browser test timed out waiting for POST /api/method/login.
- Playwright trace evidence showed the Frappe v16.5 login form successfully submitted POST /login (HTTP 200). The shared helper's route predicate was too narrow.
- Updated the helper to accept exact POST paths /login and /api/method/login, retaining response/session/navigation assertions; added a static regression test. Corrected final-head CI is required. PR #130 remains unmerged pending all four workflows; not pilot-verified.



### 2026-11-03 — PR #130 pinned Frappe 16.5 Sales User identity assertion correction (ADR-100)

- Pinned run 41647478405 completed site setup, preflight, D1/D2, Helpdesk, schema upgrade, E2E fixtures, asset build, Python tests and Frappe integration tests, then failed before permission assertions because the browser role-discovery helper returned an empty array.
- Moved Sales User role validation into the server-side fixture using frappe.get_roles(sales_user) and changed the browser precondition to verify frappe.auth.get_logged_user equals the configured synthetic Sales User.
- Added a static regression guard. All four corrected final-head workflows must pass before merge; no pilot verification is implied.



### 2026-11-03 — PR #130 follow-up: remove stale non-sales role helper reference

- Quality/Python run 41663119127 caught stale currentUserRoles references in the new HTTP permission test and the Employee dashboard test after the helper was removed. The earlier replacement had changed a separate Sales User dashboard test.
- Replaced both remaining role lookups with exact authenticated identity verification; added server-side Employee-only role validation and rejected elevated roles on the Sales User fixture.
- Fresh final-head Quality, Security, Bench v15/v16 + Playwright and pinned Frappe 16.5 workflows are required. No pilot verification is implied.



### 2026-11-03 — PR #130 final HTTP-test identity correction

- Full-file review found the new Sales User HTTP test still called currentUserRoles; replaced it with frappe.auth.get_logged_user and exact email equality.
- The Employee dashboard test also verifies its exact synthetic identity. Server-side fixture preparation enforces Sales User and Employee role boundaries.
- All four final-head workflows must pass before merge. No pilot verification is implied.



### 2026-11-03 — PR #130 corrected head queued for final verification

- Corrected head fd855ae056c81b16defa1eac6085ab481ef08ac9 removes the final currentUserRoles reference, verifies Sales User and Employee browser session identities with frappe.auth.get_logged_user, and validates role boundaries server-side.
- Fresh Quality run 41663665399, Security run 41663665370, Bench v15/v16 run 41663665401 and pinned Frappe 16.5.0 run 41663665390 were queued; Security had started. Await all four final-head results before merge.

### 2026-11-03 — PR #130 deterministic non-sales E2E role correction (ADR-101)

- Final head `7525c1521835e93245faf5840c0af1c47f9d590b` passed Quality `41663853566` and Security `41663853347`, but pinned Frappe 16.5.0 `41663853279` and supported v16 Bench `41663853266` failed before Playwright at `E2E Employee role boundary is invalid` in `crm_signals/ci.py:176`.
- Site setup, effective-user preflight, D1/D2, Helpdesk and schema-upgrade steps passed. The CI log did not print the effective role set; no specific built-in role filtering cause is claimed.
- Replaced the built-in Employee-role dependency with a dedicated CI-only `CRM Signals E2E Non-Sales` role, explicitly enabled for Desk access; added a static regression guard. Sales User permission assertions remain unchanged.
- Commits: `eb55ca5` and `1e7c911`. Fresh final-head four-workflow verification required; PR remains unmerged and not pilot-verified.

### 2026-11-03 — PR #130 merged — browser-session Sales User HTTP permission boundary

- PR #130 merged as `2b697b4d37a12b2e339bcf680ff808f23b97850f` from final tested head `42f8a38e751977e21168869c4010fcce901309ac`.
- All four final-head workflows passed: Quality/Python `41668745943`, Security/Semgrep `41668745937`, Bench v15/v16 + Playwright `41668746054`, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 `41668745681`. The pinned job's focused Playwright E2E step completed successfully.
- Added a deterministic CI-only non-sales Desk role and exact browser identity checks; preserved linked restricted 403, unlinked owned 200 and list-only-unlinked expectations. No production runtime, schema, dependency or site configuration changed. Reference-stack CI-verified, not pilot-verified.

### 2026-11-03 — PR #131 opening — direct CRM Signal form-load permission regression

- Add the `Sales User CRM Signal form permission boundary` Playwright test for the actual Desk route `/app/crm-signal/<name>`, observing Frappe's `frappe.desk.form.load.getdoc` GET request under the synthetic Sales User.
- Require 403/no restricted message for the linked signal and 200/expected message for the unlinked owned signal; include both HTTP API and direct-form tests in the pinned Frappe 16.5.0 Playwright selector.
- Add a static regression guard and document the target-site form check. No production runtime, schema, dependency or site configuration changes.
- Code-complete on the focused branch; final-head CI pending. Not pilot-verified.

### 2026-11-03 — PR #131 reproducible Bench E2E install correction (ADR-103)

- Review found the supported Frappe v15/v16 Bench E2E workflow still used `npm install` while the pinned v16.5 workflow used `npm ci`.
- Replaced the supported-lane command with `npm ci --ignore-scripts --no-audit --no-fund`; extended static checks to require lockfile installation and password masking before output propagation in both workflows.
- No package versions or lockfile changed. Final-head CI pending; not pilot verification.

### 2026-11-03 — PR #131 static guard correction

- The first Quality/Python run failed one Python 3.11 static assertion because the guard expected the bare `frappe.desk.form.load.getdoc` string while the spec correctly matches the full `/api/method/frappe.desk.form.load.getdoc` pathname.
- Corrected the static assertion only. The failure occurred before runtime or browser permission tests; fresh final-head CI is required. No permission expectations changed.

### 2026-11-03 — PR #131 second static/formatting correction

- The next Quality run exposed a second static guard mismatch because the direct form route is a TypeScript template literal, and Prettier reported two exact formatting differences in the new Playwright spec.
- Updated the guard to match the actual route syntax and applied the Prettier output. No runtime or permission assertion failed; fresh final-head CI is required.


### 2026-11-03 — PR #131 merged — direct CRM Signal form-load permission regression

- Added a Sales User Playwright check for the actual Desk form loader GET request: linked-restricted CRM Signal returns 403 without exposing its message; unlinked-owned CRM Signal returns 200 with its expected message.
- Ran the new direct-form test in the supported Frappe v16 suite and pinned Frappe 16.5.0 lane; retained Frappe v15 Bench integration coverage.
- Standardized both Bench E2E workflows on lockfile-enforced `npm ci` and masked generated E2E passwords before GitHub Actions step-output propagation.
- Final head `a72ebffbae116adf06830473bb15d764a169651b` passed Quality/Python `41676858036`, Security/Semgrep `41676862616`, Bench v15/v16 + Playwright `41676858619` (18 Playwright tests passed on v16), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 `41676858020` (3 focused Playwright tests passed).
- Merged as `08f269cdfaedc58fd4ce396c823d589e7dd3481b`. Reference-stack CI verification only; live API-token, direct-form, report/export/print/dashboard and production acceptance remain outstanding.


### 2026-11-03 — PR #133 opening — synthetic Sales User API-token permission regression

- Add a disposable Frappe API key/secret for the synthetic Sales User and test identity plus linked-denied/unlinked-allowed/list-only-unlinked outcomes through an explicit token Authorization header.
- Keep the API secret in a mode-0600 runner temp file, mask both credentials before GitHub step outputs, delete the file on step exit, and use Node fetch outside Playwright page tracing with redirects disabled.
- Run the token E2E in supported Frappe v16 and pinned Frappe 16.5.0; retain Frappe v15 Bench integration coverage.
- Code-complete on the focused branch; final-head CI pending. No production runtime or schema change. Not pilot-verified.

- Review hardening: the API-token E2E now asserts a linked-restricted 403 body omits the synthetic signal message and the unlinked-owned 200 body includes its expected name and message; a static contract test protects both checks.
- The initial head `687233baa1e3a4a747c01124b35ad13b188ee760` passed Quality/Python and Security while both integration workflows were in progress. The review commit supersedes those runs; require all four workflows to pass on the new final head.

- Hardened the token test parser to retain non-JSON response text, preventing an HTML/plain-text error body from bypassing the restricted-message non-disclosure assertion. Added a static guard for the fallback.
- Expanded the target-site acceptance kit with safe API-key/secret generation, silent entry, and post-test rotation/revocation instructions for the dedicated synthetic Sales User.

- Final code head `b9f72471d7cd7102023454cfef3ca491e950d5af` passed Quality/Python, Security/Semgrep, Bench v15/v16 + Playwright (19 tests on v16) and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 (4 Playwright tests). The operator kit now documents API-key generation, silent entry and post-test rotation/revocation; the smoke script disables shell xtrace before handling secrets.

### 2026-11-03 — PR #133 merged — cookie-independent Sales User API-token permission regression

- PR #133 merged as `b2f1d07db7fdf8b6cafdaced7b0aaeefc74f9397` from final PR head `9a1a19c207e9bdff6cfb8df445bacb390d9478b6`; code head `b9f72471d7cd7102023454cfef3ca491e950d5af` contains the implementation and E2E test.
- All four fresh final-head workflows passed: Quality/Python `41685961000`, Security/Semgrep `41685960990`, Bench v15/v16 + Playwright `41685961276` (19 tests on v16), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 `41685961014` (4 focused Playwright tests).
- The operator kit covers API credential generation, silent entry, HTTPS/no-redirect handling and post-test rotation/revocation. CI evidence is reference-stack only; authorized target-site transport and permission acceptance remain open.


### 2026-11-03 — PR #135 opening — Sales User REST resource API permission regression

- Add cookie-independent API-token E2E for Frappe's standard `/api/resource/CRM%20Signal/{name}` and collection endpoints using the disposable Sales User credentials from PR #133.
- Require linked-restricted 403 without restricted message disclosure, unlinked-owned 200 with exact record name/message, and list-only-unlinked; preserve non-JSON response bodies and reject redirects.
- Extend the target-site acceptance script with the same REST resource single-document and collection checks.
- Code-complete on a focused branch; final-head CI pending. No production runtime, schema, dependency or site-configuration change. Not pilot-verified.

### 2026-11-04 — PR #135 merged — Sales User REST resource permission regression

- Merged as `81d70410f0f81124ae468c1d929caefd1610fd9e` from tested head `ae6b7e408664a3b6f885c1c18ba9fc3d18c73890`.
- All four required final-head workflows passed: Quality/Python `41690041480`, Security/Semgrep `41690041431`, Bench v15/v16 + Playwright `41690041398`, and pinned Frappe 16.5.0 `41690041432`.
- Standard REST resource single-document and collection permission checks are reference-stack CI-verified. Target-site API-token transport, role configuration and full report/export/print/dashboard acceptance remain open; not pilot-verified.

### 2026-11-04 — PR #137 merged — CRM Signal print permission boundary

- Merged as `9b2af7f90652927ca8497777e099cd3e742ce2f2` from final tested head `a7d1f48626ae0116a300a7b89404921bdda5552b`.
- Fixes a record-level disclosure path in Frappe's read-or-print gate by requiring the existing row-level readable relationship for CRM Signal print in addition to the DocType print grant.
- All final-head checks passed: Quality/Python `41698694186`, Security `41698694333` and `41698685514`, Bench v15/v16 + Playwright `41698694301`, and pinned Frappe 16.5.0 `41698694356`.
- v15/v16 unit and integration coverage passed; v16 ran 21 Playwright tests; pinned v16.5.0 ran 6 Playwright tests. Reference-stack CI-verified, not pilot-verified.


### 2026-11-04 — PR #139 opening — Sales User Report View and CSV export permission regression

- Added a cookie-independent API-token E2E for Frappe's standard `frappe.desk.reportview.get_list` and `frappe.desk.reportview.export_query` endpoints using the existing synthetic Sales User and linked-restricted/unlinked-owned CRM Signal pair.
- Require Report View results to contain only the unlinked owned record; require CSV export to contain the unlinked record name/message and exclude the restricted record name/message.
- Added a static regression guard and updated the Administrator Guide and Target-Site Acceptance Kit. ADR-107 records why Report View and export need endpoint-specific coverage.
- Scope is CI E2E/static tests and operator documentation only; no production runtime, DocType role grant, schema, dependency or site configuration change. Final-head CI pending; not pilot-verified.

- PR #139 CI triage: initial Quality run `41708443112` identified only Prettier formatting differences in the new E2E test; applied the exact formatter output in `c75dae2`. Python 3.12 passed on the superseded head. Corrected-head full matrix required; not pilot-verified.

- PR #139 corrected-head CI update: Quality/Python `41708655615` and Security/Semgrep `41708655564` passed on `4fa1c93075235a6b19fdec7228df70aa044f32d3`; Bench v15/v16 + Playwright `41708655538` is queued and pinned Frappe 16.5.0 `41708655821` is running. Do not merge until both integration lanes pass.


### 2026-11-04 — PR #139 merged — Sales User Report View and CSV export permission regression

- PR #139 squash-merged as `ac2d83d823bdcad46fe84ccd5d2b8954c0b0d959` from final tested head `2e30fd02a1074e26adbf1d0de1f4fb715e2d837a`.
- All four final-head workflows passed: Quality/Python [41709078949](https://github.com/MitMike/crm_signals/actions/runs/41709078949), Security/Semgrep [41709078877](https://github.com/MitMike/crm_signals/actions/runs/41709078877), Bench v15/v16 + Playwright [41709078919](https://github.com/MitMike/crm_signals/actions/runs/41709078919), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 [41709078884](https://github.com/MitMike/crm_signals/actions/runs/41709078884).
- The token-authenticated Report View query returned only the unlinked-owned CRM Signal; CSV export included the permitted record and excluded the linked-restricted record name/message. Frappe v15 Bench integration coverage was retained.
- Reference-stack CI-verified; authorized Frappe 16.5 staging role/transport acceptance remains open. Not pilot-verified.


### 2026-11-04 — PR #141 opening — direct dashboard API permission boundaries

- Added a token-authenticated Sales User regression for crm_signals.api.get_dashboard_data, requiring the unlinked-owned CRM Signal and excluding the linked-restricted record/message.
- Extended the dedicated non-sales E2E to call the Executive Compass API directly and require unavailable source metrics without source read grants, and to require HTTP 403 from the CRM Signals dashboard API without CRM Signal read permission.
- Added static regression guards and updated the Administrator Guide and Target-Site Acceptance Kit. ADR-108 records the effective-user API permission decision.
- Test/documentation scope only; no production runtime, role grant, schema, dependency or site configuration change. Final-head CI pending; not pilot-verified.
- CI triage on superseded head: Quality/Python `41717036495` passed all four Python versions but identified only Prettier formatting differences; applied exact formatter output in `2b40f63`. Security/Semgrep `41717036375` passed. Fresh final-head matrix required.
- A second superseded-head Quality run `41717358086` found one remaining extra blank line; removed it in `85ed8d8`. Python 3.10–3.14 passed and Security/Semgrep `41717358293` passed. Bench/pinned results were not final-head evidence and must be repeated.


### 2026-11-04 — PR #141 merged — direct dashboard API permission boundaries

- PR #141 squash-merged as `70aa4d8953cc8a69d1317aad1c72654f05a1b29e` from final tested head `cbd69b80607473b65c4619b2495568be70fb1750`.
- All four final-head workflows passed: Quality/Python [41717651648](https://github.com/MitMike/crm_signals/actions/runs/41717651648), Security/Semgrep [41717651238](https://github.com/MitMike/crm_signals/actions/runs/41717651238), Bench v15/v16 + Playwright [41717651601](https://github.com/MitMike/crm_signals/actions/runs/41717651601), and pinned Frappe 16.5.0 / ERPNext / Helpdesk [41717651416](https://github.com/MitMike/crm_signals/actions/runs/41717651416).
- The Sales User API-token test verifies dashboard row filtering for linked-restricted versus unlinked-owned signals. The non-sales test directly verifies Executive Compass source availability and CRM Signals dashboard HTTP 403 without read permission. Frappe v15/v16 coverage is retained.
- Reference-stack CI-verified; authorized Frappe 16.5 staging API/role acceptance remains open. Not pilot-verified.


### 2026-11-04 — PR #143 opening — non-sales dashboard API token acceptance smoke

- Extended the target-site HTTPS smoke with a separate non-sales API token, exact identity verification, CRM Signals dashboard HTTP 403/no-disclosure assertion, and Executive Compass source-unavailable assertions.
- Protected both token pairs with silent prompts, separate temporary curl config files, redirect rejection, cleanup and rotation/revocation instructions.
- Added a static regression guard and ADR-109. Documentation/test-only; no runtime permissions or site roles changed. Final-head verification and merge are recorded below; not pilot-verified.


### 2026-11-04 — PR #143 merged — non-sales dashboard API token acceptance smoke

- PR #143 squash-merged as `f75dd241a2ca30505517bb2fd259e2ec62648c50` from final tested head `6dd697c8a124244299599ec972b19d153a0cc1c2`.
- All four final-head workflows passed: Quality/Python [41728280197](https://github.com/MitMike/crm_signals/actions/runs/41728280197), Security/Semgrep [41728280109](https://github.com/MitMike/crm_signals/actions/runs/41728280109), Bench v15/v16 + Playwright [41728279918](https://github.com/MitMike/crm_signals/actions/runs/41728279918), and pinned Frappe 16.5.0 / ERPNext / Helpdesk [41728280316](https://github.com/MitMike/crm_signals/actions/runs/41728280316).
- The target-site operator script now tests distinct Sales User and non-sales API-token identities, the non-sales CRM Signals HTTP 403/no-disclosure boundary, and Executive Compass source unavailability without read grants. Secret handling uses silent prompts, separate restrictive curl config files, no redirects, cleanup and rotation/revocation instructions.
- Documentation/static-test scope only. Reference-stack CI-verified; authorized Frappe 16.5 staging execution remains outstanding. Not pilot-verified.


### 2026-11-04 — PR #145 merged — split permission acceptance matrix

- PR #145 squash-merged as `ed9c22c25d0a885bd351f396c11eadf1cdbac3c6` from final tested head `c480eedb0ef6c2a67bc9ce23ac326ab92c4d7a89`.
- All four final-head workflows passed: Quality/Python [41730709519](https://github.com/MitMike/crm_signals/actions/runs/41730709519), Security/Semgrep [41730709486](https://github.com/MitMike/crm_signals/actions/runs/41730709486), Bench v15/v16 + Playwright [41730709475](https://github.com/MitMike/crm_signals/actions/runs/41730709475), Pinned Frappe 16.5.0 / ERPNext / Helpdesk [41730709472](https://github.com/MitMike/crm_signals/actions/runs/41730709472).
- Quality passed lint/static and Python 3.10, 3.11, 3.12 and 3.14. Bench v15/v16 integration passed, v16 Playwright passed, and pinned Frappe 16.5.0 / ERPNext / Helpdesk integration plus Playwright passed.
- The independent persona/path matrix is reference-stack CI-verified. Actual Sales User, Sales Manager, System Manager, non-sales and disabled-user results remain blank until authorized Frappe 16.5 staging execution. Not pilot-verified.


### 2026-11-04 — PR #147 opening — daily digest recipient eligibility

- Added unit and real-Frappe Bench regressions for digest-specific recipient resolution: role and explicit recipients are deduplicated; only enabled System Users are returned; disabled role members, disabled explicit recipients, Website Users, Guest and unknown addresses are excluded.
- Updated the daily digest validation mapping and target-site acceptance kit. ADR-111 records that digest eligibility must be tested independently from realtime recipient routing.
- Test/documentation scope only; no runtime behavior changed. The initial Bench matrix exposed a role-less explicit-recipient fixture that was not proven to persist as a Desk System User; the fixture now uses a non-Sales-Manager Sales User role and asserts saved user type/email mapping. Final-head CI rerun pending; not pilot-verified.

### 2026-11-04 — PR #147 merged — daily digest recipient eligibility

- PR #147 squash-merged as `5f3cb6a5535448ee91da8428460b268e9f60c1db` from final tested head `193a7e727b316b5c0187ec812d3ccc144b2209c2`.
- All four final-head workflows passed: Quality/Python [41752787424](https://github.com/MitMike/crm_signals/actions/runs/41752787424), Security/Semgrep [41752787359](https://github.com/MitMike/crm_signals/actions/runs/41752787359), Bench v15/v16 + Playwright [41752787379](https://github.com/MitMike/crm_signals/actions/runs/41752787379), and pinned Frappe 16.5.0 / ERPNext / Helpdesk 1.28.0 [41752787499](https://github.com/MitMike/crm_signals/actions/runs/41752787499).
- Recipient eligibility tests prove deduplication, explicit non-manager System User inclusion, and exclusion of disabled, Website, Guest and unknown recipients. No production recipient filter changed. Reference-stack CI-verified; target-site digest/mail acceptance remains open. Not pilot-verified.

### 2026-11-04 — PR #148 opening — digest queue failure isolation and Error Log privacy

- Review found digest queue failure logs exposed recipient email addresses in the title and raw exception text/traceback in the message. The runtime now records a generic title and exception class only.
- Added a real-Frappe Bench regression for one-recipient failure isolation, successful queueing of later recipients, retry of only the failed recipient on the next run, and log redaction.
- Updated the digest contract, Administrator Guide, target-site acceptance, ADR-112, plan, progress, follow-up register and changelog. Code-complete; final-head CI pending; not pilot-verified.


### 2026-11-04 — PR #148 merged — daily digest failure isolation and Error Log privacy

- PR #148 squash-merged as [a63866f](https://github.com/MitMike/crm_signals/commit/a63866f99fd9f67c5c680e57987abf47c1247377) from exact tested head [c4c237b](https://github.com/MitMike/crm_signals/commit/c4c237b69ed45657c62e6702b185904a00c92a16).
- The digest queue failure path now records a generic Error Log title and exception class only; recipient email addresses, raw exception messages and tracebacks are not persisted. A real-Frappe Bench regression verifies one-recipient failure does not block later recipients, only the failed recipient is retried on the next same-date run, and captured logs contain neither the destination address nor raw exception text.
- All four final-head workflows passed: Quality/Python [41760017843](https://github.com/MitMike/crm_signals/actions/runs/41760017843), Security/Semgrep [41760017858](https://github.com/MitMike/crm_signals/actions/runs/41760017858), Bench v15/v16 + Playwright [41760017850](https://github.com/MitMike/crm_signals/actions/runs/41760017850), and pinned Frappe 16.5.0 / ERPNext / Helpdesk 1.28.0 [41760017879](https://github.com/MitMike/crm_signals/actions/runs/41760017879). Python 3.10/3.11/3.12/3.14, lint/static, Semgrep, both Bench integration/validation lanes and pinned target validation passed.
- Reference-stack CI-verified only. Authorized Frappe 16.5 staging scheduler, recipient and mail-provider acceptance remains open; not pilot-verified.


### 2026-11-04 — PR #152 merged — release-state baseline reconciliation

- PR #152 squash-merged as [508c432](https://github.com/MitMike/crm_signals/commit/508c432d8bf39108367a42664112db55c7f87435); reviewed-main references in the implementation plan, progress register and follow-up register now point to the merged main baseline.
- Post-merge main Quality [41785092281](https://github.com/MitMike/crm_signals/actions/runs/41785092281), Security [41785092277](https://github.com/MitMike/crm_signals/actions/runs/41785092277) and Bench [41785092279](https://github.com/MitMike/crm_signals/actions/runs/41785092279) passed. Documentation-only change detection skipped full integration execution; supported-version integration/validation jobs passed.
- No application runtime, schema, permission, dependency or generated asset changed. No pilot verification is implied.


### 2026-11-04 — README webhook command correction (PR #154)

- Fixed the webhook `curl` example so its URL, authorization header, content type and form fields are passed as one shell command.
- Added a static regression test to prevent the multiline example from splitting into separate commands.
- The endpoint, authentication requirements and payload are unchanged. Target-site webhook/TLS acceptance remains open.


### README webhook operator example — PR #154 (merged and CI-verified as `00715e0`)

- Correct the README multiline `curl` example so the URL, authorization header, content type and form fields execute as one command; the endpoint, token authentication and payload are unchanged.
- Final head `fcbca00` passed Quality/Python 3.10–3.14, Security/Semgrep, Frappe v15/v16 Bench + Playwright, and pinned Frappe 16.5.0 / Helpdesk 1.28.0. Squash-merged as `00715e06529aebc62770d8c5b283c142bf4c9f08`.
- Post-merge main Quality and Security passed; Bench v15/v16 integration was still running at the latest review. No live webhook, TLS, credential or pilot acceptance is implied.


### Operator guide webhook and acceptance-script regression coverage — PR #155 (merged and CI-verified as `e2cb38e`)

- Extend the shell-continuation regression to both README and Administrator Guide webhook examples.
- Add a non-executing bash -n syntax check for the credentialed target-site permission smoke block in the acceptance kit.
- Final head `f12db6128f09ff7c70f3ba957b6ab718c842c03f` passed Quality/Python, Security/Semgrep, Frappe v15/v16 Bench + Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. Squash-merged as `e2cb38efb2d39ae6260116f35dbeb4d953f5cdb5`.
- No runtime, schema, permission policy, dependency or site configuration changed. CI did not execute credentials or send site requests; target-site and pilot acceptance remain open.


### PR #155 post-merge main verification

- Main Quality [41832550271](https://github.com/MitMike/crm_signals/actions/runs/41832550271) and Security [41832550353](https://github.com/MitMike/crm_signals/actions/runs/41832550353) passed after merge `e2cb38efb2d39ae6260116f35dbeb4d953f5cdb5`.
- Main Bench [41832550281](https://github.com/MitMike/crm_signals/actions/runs/41832550281) was still running at review; v15 had reached D1/D2 aggregate-value verification and v16 was creating the site/installing apps. Do not record the main Bench run as passed until it completes.


### Operator shell-example syntax coverage — PR #157 (merged and CI-verified as `05a0045`)

- Parse every fenced Bash/sh/shell example in README.md, docs/ADMIN_GUIDE.md, docs/DEPLOYMENT_RUNBOOK.md and docs/TARGET_SITE_ACCEPTANCE.md with `bash -n`; commands, credentials and site requests are never executed.
- Exact tested head `6e719f7` passed Quality [41843318924](https://github.com/MitMike/crm_signals/actions/runs/41843318924), Security [41843318929](https://github.com/MitMike/crm_signals/actions/runs/41843318929), Bench v15/v16 + Playwright [41843319089](https://github.com/MitMike/crm_signals/actions/runs/41843319089), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 [41843319094](https://github.com/MitMike/crm_signals/actions/runs/41843319094). Squash-merged as `05a0045`.
- Post-merge main Quality [41844574383](https://github.com/MitMike/crm_signals/actions/runs/41844574383), Security [41844574353](https://github.com/MitMike/crm_signals/actions/runs/41844574353) and Bench [41844574376](https://github.com/MitMike/crm_signals/actions/runs/41844574376) passed. This is operator syntax CI verification only; no target-site or pilot acceptance is implied.


- **PR #159:** strengthen the Frappe 16.5 target-site permission smoke to verify restricted CRM Signal messages are not disclosed through denied RPC/REST, Report View or CSV export, and that the permitted synthetic message remains visible on allowed paths. Parse-only CI coverage; no runtime or permission change.


- **PR #159 merged:** [bfc4886](https://github.com/MitMike/crm_signals/commit/bfc4886382877ce4014ac2ef0d2cb0c64000b4c1) strengthens target-site message-level privacy assertions. Exact final-head Quality [41851046486](https://github.com/MitMike/crm_signals/actions/runs/41851046486), Security [41851046368](https://github.com/MitMike/crm_signals/actions/runs/41851046368), Bench v15/v16 + Playwright [41851046485](https://github.com/MitMike/crm_signals/actions/runs/41851046485), and pinned Frappe 16.5.0 [41851046388](https://github.com/MitMike/crm_signals/actions/runs/41851046388) passed. The credentialed target-site script remains parse-only in CI; no pilot verification is implied.
