# D3 — Service Resolution and SLA

**Status:** Frappe Helpdesk adapter implemented for the standard HD Ticket schema; target-site version, permissions and SLA calendar acceptance remain open.

## Problem and users

Sales leadership needs an accurate view of customer service demand and resolution performance alongside pipeline and billing. The dashboard must measure the support system actually installed on the target site, not assume a generic ERPNext or Frappe Helpdesk schema.

## Goals

- Discover and record the installed support application and authoritative ticket DocType.
- Identify the authoritative SLA configuration, deadline, pause and resolution fields.
- Provide ticket volume, open backlog, resolved volume, resolution-time measures and SLA compliance only when source semantics are validated.
- Respect each user's permissions on ticket and SLA records.
- Show unconfigured/unavailable states distinctly from zero.

## Non-goals

- Installing a new ticketing system as part of this slice.
- Combining multiple support systems into one metric before their identities, lifecycle and deduplication rules are specified.
- Guessing that the source is Issue, HD Ticket, or a custom DocType.
- Inferring SLA compliance from ticket status or elapsed calendar time when the installed app provides a native SLA result.
- Exposing ticket descriptions, comments or personal data in executive metric cards.

## Required site discovery

Before selecting a source, inspect the target site's installed apps, DocTypes, custom fields, workflows and role permissions. Complete the mapping table in the delivery record:

| Concept | Required mapping |
|---|---|
| Ticket DocType | Exact installed DocType and owning app/version |
| Ticket identity | Stable document name and customer/Lead link |
| Created timestamp | Authoritative creation timestamp |
| Current state | Status field plus terminal/resolved state mapping |
| Resolution timestamp | Actual resolution timestamp; do not substitute modified unless validated |
| SLA record | Exact DocType/link and SLA policy identifier |
| SLA deadline | Native target timestamp and timezone |
| SLA result | Native compliant/breached/paused/cancelled semantics |
| Pause behavior | Whether and how waiting states suspend the clock |
| Business calendar | Holidays, working days, working hours and timezone |
| Permissions | Ticket and SLA read access for Sales User and Sales Manager |
| Retention | Whether old ticket/SLA records remain queryable |

The user confirmed that the target support system is Frappe Helpdesk and that the standard/default configuration is in use. The adapter targets standard HD Ticket, HD Ticket Status, and HD Service Level Agreement schema, while checking runtime metadata and permissions before querying. The agreed initial working-week assumption is Monday–Saturday; the installed SLA's own working-hours rows and holiday list remain authoritative at runtime. Do not infer target-site app versions or active policy configuration from upstream source.

## Metric contract after source mapping

All date windows use the site timezone and are configurable. The initial dashboard window is rolling 30 calendar days, matching D1/D2.

- Tickets created: count of source tickets created within the selected window.
- Tickets resolved: count of tickets whose authoritative resolution timestamp falls within the window.
- Open backlog: current tickets in configured non-terminal states.
- Average resolution time: the Helpdesk-native resolution_time is business-hours duration from SLA attachment to resolution, less hold time. Label it as average SLA business hours; do not present it as elapsed time from ticket creation. Tickets without an SLA do not provide this duration.
- SLA compliance: compliant resolved/eligible tickets divided by all tickets with a valid applicable SLA outcome in the selected cohort. Exclude tickets without an applicable SLA from the denominator and show the eligible count.
- SLA breaches: count tickets with native breach outcome in the selected cohort, including open breached tickets only if the installed SLA engine defines that state.

The final cohort definitions (created cohort vs resolved cohort) must be displayed beside each measure. Never compare ticket-created counts with resolution rates without stating the denominator and period.

## Permissions and failure states

- Use permission-aware Frappe reads for ticket and SLA sources.
- Check ticket and SLA DocType permissions independently, then verify field-level read access for every lifecycle/SLA field used by an aggregate.
- If a DocType, required field, native SLA outcome, DocType permission or field-level permission is missing, mark the corresponding metric unavailable; never interpret a field silently removed by Frappe as a zero.
- If tickets are readable but SLA records are not, ticket volume may be available while SLA compliance is unavailable.
- Do not return descriptions, comments, contact details or raw ticket payloads to the executive dashboard.

## Acceptance criteria

| ID | Requirement | Validation |
|---|---|---|
| D3-AC1 | Discovery records installed apps, ticket DocType, SLA source, fields and version | Target-site discovery report |
| D3-AC2 | No source DocType is assumed or hard-coded before discovery | Unit test with unknown/missing adapter |
| D3-AC3 | Ticket metrics follow the mapped lifecycle fields and configured cohort | Bench fixtures for each status/timestamp |
| D3-AC4 | Resolution time uses authoritative resolution timestamp | Bench fixture where modified differs from resolved_at |
| D3-AC5 | SLA calculation honors native deadline, pause and business-calendar behavior | Bench tests against the installed SLA engine |
| D3-AC6 | SLA denominator includes only tickets with valid applicable outcomes | Unit + Bench edge-case tests |
| D3-AC7 | Ticket/SLA DocType and field-level permission failures are represented as unavailable, not zero | Sales User/Manager permlevel tests |
| D3-AC8 | Dashboard cards show cohort, window, units and eligible count | Playwright E2E |
| D3-AC9 | No sensitive ticket content is returned in aggregate payloads | API schema/privacy test |
| D3-AC10 | Frappe/ERPNext v15 and v16 compatibility is maintained | Bench matrix |

## Implementation approach

Implement a small adapter contract with metadata validation, permission-aware aggregate retrieval and normalization. The current adapter uses standard Frappe Helpdesk fields: creation, status_category, resolution_date, resolution_time, sla, and agreement_status. It checks the current user's permitted field names before querying because the standard Helpdesk fields are stored at permlevels 7 and 8 and Frappe may silently remove fields the user cannot read. SLA compliance uses only native Fulfilled and Failed outcomes; due/paused states are excluded from the eligible denominator. SLA outcomes and no-SLA counts use the same rolling 30-day created-ticket cohort. The dashboard receives aggregates only.

## Delivery gate

D3 implementation is code-complete pending CI and target-site acceptance. Sign-off still requires recording the installed Helpdesk/Frappe versions, confirming the Monday–Saturday calendar against each active SLA policy's configured working hours and holiday list, and validating ticket/SLA permissions. CI fixtures cannot substitute for that site confirmation.
