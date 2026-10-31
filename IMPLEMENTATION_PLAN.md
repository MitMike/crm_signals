# CRM Signals — Implementation Plan (Frappe / ERPNext v15 & v16)

## Scope and baseline
The supplied archive is a **CRM Signals extension**, not a complete CRM. The plan hardens and completes signal capture, event-generated signals, Desk notifications, and the scheduled sales digest. Lead/contact management, customer lifecycle, sales pipeline ownership, marketing automation, campaigns, omnichannel inbox, and full CRM analytics are out of scope unless separately approved.

This is a source review, not a live-site validation. No Frappe/ERPNext v15 or v16 sites, test databases, or credentials were available.

## Slices and exit criteria

| Slice | Goal | Main work | Exit criteria | Priority |
|---|---|---|---|---|
| 0. Reproducible baseline | Make app installable/testable | Package metadata, install docs, CI matrix, smoke tests | App imports; DocType JSON validates; CI on v15/v16 | P0 |
| 1. Webhook security & validation | Remove anonymous write path | Authenticated integration user; strict payload validation; remove permission bypass/manual commit; safe response | Guest rejected; authorized call succeeds; invalid payload rejected | P0 |
| 2. Event correctness | Generate accurate signals | Resolve Quotation party using `quotation_to`; correct Lead/Customer links; confirm Opportunity statuses; prevent duplicates | Fixtures prove correct links and intended transitions | P0 |
| 3. Signal data model & permissions | Govern records | Validate required fields and party exclusivity; role permissions; safe read-state mutation; idempotency metadata | Permission tests for Sales User/Manager/System Manager | P1 |
| 4. Real-time delivery | Reliable, scoped notifications | Resolve recipients from assignment/owner/roles; minimal payload; publish after commit | Only intended users receive notification after insert commits | P1 |
| 5. Daily digest | Correct manager summary | Verify Lead status/inactivity semantics; quote expiry window; escape HTML; enabled manager recipients; configurable settings | Tests cover counts, expiry, escaping, recipients | P1 |
| 6. UX & operations | Make signals actionable | Related-document links, unread count, filters, mark-read workflow, runbook | Desk smoke test and workflow documented | P2 |
| 7. Observability & release | Ship safely | Logs, failure isolation, migration/rollback, compatibility matrix, tagged release | Clean install/upgrade/uninstall on pinned v15/v16 | P2 |

## Detailed implementation tasks

### Slice 0 — baseline
- Add app packaging metadata consistent with bench conventions.
- Validate DocType JSON and Python syntax in CI.
- Add pytest tests and a Frappe test harness for database behavior.
- Define GitHub Actions matrix for supported Python/Frappe versions. Do not claim tested versions until jobs pass.

### Slice 1 — webhook security
- Do not allow Guest access. Use a dedicated integration user with minimum role/permission.
- Remove `ignore_permissions=True` from the public API path.
- Never call `frappe.db.commit()` in the request handler; use framework transaction boundaries and after-commit realtime publishing.
- Validate signal type/priority, message length, Lead/Customer existence, and party exclusivity.
- Do not let the request choose arbitrary notification recipients.
- Document TLS, token rotation, secret storage, and gateway rate limiting.

### Slice 2 — event correctness
- A submitted Quotation uses `quotation_to` and `party_name`; set exactly one matching Link field.
- Confirm ERPNext Opportunity party fields and status options against target v15/v16 schemas.
- Publish minimal payload after commit.
- Add idempotency where duplicate event delivery is possible.

### Slice 3 — data model and authorization
- Enforce signal policy server-side.
- Explicitly decide whether unassociated system signals are allowed.
- Review Sales User, Sales Manager, and System Manager permissions.
- Prevent untrusted callers from setting owner/read state/recipient fields.

### Slice 4 — realtime delivery
- Define recipient resolution from assignment, document ownership, or configured teams.
- Avoid global broadcasts of customer-sensitive content.
- Fetch full signal detail through permission-checked APIs.

### Slice 5 — digest
- Verify Lead statuses and define whether inactivity means no modification or no communication.
- Confirm quote status and expiry semantics.
- Escape party names and document IDs in generated HTML.
- Exclude disabled/system users and deduplicate recipients.
- Make threshold and send time configurable; record execution outcomes.

### Slice 6 — UX
- Add permission-safe links to related records.
- Add unread, priority, type, and party filters.
- Make read/unread mutation server-enforced.

### Slice 7 — release
- Test install, migrate, scheduler registration, hooks, realtime, and uninstall on clean v15/v16 sites.
- Record tested framework/ERPNext/Python/bench versions.
- Publish runbook, rollback steps, webhook example, and security notes.

## Acceptance test matrix

| Area | Test | Expected result |
|---|---|---|
| API auth | Guest request | 401/403; no signal |
| API auth | Integration user with permission | One signal inserted |
| Validation | Unknown type/priority | Validation error; no row |
| Validation | Missing or oversized message | Validation error; no row |
| Validation | Invalid Lead/Customer | Validation error; no row |
| Validation | Both Lead and Customer set | Rejected |
| Notification | Caller attempts arbitrary recipient | No caller-controlled recipient honored |
| Quotation | Submitted high-value quote to Customer | Customer only |
| Quotation | Submitted high-value quote to Lead | Lead only |
| Quotation | Below threshold/draft quote | No signal |
| Opportunity | Status unchanged | No signal |
| Opportunity | Configured status transition | One correctly linked signal |
| Digest | Old vs recent Leads | Only qualifying records counted |
| Digest | Expiring/non-expiring/cancelled quotes | Only intended quotes included |
| Digest | HTML metacharacters in party name | Escaped output |
| Digest | No eligible managers | No crash/no email |
| Realtime | Transaction rollback | No notification |
| Compatibility | Clean install/migrate on v15/v16 | No errors; hooks/tasks/assets registered |

## Current progress
- [x] Baseline source audit and implementation plan
- [x] Initial webhook hardening (live permission/rate-limit tests open)
- [x] Initial Quotation/Opportunity party-link improvements (fixtures and status decision open)
- [ ] Complete model/permission hardening
- [ ] Explicit realtime recipient resolution
- [x] Digest HTML safety and removal of guessed Lead status filter (live semantics open)
- [x] Security and implementation documentation
- [ ] Automated CI and live v15/v16 acceptance
