# CRM Signals — Implementation Plan (Frappe / ERPNext v15 & v16)

## Scope and baseline
The supplied archive is a **CRM Signals extension**, not a complete CRM. The plan hardens and completes signal capture, event-generated signals, Desk notifications, and the scheduled sales digest. Lead/contact management, customer lifecycle, sales pipeline ownership, marketing automation, campaigns, omnichannel inbox, and full CRM analytics are out of scope unless separately approved.

## Slices and exit criteria

| Slice | Goal | Main work | Exit criteria | Priority |
|---|---|---|---|---|
| 0. App discovery and packaging | Make Pilot identify and install the repository | Root pyproject metadata, bounded dependencies, package/module layout | Pilot resolver finds crm_signals; editable package install succeeds; DocType path matches module |
| 1. Webhook security & validation | Remove anonymous write path | Authenticated integration user; strict payload validation; remove permission bypass/manual commit; safe response | Guest rejected; authorized call succeeds; invalid payload rejected |
| 2. Event correctness | Generate accurate signals | Resolve Quotation party using quotation_to; correct Lead/Customer links; confirm Opportunity statuses; prevent duplicates | Fixtures prove correct links and intended transitions |
| 3. Signal data model & permissions | Govern records | Validate required fields and party exclusivity; role and record-level permissions; safe read-state mutation; idempotency metadata | Permission tests for Sales User/Manager/System Manager |
| 4. Real-time delivery | Reliable, scoped notifications | Resolve recipients from related document owner and active ToDo assignments; minimal payload; publish after commit | Only related enabled users receive notification; record read permissions verified |
| 5. Daily digest | Correct manager summary | Verify Lead status/inactivity semantics; quote expiry window; escape HTML; enabled manager recipients; configurable settings | Tests cover counts, expiry, escaping, recipients |
| 6. UX & operations | Make signals actionable | Related-document links, unread count, filters, mark-read workflow, runbook | Desk smoke test and workflow documented |
| 7. Observability & release | Ship safely | Logs, failure isolation, migration/rollback, compatibility matrix, tagged release | Clean install/upgrade/uninstall on pinned v15/v16 |

## Slice 0 implementation
- Add root `pyproject.toml` with `[project].name = "crm_signals"`.
- Declare bounded Frappe and ERPNext dependency ranges under `[tool.bench.frappe-dependencies]`.
- Keep `crm_signals/hooks.py` at the repository path expected by Pilot.
- Put the `Crm Signals` module and its DocType at `crm_signals/crm_signals/`.
- Check the repository discovery contract and editable package install in CI.

## Remaining slices
### Slice 1 — webhook security
- Authenticated API key/secret with a dedicated integration user.
- No Guest access, permission bypass, arbitrary realtime recipient, or manual commit.
- Strict type, length and linked-record validation.
- HTTPS, token rotation, secret management and gateway rate limits.

### Slice 2 — event correctness
- Map Quotation `quotation_to` and `party_name` into exactly one matching party Link.
- Confirm ERPNext Opportunity fields and status options on v15/v16.
- Add idempotency where duplicate event delivery is possible.

### Slice 3 — data model and authorization
- Restrict Sales User list/document access to linked Lead/Customer owners and active assignees.
- Verify list, report, export, direct-document and Desk workflows.

### Slice 4 — real-time delivery
- Resolve users from related Lead/Customer owner and active ToDo assignments.
- Publish to per-user rooms only and read full signal data through permission-checked APIs.

### Slice 5 — digest
- Confirm Lead inactivity meaning and quote status/expiry semantics.
- Keep HTML-escaped names and document IDs.
- Filter to enabled System Users, deduplicate recipients and configure digest thresholds.

### Slice 6 — UX
- Add permission-safe related-document links, unread count, filters and server-enforced read state.

### Slice 7 — release
- Run clean install, migrate, scheduler, hooks, realtime and uninstall on v15/v16.
- Record tested versions and publish rollback/runbook.

## Acceptance tests
- Pilot resolves app name from root pyproject and finds crm_signals/hooks.py.
- Editable package install succeeds.
- DocType metadata is found under the Crm Signals module.
- Guest webhook rejected; authenticated integration user succeeds.
- Invalid payloads and invalid Lead/Customer links are rejected.
- Related owners/active assignees receive realtime alerts; unrelated users do not.
- List and direct-document access enforce the same parent-party restrictions.
- Quotation/Opportunity events create the intended records exactly once.
- Digest counts, expiry filters, HTML escaping and recipients are correct.
- Clean install/migrate/uninstall succeeds on Frappe/ERPNext v15 and v16.

## Remaining verification
No live Frappe bench/site was available in this session. The declared ranges express intended compatibility only. End-to-end v15/v16 testing is still required.
