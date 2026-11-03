# CRM Signals — Deployment and rollback runbook

This runbook is the generic release procedure for CRM Signals. It does not replace the target site's change-control process or constitute evidence that a deployment has been rehearsed.

## 1. Preflight

Record the following before scheduling a change:

- Site name and hosting/Bench owner.
- Installed Frappe and ERPNext versions, plus all installed apps.
- CRM Signals revision currently deployed and revision to be deployed.
- Database engine and backup/restore procedure for the site.
- Company default currencies and the approved Company-specific quotation thresholds or exact-currency legacy fallback.
- System Settings timezone.
- Opportunity statuses and terminal Lead statuses used by the live workflows.
- Sales User, Sales Manager, System Manager and non-sales test accounts.
- Optional effective DocType/field permission probe: use dedicated active synthetic System User accounts (not Website Users) and the alias-only `effective_user_permissions` section of the read-only preflight report. See the Administrator Guide for the exact `--kwargs` invocation.
- Approved digest recipients and business owner for the stale-Lead definition.
- Dedicated integration user, API credential owner, gateway/TLS/rate-limit configuration and secret-rotation contact.

Configure and approve a threshold for each enabled Company in that Company's base currency. A Company-specific row takes precedence. The legacy site-wide threshold is a fallback only when its currency exactly matches that Company's base currency; no implicit FX conversion occurs, and a mismatch suppresses the signal. Record the approved amount and currency for every enabled Company in the target-site acceptance record.

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

1. Resolve the approved full 40-character CRM Signals commit SHA from the release/change record. Do not deploy the moving `main` branch.
2. For a first installation, clone directly into the Bench app directory, detach and verify the approved SHA, then run Bench dependency setup:

```bash
APP_SHA="<approved-commit-sha>"
test "${#APP_SHA}" -eq 40
git clone --origin upstream https://github.com/MitMike/crm_signals.git apps/crm_signals
git -C apps/crm_signals fetch upstream --tags
git -C apps/crm_signals checkout --detach "$APP_SHA"
test "$(git -C apps/crm_signals rev-parse HEAD)" = "$APP_SHA"
bench setup requirements crm_signals
bench --site <site-name> install-app crm_signals
```

3. For an existing installation, inspect the Bench-managed remote, verify that it points to the approved CRM Signals repository, fetch, detach and verify the approved SHA before reconciling dependencies:

```bash
APP_SHA="<approved-commit-sha>"
test "${#APP_SHA}" -eq 40
git -C apps/crm_signals remote get-url upstream
git -C apps/crm_signals fetch upstream --tags
git -C apps/crm_signals checkout --detach "$APP_SHA"
test "$(git -C apps/crm_signals rev-parse HEAD)" = "$APP_SHA"
bench setup requirements crm_signals
```

Bench-created app clones use the remote name `upstream`; do not assume `origin` exists. If an existing non-Bench clone uses another remote name, inspect `git remote -v`, verify the repository URL and substitute that remote explicitly. Stop if the remote does not identify the approved repository.

`bench setup requirements crm_signals` installs the editable Python package and Node dependencies and synchronizes Bench app state from the pinned tree. Do not run `bench get-app crm_signals` in this pinned procedure: it installs the cloned tree before returning, so a later checkout cannot protect the initial dependency install or asset build.

4. Record the verified `git -C apps/crm_signals rev-parse HEAD` output in the target-site acceptance record.
5. Run the site migration:

```bash
bench --site <site-name> migrate
```

6. Build the app assets:

```bash
bench build --app crm_signals
```

7. Restart web, scheduler and worker processes using the site's normal process manager:

```bash
bench restart
```

8. Confirm the migration completed without errors and that the site starts normally. Do not proceed if the checked-out SHA differs from the approved SHA, dependency setup, schema sync, patch execution, asset build or worker startup failed.


## 4. Post-deploy smoke tests

### Release identity preflight

After installation and migration, run the read-only target-site report:

```bash
bench --site <site-name> execute crm_signals.diagnostics.get_site_preflight_report
```

Proceed only when `framework.crm_signals_source.available` is true and `framework.crm_signals_source.commit_sha` exactly matches the approved full release SHA. The diagnostic verifies that Git's top-level directory is the CRM Signals repository itself (not an enclosing Bench/monorepo), checks tracked and untracked changes, and validates the full SHA. Each fixed Git query is read-only and bounded to five seconds. A dirty checkout, root mismatch, missing Git, timeout or invalid revision is a stop condition; do not infer identity from a branch or package version. See [Administrator Guide — read-only preflight](ADMIN_GUIDE.md#read-only-target-site-preflight-report) and [Target-Site Acceptance Kit §2](TARGET_SITE_ACCEPTANCE.md#2-preflight-inventory).


Run these checks with named test accounts. Record the user, role, result and evidence for each check.

### Installation and settings

- Confirm CRM Signals appears in `bench --site <site-name> list-apps`.
- Open CRM Signals Settings as System Manager; verify that a Sales User and non-sales user cannot read or edit it.
- Confirm the master switch, external-ingestion switch, Quotation/Opportunity switches, threshold currency, statuses, digest time and recipients.
- Confirm that the System Settings timezone is valid and that each configured recipient is an enabled System User.
- Confirm each enabled Company has an approved Company-specific threshold or exact-currency legacy fallback; a currency mismatch suppresses the signal.

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

### Explorer activity timeline

- Verify the Activity Timeline entry points from Lead, Customer, Opportunity and CRM Signal forms; a High-Value Quote signal must open the Highlight context.
- Run the context, role and field-permission matrix in [Target-Site Acceptance Kit](TARGET_SITE_ACCEPTANCE.md#10-e-explorer-activity-timeline-acceptance) with Sales User, Sales Manager, System Manager and non-sales accounts.
- Verify GET-only paging, source drill-down, and distinct empty, unavailable and not-connected states. Confirm unreadable context/source fields or records do not leak summaries or links.

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
