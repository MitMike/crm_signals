# E — Explorer and customer interaction timeline

**Status:** Design specified; integration adapters and target-site source inventory remain.

## Problem and users

Sales users need one chronological view of the customer interactions relevant to an active sales relationship. The timeline must link back to authoritative source records and must not imply that an integration exists when it does not.

## Goals

- Provide a Lead/Customer-centered timeline reachable from a CRM Signal, Highlight, Lead, Customer or Opportunity.
- Normalize source events through explicit adapters.
- Include only sources installed, configured and readable by the current user.
- Preserve source timestamps, identity, type and source-document link.
- Paginate large timelines and prevent duplicate display of the same source event.

## Non-goals

- Replacing Communication, Email, Calendar, WhatsApp or telephony products.
- Scraping mailboxes or external systems without a configured integration.
- Storing full message bodies, call recordings or attachments in the timeline.
- Displaying activities the user cannot read in the source application.

## Source adapter contract

An adapter declares:
- source ID and owning app/provider;
- installed/configured status and supported version range;
- source DocType and required fields;
- normalized event type and timestamp;
- stable source event ID;
- relationship resolver to Lead/Customer/Opportunity;
- permission check and authorized Desk route;
- cursor/pagination support.

Potential source adapters may include CRM Signal, Quotation, Opportunity, Communication, Event and ToDo, plus call/WhatsApp providers only when installed and configured. This list is a discovery candidate, not a claim that every source exists on the target site. Do not guess custom DocTypes or field names.

## Timeline contract

Each row contains normalized source ID, source event ID, event type, timestamp, related Lead/Customer/Opportunity, safe summary, source route (if authorized) and source status. Sort newest first, with a deterministic source-ID/event-ID tie-break. Use site timezone for display and preserve the source timezone in the underlying timestamp.

The first release shows metadata and a short, safely escaped summary only. Full email bodies, call recordings, WhatsApp text and attachments remain in their source systems and are opened only through an authorized route.

Deduplicate by source ID plus stable source event ID. Do not deduplicate solely by timestamp or message text. If an adapter lacks a stable identity, it must not participate in the unified feed until it can provide one.

## Permissions and availability

- Fetch through permission-aware source APIs or adapter-specific permission checks.
- Re-check read permissions before rendering a source link.
- A source that is not installed/configured is "not connected"; a source with no matching activity is an empty result; a source denied by permission is unavailable. These states are distinct.
- Never fall back to Administrator/system permission bypass for a user timeline.
- Do not expose whether inaccessible records exist.

## Acceptance criteria

| ID | Requirement | Validation |
|---|---|---|
| E-AC1 | Timeline shows only configured, supported source adapters | Adapter registry unit tests |
| E-AC2 | Entries normalize to a stable event contract | Adapter fixture tests |
| E-AC3 | Sort order and pagination are stable under equal timestamps | Unit + Bench tests |
| E-AC4 | Duplicate source event IDs render once | Deduplication tests |
| E-AC5 | Source links are shown only when the user can read the source record | Role-specific Bench tests |
| E-AC6 | Missing integration, empty result and permission-denied states differ | API + Playwright tests |
| E-AC7 | Message bodies, recordings and attachments are not copied into the normalized feed | API schema/privacy test |
| E-AC8 | Timeline opens from Lead, Customer, Opportunity, Signal and Highlight contexts | Playwright E2E |
| E-AC9 | All timestamps display consistently in the site timezone | Timezone tests |
| E-AC10 | Frappe v15 and v16 are supported for each installed adapter | Bench matrix |

## Dependencies and rollout

Start with CRM Signal, Quotation, Opportunity and standard Frappe activity sources actually present on the target site. Add WhatsApp/call adapters only after a provider and installed DocType are verified. Keep each adapter independently testable and independently disableable.
