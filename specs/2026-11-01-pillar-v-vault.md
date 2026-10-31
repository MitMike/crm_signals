# V — Vault and historical metric snapshots

**Status:** Design specified; metric registry and retention configuration are prerequisites.

## Problem and users

Managers need to compare operating performance across time without recalculating historical dashboards using today's changing records. Historical values must be reproducible and auditable.

## Goals

- Store daily snapshots of approved aggregate metrics.
- Record the metric definition and source version used for each snapshot.
- Preserve dimensions such as currency, status and business unit where approved.
- Make corrections traceable without silently rewriting prior snapshots.
- Store aggregate values only; do not copy raw customer content or personal data into the Vault.

## Non-goals

- A raw CRM or financial data warehouse.
- Replacing ERPNext accounting ledgers or audit trails.
- Recomputing or correcting historical values without a versioned record.
- Cross-currency conversion without an approved conversion contract.
- Backfilling unbounded history automatically.

## Snapshot contract

Each snapshot record includes:
- metric ID and definition version;
- snapshot date and site timezone;
- window/cohort and filter definition;
- dimensions (for example currency or stage);
- numeric value and unit;
- source DocTypes and source record count;
- calculation status (complete, partial, unavailable);
- captured timestamp and app version;
- correction/supersedes reference when a revised snapshot is created.

The initial metric registry includes validated D1 and D2 measures. D3 metrics are added only after the target support/SLA source mapping passes its acceptance criteria. H interaction metrics are added only after verified event tracking is live. A metric with unavailable sources produces an explicit unavailable snapshot status, not a numeric zero.

## Persistence and correction policy

- Produce one daily snapshot per metric, dimension set, date and definition version.
- Snapshot records are append-only. A correction creates a new revision linked to the superseded record; it never overwrites the prior value.
- Backfills are admin-only, bounded by an explicit date range and logged.
- Use a unique idempotency key to prevent duplicate records when the scheduler retries.
- Keep monetary metrics grouped by source currency.
- Do not store source document names, party names, email addresses or free-text summaries in snapshot rows unless a future approved use case requires them.

## Retention and access

Snapshot storage is disabled until System Manager configures an explicit retention period and the business owner approves it. Do not silently retain indefinitely or silently delete data. Pruning must be a separately tested scheduled operation with an audit log and a dry-run mode.

Only Sales Manager and System Manager roles can read the executive Vault by default. Any narrower source permissions must still be respected when generating snapshots; the scheduler's elevated execution context must not be used to expose records hidden from the approved reporting population. The source visibility policy must be finalized before enabling scheduled capture.

## Acceptance criteria

| ID | Requirement | Validation |
|---|---|---|
| V-AC1 | Snapshot contains metric ID, version, date, dimensions, unit and source count | Schema tests |
| V-AC2 | Same scheduler event cannot create duplicate snapshots | Idempotency test |
| V-AC3 | Corrections create a linked revision and preserve the original | Bench migration and update tests |
| V-AC4 | Monetary dimensions retain separate currencies | Multi-currency fixture |
| V-AC5 | Unavailable source produces an unavailable snapshot state, not zero | Permission/schema failure test |
| V-AC6 | Snapshot rows do not contain raw party identifiers or message bodies | Schema/privacy test |
| V-AC7 | Backfill is bounded, admin-only and audited | Permission + job tests |
| V-AC8 | No snapshots run until retention and source visibility policy are configured | Settings/scheduler test |
| V-AC9 | Pruning has dry-run, audit and boundary tests | Retention job tests |
| V-AC10 | Manager views are permission-controlled | Bench + Playwright E2E |

## Data model proposal

A CRM Metric Snapshot DocType stores one record per metric/dimension/date/version with the value, status and provenance fields. A child table or normalized dimension JSON may be used for the small fixed dimension set, but the representation must be queryable and validated. Choose the simplest schema that supports unique idempotency, append-only revisions and indexes by date/metric.

## Dependencies and rollout

D1 and D2 must have accepted metric definitions and target-site reconciliation. D3 and H metrics are optional registry entries until implemented. Approve source visibility and retention before enabling the scheduler. Start with a limited set of aggregate counts; add financial values only after target-site reconciliation.
