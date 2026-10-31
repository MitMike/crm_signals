# CRM Signals — Settings and core reliability

**Status:** Implementation in progress.
**Scope:** Singleton configuration, starter presets, event identity, external ingestion deduplication and digest delivery safety.

## Goals

- Move business defaults from source constants into a validated System Manager-only singleton.
- Provide starter profiles that administrators can apply and then customise.
- Never assume the Company's currency is INR.
- Generate source-event identities that remain stable across retries.
- Ensure repeated webhook requests do not create duplicate signal records when an event ID is supplied.
- Make daily digest timing and recipients configurable and avoid duplicate queuing for one site-local date.
- Keep failures in ancillary notification delivery from breaking Quotation/Opportunity saves.

## Settings contract

The singleton is `CRM Signals Settings`. It includes a master switch, external ingestion switch, Quotation signal switch and threshold/currency, Opportunity signal switch and exact trigger statuses, digest switch/time/stale window, optional additional enabled System User recipients, and last-queued diagnostics.

The preset profiles are Balanced, Sales Focused and Executive. They populate a defined set of starter values only. Selecting a preset does not override later edits unless an administrator selects another preset. Any manual change sets the visible preset label to Custom.

The threshold is interpreted in one site-wide threshold currency. Quotation events compare the Quotation's base total against that threshold and display the Quotation transaction currency. Multi-company sites with different base currencies are not considered supported for a single global threshold; this must be solved with per-company settings before enabling those events across such companies.

## Event identity and deduplication

A source event is identified by source DocType/type, source document/integration identity and a stable source event ID. CRM Signal DocType validation normalizes those values and derives the SHA-256 key itself; it never trusts a caller-supplied hash. A unique field enforces the key. A repeated event returns the existing signal and does not publish another notification. Partial identities are rejected; a key without identity is cleared.

External API callers may provide a source event ID. When source metadata is omitted, the server namespaces the event by the authenticated integration user. When callers supply source DocType and source name, those caller-provided values form the namespace and must be stable and unique across integrations. Retries must reuse the same integration identity, source namespace and event ID. Without an ID, the endpoint retains legacy non-idempotent behavior.

Quotation submit identity includes the source document and its submission modification timestamp. Opportunity transition identity includes source document, previous/next status and modification timestamp.

## Digest contract

The scheduled checker runs every minute. It compares the configured time with the timezone in System Settings and uses the site-local calendar date as its idempotency boundary. A recipient is marked queued only after their separate `frappe.sendmail` request succeeds; the email-queue write and that recipient's Settings marker are committed together. A later scheduler run skips already queued recipients and retries the remaining recipients.

Recipients are enabled System Users holding the Sales Manager role plus explicitly configured additional System User email addresses. Settings validation rejects unknown, disabled or Website User addresses; the task still filters recipients to enabled System Users and never sends to Guest or arbitrary external recipients. Generate each message while impersonating that recipient and use permission-aware `frappe.get_list` queries for Lead counts and expiring Quotations. Send one digest per user; never share a system-wide result across recipients.

## Failure behavior

Notification delivery to one recipient is isolated from other recipients and the source transaction. Errors are logged without rolling back the saved Quotation, Opportunity or CRM Signal. A failed signal-creation hook is logged and does not block the source business document; repeated source events remain safe because identity is unique.

## Acceptance criteria

- Settings are System Manager-only; configuration validates ranges, time, currencies, statuses and recipient addresses. Additional addresses must resolve to registered, enabled System Users (not Website Users).
- Preset selection fills values; manual changes switch the profile indicator to Custom.
- The event handler uses configured thresholds/statuses and no hard-coded currency symbol.
- The API requires Guest rejection, honors the ingestion switch, validates optional source identity and deduplicates stable IDs.
- DocType validation recomputes source-event keys and rejects partial identities regardless of whether records arrive through hooks, the ingestion endpoint, Desk or another API.
- Repeated source event IDs return the original CRM Signal without duplicate notification.
- Digest schedule respects the System Settings timezone and sends at most one queued digest per date.
- Digest labels the stale Lead condition as not modified, formats each Quote in its transaction currency and filters recipients to enabled System Users.
- Unit, Bench and E2E tests cover the settings schema, identity uniqueness, scheduler date boundary, retries and user-visible settings.

## Deferred acceptance

- Live-site confirmation of Company currency, Opportunity statuses, timezone, recipient policy and role matrix.
- Multi-company threshold policy for installations whose companies use different base currencies.
- Production webhook TLS/rate limiting/secret rotation and deployment rollback.
