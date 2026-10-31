# H — Highlights and event-driven sales alerts

**Status:** Design specified; implementation planned after CRM Signals event idempotency and settings hardening.

## Problem and users

Sales users and managers need high-priority alerts for high-value quotations and meaningful VIP proposal engagement. Alerts must be timely, attributable, deduplicated and routed to people responsible for the relationship.

## Goals

- Reuse the CRM Signal record and recipient-routing contract.
- Trigger high-value quote alerts on submitted quotations.
- Track opens only for first-party proposal links created by the app or a verified integration.
- Support an explicit, admin-managed VIP customer list and configurable threshold.
- Prevent duplicate notifications, crawler noise and alert storms.
- Preserve currency and source-document context.

## High-value quotation rule

- Trigger on Quotation submission only.
- Default threshold: 200,000 in the Company default currency, preserving the current numeric default but removing the hard-coded INR assumption.
- Use grand_total and the quotation's actual currency after confirming it matches Company default currency. If the currency basis cannot be established, do not trigger a misleading monetary alert.
- Comparison is greater than or equal to the threshold.
- A quotation creates at most one high-value event for its submission identity. Replaying the hook does not create another signal.

## VIP proposal-link open rule

Only a first-party tracked proposal link or a provider integration with a stable event ID is supported. Do not infer an open from an arbitrary external URL.

The link record binds an opaque random token to a Quotation and, when available, its Customer/Lead. Store only a token hash; do not persist the bearer token. Links have an expiry and may be revoked. A tracking request validates the token, resolves the source record and records an event ID.

- A stable provider event ID is mandatory for provider callbacks; duplicate IDs are ignored.
- For first-party requests, one recognized human-open event is recorded per link/session window; do not use invasive browser fingerprinting.
- Known security scanners, mail previews and link-unfurl bots are classified as automated and do not trigger a human-engagement alert. Uncertain traffic is retained as an unclassified view but does not trigger escalation.
- The alert cooldown is one notification per tracked link and recipient in 24 hours. The underlying event log may retain additional deduplicated opens for analysis.
- A privacy notice and any required consent must be approved before deployment of tracking links.

## Configuration and recipients

Create CRM Signals Settings fields for the high-value threshold, VIP Customer allowlist, notification cooldown and escalation recipients. Only System Manager can edit them.

Recipients are the linked Lead/Customer owner, active ToDo assignees and explicitly configured escalation recipients. Resolve to enabled System Users with read permission on the linked party. No site-wide broadcast.

## Data model

- CRM Proposal Link: source Quotation, party, token hash, created/expiry/revoked fields and owner.
- CRM Proposal Link Event: link reference, source event ID, event time, classification (human/automated/unclassified), non-identifying metadata needed for diagnostics, and deduplication key.
- CRM Signal source-event fields link alert records to their originating quote or proposal-link event.

Do not store full IP addresses or create browser fingerprints. Apply a documented retention period to event records after the site owner approves privacy requirements.

## Acceptance criteria

| ID | Requirement | Validation |
|---|---|---|
| H-AC1 | Quote threshold uses Company currency and is configurable | Multi-currency Bench tests |
| H-AC2 | Quote at threshold triggers one High signal; below threshold does not | Unit + Bench tests |
| H-AC3 | Retry of the same Quotation submit event does not duplicate signal or notification | Idempotency tests |
| H-AC4 | VIP proposal links are opaque, expiring and revocable | Security tests |
| H-AC5 | Repeated provider event ID is processed once | Callback idempotency test |
| H-AC6 | Known automated opens do not trigger a human alert | User-agent/provider classification fixtures |
| H-AC7 | Unclassified opens are not escalated | Unit test |
| H-AC8 | Alert recipients are enabled, related and allowed to read the parent | Permission + notification tests |
| H-AC9 | Cooldown limits notification frequency without deleting event history | Time-window unit test |
| H-AC10 | Tracking is disabled until privacy/consent requirements are approved | Settings validation and rollout checklist |
| H-AC11 | CRM Signals Console links to the source Quotation | Bench + Playwright E2E |

## Dependencies and rollout

Depends on CRM Signals Settings, source-event idempotency and recipient permission tests. Ship high-value quote alerts first. Ship proposal-link tracking only after a privacy review and a working first-party link flow exist. Do not label arbitrary link opens as VIP engagement.
