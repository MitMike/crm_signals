# CRM Signals — Deployment and rollback runbook

This runbook is the generic release procedure for CRM Signals. It does not replace the target site's change-control process or constitute evidence that a deployment has been rehearsed.

## 1. Preflight

Record the following before scheduling a change:

- Site name and hosting/Bench owner.
- Installed Frappe and ERPNext versions, plus all installed apps.
- CRM Signals revision currently deployed and revision to be deployed.
- Database engine and backup/restore procedure for the site.
- Company default currencies, including any company-specific differences.
- System Settings timezone.
- Opportunity statuses and terminal Lead statuses used by the live workflows.
- Sales User, Sales Manager, System Manager and non-sales test accounts.
- Approved digest recipients and business owner for the stale-Lead definition.
- Dedicated integration user, API credential owner, gateway/TLS/rate-limit configuration and secret-rotation contact.

Do not enable quotation threshold signals across companies with different base currencies. The first release has one site-wide threshold currency.

## 2. Before deployment

1. Announce the maintenance window and identify the person authorized to approve rollback.
2. Confirm scheduler, background workers, Redis, database and mail queue are healthy.
3. Review the release PR, migration/schema changes, CI evidence and deferred follow-ups.
4. Take a database backup and include public and private files. Record the backup paths and timestamp.
5. Verify that the backup files exist, are readable and are copied to the site's approved off-host backup location.
6. Confirm that the restore procedure and required app revisions are available. A backup that has never been restored is not a proven rollback.

Typical Bench backup command:

```bash
bench --site <site-name> backup --with-files
```

Use the backup location and restore options supported by the installed Bench version. Do not assume that a database-only backup includes uploaded files.

## 3. Deploy

1. Deploy the approved CRM Signals revision using the site's normal source-control/release process.
2. Confirm the checked-out revision before running migrations.
3. Run the site migration:

```bash
bench --site <site-name> migrate
```

4. Build the app assets:

```bash
bench build --app crm_signals
```

5. Restart web, scheduler and worker processes using the site's normal process manager:

```bash
bench restart
```

6. Confirm the migration completed without errors and that the site starts normally. Do not proceed if schema sync, patch execution, asset build or worker startup failed.

## 4. Post-deploy smoke tests

Run these checks with named test accounts. Record the user, role, result and evidence for each check.

### Installation and settings

- Confirm CRM Signals appears in `bench --site <site-name> list-apps`.
- Open CRM Signals Settings as System Manager; verify that a Sales User and non-sales user cannot read or edit it.
- Confirm the master switch, external-ingestion switch, Quotation/Opportunity switches, threshold currency, statuses, digest time and recipients.
- Confirm that the System Settings timezone is valid and that each configured recipient is an enabled System User.
- Confirm that companies using a different base currency are not inadvertently enabled for the site-wide threshold policy.

### Permissions and privacy

- Test a Sales User who owns a Lead, a Sales User assigned through an active ToDo, a Sales User with a restrictive User Permission, a Sales Manager, a System Manager and a non-sales user.
- Verify list view, direct form, API read, report, export and print paths. Test both linked and unlinked signals.
- Verify that an owner/assignee without read permission on the linked Lead/Customer and CRM Signal receives no realtime payload.
- Verify that an unreadable linked signal does not appear in a user's list merely because that user owns the CRM Signal record.
- Confirm that no notification is broadcast site-wide.

### Event and API behavior

- Submit a Quotation below and at the configured threshold; verify currency and signal behavior.
- Transition an Opportunity into and out of a configured status; verify only the configured transition creates a signal.
- POST a valid external event using a dedicated integration user and a stable `source_event_id`.
- Repeat the exact request with the same integration identity and event ID; verify that the original signal is returned and no second notification is sent.
- Verify Guest rejection, ingestion switch behavior, invalid fields and link validation.
- Do not use Administrator API credentials for integrations.

### Digest and operations

- Verify the scheduler is enabled and running in the configured site timezone.
- Verify a digest is queued only for enabled, eligible System Users and that each recipient sees only rows their account can read.
- Check Email Queue and Error Log for the test date; distinguish queued from delivered.
- Confirm that failed recipient sends are visible in diagnostics and that a later scheduler run retries pending recipients.
- Reconcile D2 invoices, Payment Entry receipts, separate POS receipts, open receivables and overdue invoices against native ERPNext reports, grouped by currency.
- Confirm that backup monitoring, application logs, scheduler and worker monitoring are active.

## 5. Rollback

### Immediate containment

If a functional or privacy issue is found:

1. A System Manager disables **Enable CRM Signals** in CRM Signals Settings. Disable external ingestion separately if the API is implicated.
2. If the Settings page is unavailable, follow the site's approved emergency configuration procedure; do not improvise direct database edits.
3. Stop sending new external events and notify the integration owner.
4. Preserve relevant logs, Error Log entries, Email Queue records and the deployed commit SHA.

### Full rollback

A code-only checkout is not a safe rollback when a release has changed DocType schema or data.

1. Stop or pause scheduler and workers according to the site's change procedure.
2. Restore the database and public/private files from the pre-deployment backup using the installed Bench version's documented restore procedure.
3. Restore the application code to the exact revision paired with that backup.
4. Run the site's standard service restart and health checks.
5. Verify login, core ERPNext operations, CRM Signal visibility and scheduler state.
6. Reconcile any external webhook retries or email queue activity that occurred during the failed deployment.
7. Record the reason, restored backup timestamp, restored app revision and follow-up actions.

Do not delete CRM Signal records or manually remove unique indexes as an improvised rollback.

## 6. Release record

For each target site, attach:

- Preflight inventory and approved configuration.
- Backup paths, timestamp and restore verification.
- Deployed commit SHA and migration output.
- Smoke-test results and role matrix.
- D2 reconciliation evidence.
- API integration and secret-management confirmation.
- Scheduler, mail-queue and realtime evidence.
- Rollback rehearsal or explicit approval of the site's existing tested rollback process.
- Outstanding exceptions, owner and due date.

A successful CI run proves the tested code paths in CI only. It does not complete any target-site acceptance item in `docs/FOLLOW_UPS.md`.
