# CRM Signals — Target-Site Acceptance Kit

**Purpose:** collect reproducible evidence that CRM Signals is safe and correct on the intended Frappe/ERPNext site. The confirmed framework target is Frappe v16.5; this kit remains an evidence template, not proof that any target-site test has already passed.

**Release rule:** do not sign off production until every P0 gate has an owner, dated evidence and an explicit pass. CI on a disposable Bench does not replace site-specific acceptance.

## 1. Execution record

| Field | Value |
|---|---|
| Site / environment | |
| Business owner | |
| Technical owner | |
| Test date (with timezone) | |
| CRM Signals approved commit SHA (full 40 characters) | |
| Frappe version (exact v16.5 patch/build) | |
| ERPNext version | |
| Helpdesk version | |
| Database engine / version | |
| Installed app list and versions | |
| Backup identifier | |
| Rollback owner | |

Attach the output of `bench version`, the installed-app inventory and the deployment revision. Redact credentials, tokens, customer data and internal hostnames before sharing evidence.

## 2. Preflight inventory

Record, do not infer:

- [ ] Frappe reports the expected v16.5 patch/build; ERPNext and Helpdesk exact versions are recorded and compatible.
- [ ] Run the read-only Bench preflight command (`bench --site <site-name> execute crm_signals.diagnostics.get_site_preflight_report`) after deploying a revision containing it; attach reviewed output through the site's approved secure channel. The report includes Company names and threshold amounts and must not be shared publicly.
- [ ] Confirm `framework.crm_signals_source.available` is true (the imported package resolves to the CRM Signals Git repository itself, the checkout has no tracked or untracked changes, and Git returned a valid full SHA) and `framework.crm_signals_source.commit_sha` exactly matches the approved full 40-character release SHA recorded above. The preflight rejects an enclosing Bench/monorepo Git root. If unavailable, dirty or mismatched, stop and resolve the checkout/release identity before installation, migration or acceptance; do not infer it from a branch, tag or package version.
- [ ] CRM Signals is installed and migrated on the intended site.
- [ ] Installed support, helpdesk, telephony, email and activity apps are inventoried with exact versions.
- [ ] Every enabled Company and its default currency are recorded.
- [ ] System Settings timezone and scheduler status are recorded.
- [ ] Lead and Opportunity workflows, status values and terminal statuses are exported/reviewed.
- [ ] Relevant custom fields, custom scripts, server scripts and permission overrides are inventoried.
- [ ] Sales roles and representative users are identified for the permission matrix.
- [ ] Review static DocPerm rows and field permlevels, then independently complete the effective user/persona matrix below; static role grants do not prove effective access.
- [ ] Run the optional effective DocType/field permission probe with dedicated active synthetic System User accounts (never Administrator or Website User) and attach its alias-only `effective_user_permissions` result:
  ```bash
  bench --site <site-name> execute crm_signals.diagnostics.get_site_preflight_report --kwargs "{'test_users': {'sales_user': 'crm-sales-user-test', 'sales_manager': 'crm-sales-manager-test', 'system_manager': 'crm-system-manager-test', 'non_sales': 'crm-non-sales-test'}}"
  ```
- [ ] For list-level record visibility, create dedicated synthetic Lead/Customer/Opportunity/Quotation/CRM Signal/invoice/payment/ticket records and optionally pass their exact names under `test_records`, keyed by profile, DocType and non-sensitive label. The report uses permission-filtered `frappe.get_list` with `fields=["name"]`; it returns labels/booleans only. A false result may mean missing or inaccessible.
- [ ] For the Sales User linked-party boundary, create an allowed synthetic Lead and a restricted synthetic Lead; set the Sales User's Lead User Permission to the allowed Lead; create a linked CRM Signal for the restricted Lead owned by that Sales User; and create an unlinked CRM Signal owned by the same user. Verify both signals exist with the authorized setup account, then run the `test_records` probe for those two exact CRM Signal names. Expect `linked_restricted: false` and `unlinked_owned: true` with checked status. The linked signal must remain hidden despite CRM Signal ownership; do not add a share or replace permission-filtered reads with `get_all`. This mirrors the real-Frappe regression in PR #124.
- [ ] Confirm each supplied profile reports `status: checked`, active System User account and valid role membership; review every DocType and required-field result plus any supplied record-visibility result. `partial`, missing, invalid-role, false or unavailable results require investigation, not sign-off.
- [ ] As an authorized System Manager, open the dedicated synthetic Sales User's User form and generate or rotate API credentials through its API Access controls (typically "Generate Keys"; confirm the label on the installed Frappe patch). Do not use Administrator credentials or print the secret with a Bench command.
- [ ] Store the API key/secret only in the site's approved password manager or secret store. Enter them at the script's silent prompts; do not place credentials in command arguments, environment files, shell history, tickets or acceptance evidence.
- [ ] After testing, rotate the API secret or disable/delete the dedicated synthetic user, then verify the old credential pair is rejected. Record only the test alias and rotation/revocation outcome.
- [ ] With the dedicated Sales User's own API credentials (never Administrator), run the authenticated HTTP smoke below. It verifies the authenticated identity first, then expects HTTP 403 for the linked restricted document, HTTP 200 for the unlinked owned document, and a list containing exactly the unlinked record. Do not follow redirects; a redirect is a failed check because the token must not be forwarded to another origin.
- [ ] Keep response bodies in a mode-0600 temporary directory and remove them after checking. Record only the authenticated profile alias, HTTP status codes, pass/fail outcomes, site/Frappe version, deployed full SHA and timestamp. Never attach raw response bodies, API keys/secrets, record names or user identifiers.
- [ ] The script below requires Bash, curl and Python 3.10+. It uses GET query parameters exactly as Frappe's method wrappers expect. PR #130 is merged and CI-verified: Playwright exercises the same methods over a browser session cookie on Frappe v16 and pinned v16.5. PR #131 is merged and CI-verified: the direct Desk form-loader permission regression passed in supported Frappe v16 and pinned Frappe 16.5.0 Playwright. PR #133 is merged and CI-verified: cookie-independent token authentication is exercised on supported v16 and pinned v16.5. PR #135 is merged and CI-verified: the separate `/api/resource/CRM%20Signal` single-document and list API-token checks passed on supported v16 and pinned v16.5.0. PR #137 is merged and its final-head print-view regression passed on supported Frappe v16 and pinned v16.5.0. The linked-restricted/unlinked-owned browser print check below still requires authorized target-site execution. These are reference-stack tests and do not verify the target site's TLS, reverse proxy, gateway or credential policy or replace live API-token/browser-form acceptance below. Report/export/print/dashboard behavior remains separate.

```bash
set -euo pipefail
# Prevent inherited bash -x tracing from exposing credential expansion below.
set +x

: "${SITE_URL:?Set the canonical HTTPS staging site URL}"
: "${EXPECTED_SALES_USER:?Set the dedicated non-Administrator Sales User name}"
: "${LINKED_RESTRICTED_SIGNAL:?Set the CRM Signal linked to a Lead excluded by the Sales User User Permission}"
: "${UNLINKED_OWNED_SIGNAL:?Set the unlinked CRM Signal owned by the same Sales User}"
[[ "$SITE_URL" == https://* ]] || { echo "SITE_URL must use HTTPS" >&2; exit 2; }
[[ "$EXPECTED_SALES_USER" != "Administrator" ]] || { echo "Administrator is not an acceptable test identity" >&2; exit 2; }
[[ "$LINKED_RESTRICTED_SIGNAL" != "$UNLINKED_OWNED_SIGNAL" ]] || { echo "Use two distinct synthetic records" >&2; exit 2; }

read -r -s -p "Frappe API key: " CRM_SIGNALS_API_KEY; printf '\n'
read -r -s -p "Frappe API secret: " CRM_SIGNALS_API_SECRET; printf '\n'

umask 077
tmp_dir="$(mktemp -d)"
curl_config="$tmp_dir/curl.conf"
trap 'rm -rf "$tmp_dir"; unset CRM_SIGNALS_API_KEY CRM_SIGNALS_API_SECRET' EXIT
printf 'header = "Authorization: token %s:%s"\n' "$CRM_SIGNALS_API_KEY" "$CRM_SIGNALS_API_SECRET" > "$curl_config"

request() {
  curl --proto '=https' --config "$curl_config" --silent --show-error --output "$2" --write-out '%{http_code}' "${@:3}" "$1"
}

base_url="${SITE_URL%/}"

# Prove the API key belongs to the intended synthetic Sales User.
status="$(request "$base_url/api/method/frappe.auth.get_logged_user" "$tmp_dir/user.json")"
[[ "$status" == "200" ]] || { echo "FAIL: identity endpoint returned HTTP $status" >&2; exit 1; }
python3 - "$tmp_dir/user.json" "$EXPECTED_SALES_USER" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as response_file:
    payload = json.load(response_file)
if payload.get("message") != sys.argv[2]:
    raise SystemExit("FAIL: API credentials do not belong to the expected Sales User")
print("PASS: authenticated identity matches the dedicated Sales User")
PY

# A CRM Signal owner must not read a signal linked to a Lead they cannot read.
status="$(request "$base_url/api/method/frappe.client.get" "$tmp_dir/restricted.json" \
  --get --data-urlencode "doctype=CRM Signal" \
  --data-urlencode "name=$LINKED_RESTRICTED_SIGNAL")"
[[ "$status" == "403" ]] || { echo "FAIL: restricted linked document expected HTTP 403, got $status" >&2; exit 1; }
echo "PASS: linked restricted document denied (HTTP 403)"

# The same user must retain access to their unlinked owned signal.
status="$(request "$base_url/api/method/frappe.client.get" "$tmp_dir/allowed.json" \
  --get --data-urlencode "doctype=CRM Signal" \
  --data-urlencode "name=$UNLINKED_OWNED_SIGNAL")"
[[ "$status" == "200" ]] || { echo "FAIL: unlinked owned document expected HTTP 200, got $status" >&2; exit 1; }
python3 - "$tmp_dir/allowed.json" "$UNLINKED_OWNED_SIGNAL" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as response_file:
    payload = json.load(response_file)
if payload.get("message", {}).get("name") != sys.argv[2]:
    raise SystemExit("FAIL: allowed document response did not match the synthetic record")
print("PASS: unlinked owned document readable (HTTP 200)")
PY

# A permission-filtered list must exclude the linked restricted signal.
status="$(request "$base_url/api/method/frappe.client.get_list" "$tmp_dir/list.json" \
  --get --data-urlencode "doctype=CRM Signal" \
  --data-urlencode 'fields=["name"]' \
  --data-urlencode "filters={\"name\":[\"in\",[\"$LINKED_RESTRICTED_SIGNAL\",\"$UNLINKED_OWNED_SIGNAL\"]]}" \
  --data-urlencode "limit_page_length=10")"
[[ "$status" == "200" ]] || { echo "FAIL: list endpoint expected HTTP 200, got $status" >&2; exit 1; }
python3 - "$tmp_dir/list.json" "$UNLINKED_OWNED_SIGNAL" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as response_file:
    payload = json.load(response_file)
names = {row.get("name") for row in payload.get("message", [])}
if names != {sys.argv[2]}:
    raise SystemExit("FAIL: list response did not contain exactly the unlinked owned record")
print("PASS: list contains only the unlinked owned record (HTTP 200)")
PY



# The standard REST resource endpoint must enforce the same linked-party boundary.
status="$(request "$base_url/api/resource/CRM%20Signal/$LINKED_RESTRICTED_SIGNAL" "$tmp_dir/resource-restricted.json" --header "Accept: application/json")"
[[ "$status" == "403" ]] || { echo "FAIL: restricted REST resource expected HTTP 403, got $status" >&2; exit 1; }
if grep -Fq -- "$LINKED_RESTRICTED_SIGNAL" "$tmp_dir/resource-restricted.json"; then
  echo "FAIL: restricted REST resource response disclosed the record name" >&2
  exit 1
fi
echo "PASS: linked restricted REST resource denied without record-name disclosure (HTTP 403)"

status="$(request "$base_url/api/resource/CRM%20Signal/$UNLINKED_OWNED_SIGNAL" "$tmp_dir/resource-allowed.json" --header "Accept: application/json")"
[[ "$status" == "200" ]] || { echo "FAIL: allowed REST resource expected HTTP 200, got $status" >&2; exit 1; }
python3 - "$tmp_dir/resource-allowed.json" "$UNLINKED_OWNED_SIGNAL" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as response_file:
    payload = json.load(response_file)
if payload.get("data", {}).get("name") != sys.argv[2]:
    raise SystemExit("FAIL: REST resource response did not match the synthetic record")
print("PASS: unlinked owned REST resource readable (HTTP 200)")
PY

status="$(request "$base_url/api/resource/CRM%20Signal" "$tmp_dir/resource-list.json" \
  --get --header "Accept: application/json" \
  --data-urlencode 'fields=["name"]' \
  --data-urlencode "filters=$(python3 -c 'import json,sys; print(json.dumps([["CRM Signal","name","in",sys.argv[1:]]]))' "$LINKED_RESTRICTED_SIGNAL" "$UNLINKED_OWNED_SIGNAL")" \
  --data-urlencode "limit_page_length=10")"
[[ "$status" == "200" ]] || { echo "FAIL: REST resource list expected HTTP 200, got $status" >&2; exit 1; }
python3 - "$tmp_dir/resource-list.json" "$UNLINKED_OWNED_SIGNAL" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as response_file:
    payload = json.load(response_file)
names = {row.get("name") for row in payload.get("data", [])}
if names != {sys.argv[2]}:
    raise SystemExit("FAIL: REST resource list did not contain exactly the unlinked owned record")
print("PASS: REST resource list contains only the unlinked owned record (HTTP 200)")
PY

report_filters="$(python3 -c 'import json,sys; print(json.dumps([["CRM Signal","name","in",sys.argv[1:]]]))' "$LINKED_RESTRICTED_SIGNAL" "$UNLINKED_OWNED_SIGNAL")"

status="$(request "$base_url/api/method/frappe.desk.reportview.get_list" "$tmp_dir/reportview.json" \
  --get --data-urlencode "doctype=CRM Signal" \
  --data-urlencode 'fields=["name","message"]' \
  --data-urlencode "filters=$report_filters" \
  --data-urlencode "limit_page_length=10")"
[[ "$status" == "200" ]] || { echo "FAIL: Report View expected HTTP 200, got $status" >&2; exit 1; }
python3 - "$tmp_dir/reportview.json" "$UNLINKED_OWNED_SIGNAL" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as response_file:
    payload = json.load(response_file)
rows = payload.get("message", [])
names = {row.get("name") for row in rows}
if names != {sys.argv[2]}:
    raise SystemExit("FAIL: Report View did not return only the unlinked owned record")
print("PASS: Report View contains only the unlinked owned record (HTTP 200)")
PY

status="$(request "$base_url/api/method/frappe.desk.reportview.export_query" "$tmp_dir/reportview-export.csv" \
  --get --data-urlencode "doctype=CRM Signal" \
  --data-urlencode 'fields=["name","message"]' \
  --data-urlencode "filters=$report_filters" \
  --data-urlencode "file_format_type=CSV" \
  --data-urlencode "title=CRM Signals permission export" \
  --data-urlencode "csv_delimiter=," \
  --data-urlencode "csv_quoting=2")"
[[ "$status" == "200" ]] || { echo "FAIL: Report View CSV export expected HTTP 200, got $status" >&2; exit 1; }
python3 - "$tmp_dir/reportview-export.csv" "$LINKED_RESTRICTED_SIGNAL" "$UNLINKED_OWNED_SIGNAL" <<'PY'
from pathlib import Path
import sys

csv_text = Path(sys.argv[1]).read_text(encoding="utf-8")
if sys.argv[2] in csv_text:
    raise SystemExit("FAIL: CSV export disclosed the linked restricted record name")
if sys.argv[3] not in csv_text:
    raise SystemExit("FAIL: CSV export omitted the unlinked owned record")
print("PASS: CSV export includes only the permitted synthetic record (HTTP 200)")
PY

echo "PASS: authenticated Sales User API permission boundary verified"
```

If any status or payload assertion fails, stop acceptance. Preserve the redacted status and sanitized error class only; inspect the target Frappe version, API authentication, User Permission and CRM Signal permission-query path. Do not retry with Administrator or weaken the linked-denied/unlinked-allowed expectation.
- [ ] With a fresh browser session authenticated as the dedicated Sales User, open the linked-restricted CRM Signal at `/printview?doctype=CRM%20Signal&name=<linked-name>&format=Standard&no_letterhead=1`; expect HTTP 403 and confirm the restricted message is absent. Open the unlinked-owned signal through the same print route; expect HTTP 200 and its synthetic message. Do not use a share key, Administrator session or broadened permission to obtain the expected result. PR #137's reference-stack regression passed on v16 and pinned v16.5.0; live staging remains required.
- [ ] Separately test direct form, REST API, reports, exports, print and dashboard behavior with approved controlled records. The optional preflight does not prove those paths.
- [ ] Email account, sender policy, mail queue and realtime deployment topology are recorded.
- [ ] Current CRM Signals Settings values and enabled presets are captured.

| Company | Default currency | Company override threshold | Derived currency | Legacy fallback threshold (only on exact currency match) | Approved? |
|---|---|---:|---|---:|---|
| | | | | | |

**Multi-company rule:** a Company-specific threshold row takes precedence and derives its currency from that Company's default currency. If no row exists, the legacy site-wide threshold is used only when its currency exactly matches the Quotation Company's base currency. No implicit FX conversion occurs. Record a row or explicitly approve the fallback for every enabled Company.

## 3. Deployment, migration and rollback

- [ ] Record the approved full 40-character CRM Signals commit SHA.
- [ ] Before any CRM Signals dependency installation, Node package setup, asset build, site install or migration, verify the app checkout is detached at that exact SHA.
- [ ] For first install, use the direct-clone procedure below; do not use `bench get-app crm_signals` because Bench installs the app before that command returns.
- [ ] For upgrades, inspect the `upstream` remote (the default name created by Bench), verify it points to the approved repository, fetch and detach to the approved SHA. If the existing clone uses a different remote, verify and use its actual name rather than assuming `origin`.
- [ ] Run `bench setup requirements crm_signals` only after the detached SHA check. This installs Python/Node dependencies from the pinned tree and synchronizes Bench app state.
- [ ] On first install, run `bench --site <site-name> install-app crm_signals` after dependency setup.
- [ ] Take a database and private/public files backup using the site's approved process.
- [ ] Record backup location, timestamp, retention and restore operator.
- [ ] Deploy to staging first.
- [ ] Run `bench --site <site-name> migrate` and capture complete output.
- [ ] Build assets with `bench build --app crm_signals` and capture output.
- [ ] Verify DocType schema, roles, fixtures, hooks, scheduler registrations and installed app state.
- [ ] Run CRM Signals tests appropriate to the environment.
- [ ] Perform a smoke test of Desk, CRM Signals Settings, dashboard/report routes and API access.
- [ ] Rehearse restore into an isolated environment; verify database and files are mutually consistent.
- [ ] Rehearse rollback to the prior app revision and restore point.
- [ ] Obtain technical and business approval before production deployment.

### First installation — pin before Bench setup

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

### Existing installation upgrade

```bash
APP_SHA="<approved-commit-sha>"
test "${#APP_SHA}" -eq 40
git -C apps/crm_signals remote get-url upstream
git -C apps/crm_signals fetch upstream --tags
git -C apps/crm_signals checkout --detach "$APP_SHA"
test "$(git -C apps/crm_signals rev-parse HEAD)" = "$APP_SHA"
bench setup requirements crm_signals
bench --site <site-name> migrate
bench build --app crm_signals
bench restart
```

| Step | Command / evidence reference | Result | Owner | Date |
|---|---|---|---|---|
| Approved SHA / detached checkout | | | | |
| Dependency setup from pinned tree | | | | |
| Backup | | | | |
| Staging migrate | | | | |
| Smoke tests | | | | |
| Restore rehearsal | | | | |
| Rollback rehearsal | | | | |

Do not paste secrets or full customer records into this document.


## 4. Permission parity matrix

Test with real representative users, not only Administrator. Check each path independently because list visibility, direct document access and downstream report/export paths can differ.

| Role / persona | Signal list | Direct signal form | Dashboard/report | API read | Export/print | Digest email | Realtime |
|---|---|---|---|---|---|---|---|
| Sales User | | | | | | | |
| Sales Manager | | | | | | | |
| System Manager | | | | | | | |
| Non-sales user | | | | | | | |
| Disabled user | | | | | | | |

### Direct CRM Signal form loading

Use the same two synthetic records as the linked-party permission test: a CRM Signal linked to a Lead excluded by the Sales User's Lead User Permission, and an unlinked CRM Signal owned by that user. Do not use Administrator for the permission assertions.

- [ ] Sign in to Desk as the dedicated Sales User and open the linked-restricted record directly at `/app/crm-signal/<URL-encoded-name>`, not through a list view.
- [ ] In the browser Network panel, inspect the GET `/api/method/frappe.desk.form.load.getdoc` request for DocType `CRM Signal` and the restricted name. Expect a permission-denied response (HTTP 403 on the tested Frappe v16/v16.5 reference stacks); confirm the restricted signal message and document fields are not returned or rendered. The Desk SPA shell itself may return 200; that is not document access.
- [ ] Open the unlinked owned signal directly. Expect the form-loader GET to return 200, the loaded document to identify only that synthetic record, and its expected message to render.
- [ ] Repeat for Sales Manager and non-sales personas using approved records and record each result independently; do not infer their form permissions from the Sales User case.
- [ ] Record only persona alias, route outcome, loader status, exact Frappe build, deployed full SHA and timestamp. Redact record names, message content, credentials and response bodies from shared evidence.
- [ ] If the restricted document loads, stop acceptance. Inspect DocPerm, User Permission, shares, owner/assignment and the CRM Signal permission query; do not add a share or weaken the expected denial.

PR #131 adds a Playwright regression for this direct route on supported Frappe v16 and pinned v16.5.0. It is reference-stack evidence only; execute this procedure on the authorized target site.

Acceptance criteria:
- [ ] A user cannot read signal content when they cannot read the linked Lead/Customer.
- [ ] List-query and direct-document access produce equivalent authorization outcomes.
- [ ] API access does not bypass document or linked-party permissions.
- [ ] Digest content is generated under each recipient's user context.
- [ ] Realtime delivery excludes users without read access to the CRM Signal, linked Lead/Customer and originating source DocType (e.g. Quotation/Opportunity); test that parent access without source access suppresses the notification.
- [ ] As the dedicated Sales User, open the CRM Signal Report View with the linked-restricted and unlinked-owned synthetic pair. Confirm only the unlinked owned record appears. Export the filtered result as CSV and confirm it contains the unlinked record but not the linked-restricted record or message. Repeat with the Sales Manager and System Manager and record each persona separately; do not infer their results from the Sales User.
- [ ] Record only persona alias, Report View/export status, permitted row count, exact Frappe build, deployed full SHA and timestamp. Do not attach the CSV, record names, messages, credentials or raw response bodies.
- [x] PR #139 adds cookie-independent API-token CI coverage for `frappe.desk.reportview.get_list` and `frappe.desk.reportview.export_query`; merged as `ac2d83d823bdcad46fe84ccd5d2b8954c0b0d959` from final tested head `2e30fd02a1074e26adbf1d0de1f4fb715e2d837a` after all four final-head workflows passed on supported Frappe v15/v16 and pinned Frappe 16.5.0. CI does not replace execution on the authorized target site.
- [ ] Export and print do not expose rows unavailable in the corresponding report/list.
- [ ] Helpdesk HD Ticket field-level read access is checked independently for `status_category`, `resolution_date`, `resolution_time`, `sla` and `agreement_status` using the installed version's actual permlevels (all are permlevel 0 in the v1.28.0 reference).
- [ ] If Helpdesk v1.29.0, v1.30.2 or v1.31.1 is installed, verify the exact Frappe build contains the `frappe/ui` package required by `@framework/ui`; if v1.31.1, also verify the `Notification Type` DocType/controller. Stop if absent.
- [ ] Compare installed Helpdesk permission metadata with the v1.28.0 reference: Sales User/Manager are not default HD Ticket or SLA readers. Do not assign Agent/Agent Manager solely for dashboard visibility; use an approved custom read-only role with base HD Ticket read, plus HD Service Level Agreement read only if SLA metrics are approved. For later versions, add only the exact approved higher field permlevels.
- [ ] Confirm ticket metrics become unavailable without HD Ticket read/required fields, and SLA metrics become unavailable without SLA DocType read or `agreement_status` field access.
- [ ] Disabled or unapproved recipients receive no digest or realtime content.

Record user IDs/roles only in the site's secured test record; do not add personal data here.

## 5. D1/D2 data correctness and finance reconciliation

**Automated evidence boundary:** PR #67 (merged as `84ab2ce`; final head `cfd7c5ec`) passed the Frappe v15/v16 Bench workflows and the pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lane. It checks Lead/Opportunity deltas, invoice and party-account currency grouping, overdue/receipt/POS aggregate filters, and the independent Payment Entry/Sales Invoice DocType permission path. PR #67's POS row models persisted aggregate fields only. PR #69 (merged as `efe7872`; final head `33b750a`) adds a real disposable POS Profile, company-specific Mode of Payment and submitted POS Sales Invoice; it asserts ERPNext-calculated payment settlement through the normal document lifecycle. Both changes passed the Frappe v15/v16 Bench matrix and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lane. All synthetic records and temporary permissions are rolled back. Neither fixture simulates browser checkout, POS Opening/Closing, cash-drawer operations or inventory movements. CI does not reconcile financial values to native reports or prove real Sales User/Manager permissions. Complete the site checks below regardless of CI outcome.

Use a fixed, approved date range and the site's native ERPNext reports as the comparison source. Record filters, company, currency, timezone and report run time. Reconcile by Company and currency; do not sum unlike currencies.

| Metric | CRM Signals result | Native ERPNext report/result | Company/currency | Difference | Explanation / sign-off |
|---|---:|---:|---|---:|---|
| Active Leads | | | | | |
| Active Opportunities | | | | | |
| Pipeline value | | | | | |
| Sales Invoice value excluding returns | | | | | |
| Payment Entry receipts | | | | | |
| POS receipts | | | | | |
| Party-account-currency receivables | | | | | |

- [ ] Confirm the selected Lead/Opportunity statuses match actual workflows.
- [ ] Confirm terminal Lead statuses and stale-Lead semantics with Sales.
- [ ] Confirm Sales Invoice returns/credit notes are excluded exactly as intended.
- [ ] Confirm Payment Entry receipt treatment independently of Sales Invoice return metadata.
- [ ] Confirm POS receipts are not double-counted with Sales Invoices.
- [ ] Confirm receivables are grouped by party account currency and reconcile to the native report.
- [ ] Explain every non-zero variance; finance owner signs off.

## 6. Webhook and integration security

- [ ] Create a dedicated integration System User; do not use Administrator.
- [ ] Grant only the required CRM Signal create/API permissions.
- [ ] Generate unique credentials per environment and store them in an approved secret manager.
- [ ] Enforce HTTPS/TLS at the public endpoint and reverse proxy.
- [ ] Apply gateway rate limits, request-size limits and abuse monitoring.
- [ ] Confirm authentication failures are logged without logging secrets.
- [ ] Verify stable `source_event_id` is supplied by each producer for retry idempotency.
- [ ] Test duplicate delivery, malformed payload, unauthorized user and rate-limit behavior.
- [ ] Document credential owner, rotation interval, revocation procedure and incident contact.
- [ ] Rotate a test credential and prove the old credential is rejected.

| Integration / producer | Service user | Permission scope | Rate limit | Secret owner | Rotation date |
|---|---|---|---|---|---|
| | | | | | |

## 7. Scheduler, email and realtime operations

- [ ] Confirm scheduler is enabled and workers are healthy.
- [ ] Confirm digest time is interpreted in the intended System Settings timezone.
- [ ] Confirm the configured recipient list contains only active, approved System Users.
- [ ] Trigger a controlled digest and inspect the queued email as each recipient.
- [ ] Confirm per-recipient failures do not block other recipients.
- [ ] Confirm duplicate scheduler execution does not queue duplicate recipient/date digests.
- [ ] In staging, use a controlled Failed outbox fixture to verify only a System Manager with outbox read access can replay; GET is rejected, only Failed rows are accepted, and attempt history/audit comment are preserved.
- [ ] Verify a second replay is rejected while the row is Pending/Completed and that an enqueue failure leaves Pending for scheduled recovery.
- [ ] Confirm mail provider delivery, bounce and suppression behavior.
- [ ] After deploying a release that includes PR #54, verify **CRM Signal Notification Delivery** is readable by System Managers only and cannot be created, edited or deleted through Desk.
- [ ] Create a synthetic signal for an approved test recipient. Verify exactly one ledger row exists for the signal/recipient pair, the stable delivery ID is populated, and the ledger contains no copied message/source content.
- [ ] Verify the initial row becomes Attempted, and record that this means only that Frappe queued an after-commit callback—not that Redis published the event or a browser received it.
- [ ] In staging only, identify the dedicated Socket.IO Redis endpoint from the site's actual Bench configuration. Do not stop shared cache/queue Redis or disrupt production. Temporarily make only the Socket.IO endpoint unavailable, create a synthetic signal, restore the endpoint, and wait until next_retry_at is due. Verify the scheduler increments the attempt count, retains the same delivery ID and produces no duplicate toast in the active Desk session.
- [ ] With a due Attempted row present, restart the scheduler/worker using the site's normal process manager. Verify scheduled recovery resumes after restart and capture the resulting ledger state.
- [ ] After an initial attempt, revoke the recipient's eligibility (remove the relevant owner/ToDo assignment or originating DocType read access) before the next retry. Verify the row becomes Cancelled and no further realtime publish occurs.
- [ ] Confirm Failed rows appear after the bounded retry budget is exhausted; inspect the recorded error type and Error Log without copying signal content into this evidence file.
- [ ] Record monitoring, alert thresholds, log locations and on-call owner.

Note: digest recipient failure isolation and digest queue idempotency are code-level safeguards; actual scheduler topology and mail-provider behavior still require this site test. Realtime retry is bounded at-least-once. The stable delivery ID suppresses duplicate toasts only within the active Desk session; Attempted is not a Redis delivery receipt, browser receipt or human acknowledgement. Run Redis/worker fault injection only in an approved staging environment.

## 8. Settings and business semantics

- [ ] System Manager reviews Balanced, Sales Focused and Executive presets before enabling.
- [ ] Master enable and external ingestion remain off until approved.
- [ ] Each enabled Company has an approved override or a currency-matched legacy fallback; no cross-currency comparison or implicit conversion is used.
- [ ] Opportunity status list matches actual workflow values.
- [ ] Stale-day window and timestamp semantics are approved.
- [ ] Digest time, timezone and extra recipients are approved.
- [ ] Each setting is tested after save and after a worker/scheduler restart.
- [ ] Non-System Manager users cannot modify settings or outbox records.

## 9. D3 Frappe Helpdesk adapter acceptance

The initial adapter is implemented for standard Frappe Helpdesk. Verify the installed app and schema rather than assuming that the target site's patch level exactly matches upstream. Record the observed metadata and policy:

| Question | Observed answer / evidence |
|---|---|
| Installed Helpdesk app and exact version | |
| `HD Ticket` and `HD Service Level Agreement` DocTypes present | |
| Required fields present: `creation`, `status_category`, `resolution_date`, `resolution_time`, `sla`, `agreement_status` | |
| Sales User permitted fields at read level (record installed permlevels) | |
| Sales Manager permitted fields at read level (record installed permlevels) | |
| Ticket DocType read permission for each role | |
| SLA DocType read permission for each role | |
| Active SLA working days/hours and timezone | |
| Active SLA holiday list | |
| Confirmed Monday–Saturday calendar match or documented exception | |
| Native pause/resume and Fulfilled/Failed behavior | |
| Retention/deletion policy and business-approved KPI interpretation | |

The v1.28.0 reference fields are all permlevel 0. For later Helpdesk versions, do not automatically grant permlevel 7 or 8; review all fields at those levels with the security owner. A field-level permission gap should make the affected metric unavailable, not zero. Helpdesk v1.29.0 and later link `@framework/ui` to `apps/frappe/ui`, absent from the unmodified Frappe v16.5.0 tag; v1.31.1 additionally calls `Notification Type` during installation, also absent. Verify the exact Frappe build before using those versions; the pinned v16.5.0 reference uses v1.28.0.

### D3 staging test matrix

Create synthetic tickets only in staging. Allow the Helpdesk SLA engine to set native outcomes.

| Fixture | Expected dashboard behavior |
|---|---|
| Open ticket | Included in current Open backlog |
| Paused ticket | Included in current Paused backlog; not an SLA-compliance outcome |
| Resolved in last 30 days | Included in resolved cohort when `resolution_date` and status_category are readable |
| Ticket with Fulfilled SLA | Included in eligible denominator and fulfilled numerator |
| Ticket with Failed SLA | Included in eligible denominator and failed count |
| First Response Due / Resolution Due / Paused | Excluded from Fulfilled/Failed compliance denominator |
| Ticket without an SLA | Counted separately; excluded from compliance denominator |
| User without HD Ticket read | D3 unavailable |
| User without required field-level permission | Only affected measures unavailable; never displayed as zero |

Expected compliance is `Fulfilled / (Fulfilled + Failed)`. With no eligible outcomes, show unavailable (—), not 0%. Average resolution duration uses positive Helpdesk `resolution_time` values converted from seconds to business hours; it is not elapsed time from ticket creation. SLA policy working hours, holiday list and timezone are authoritative.

## 10. E Explorer activity timeline acceptance

The first Explorer release is deliberately limited to CRM Signal, Quotation and Opportunity. Quotation and Opportunity rows are record-created timeline entries showing the current status; they are not historical status-change events. Do not enable optional activity providers merely because their DocTypes exist.

### Context and entry-point matrix

| Entry point | Expected timeline context | Required relationship / behavior |
|---|---|---|
| Lead form | Lead | Resolve the selected Lead and show only linked, readable source rows |
| Customer form | Customer | Resolve the selected Customer and show only linked, readable source rows |
| Opportunity form | Opportunity | Read `opportunity_from` and `party_name`; resolve only a Lead or Customer relationship |
| CRM Signal form | CRM Signal | Resolve the populated Lead or Customer relation; no action is expected for an unlinked signal |
| High-Value Quote CRM Signal | Highlight | Resolve only the linked CRM Signal whose `signal_type` is exactly `High-Value Quote` |

- [ ] Confirm the page is visible to the intended Sales User, Sales Manager and System Manager roles; confirm an unapproved non-sales role does not receive the page or form action.
- [ ] Open the timeline from each of the four supported forms. Verify the High-Value Quote action uses the Highlight context and a non-High-Value-Quote signal uses the ordinary CRM Signal context.
- [ ] Test direct route entry as well as form actions. Page visibility is role-restricted; the read-only API must independently enforce the current user's context-record, source-record and field-level read permissions.
- [ ] For Lead, Customer, Opportunity and CRM Signal contexts, test both readable and unreadable records. A hidden context relationship/filter field must make the context unavailable, not resolve from a silently omitted value.
- [ ] Verify source fields are readable before use: CRM Signal `signal_type`, `priority` and the applicable `lead`/`customer` relation; Quotation `quotation_to`, `party_name`, `status`; Opportunity `opportunity_from`, `party_name`, `status`.
- [ ] Verify every returned source link opens only a source record the same user can read. Revoke source access and repeat; the row/link must disappear or the source must become unavailable, never bypass Desk permissions.
- [ ] Distinguish source states: missing DocType = not connected; missing required field or denied DocType/field access = unavailable; readable source with no matching records = empty. Do not interpret unavailable or not connected as zero activity.
- [ ] Verify the endpoint accepts GET for reads and rejects write methods. Confirm summaries contain only type/status metadata, not quotation amounts, signal message bodies, comments, recordings or attachments.
- [ ] Page through a timeline with more than one page. Confirm deterministic ordering for equal timestamps, no duplicate source/event identities, and that the cursor is rejected when reused with another user, context or page size. Refresh must begin a new snapshot.
- [ ] Confirm timestamps render in the site's configured timezone and that a source record's current status is not presented as a historical status transition.

### Optional provider discovery record

Complete one row for each proposed Communication, Event, ToDo, call or WhatsApp provider before implementation. A DocType name alone is not sufficient evidence of a connected source.

| Installed provider / exact version | Source DocType | Required fields | Stable event identity | Lead/Customer relationship mapping | DocType + field read permissions | Operator / evidence |
|---|---|---|---|---|---|---|
| | | | | | | |

Do not add an optional adapter until the installed provider/version, exact schema, stable event identity, relationship mapping and permission contract are recorded and reviewed. Until then, the source remains not connected.

## 11. Dashboard horizontal-inset visual acceptance

BUG-2026-001 / FIX-2026-001 restores the CRM Signals dashboard's desktop and mobile horizontal spacing. PR #100 adds a Playwright computed-style assertion (24px at 1440px; 12px at 390px) and is merged/CI-verified. This section records the separate staging visual check; the automated test does not prove that the target site's rebuilt assets are current or visually correct.

- [ ] Confirm this is an authorized staging site and record the deployed full CRM Signals SHA, exact Frappe build, browser/version and test date/timezone.
- [ ] Follow the approved deployment procedure to build the assets with bench build --app crm_signals, clear the relevant site/browser caches and restart services as required by the site's change process. Attach the build output. Do not run a visual test by changing production assets outside approved change control.
- [ ] Sign in as System Manager and an approved Sales User who can access the dashboard. Open /app/crm-signals-dashboard at 100% browser zoom.
- [ ] At a 1440 × 900 desktop viewport, confirm the dashboard wrapper has 24px left and right padding and the content/cards are not clipped or horizontally overflowing.
- [ ] At a 390 × 844 mobile viewport, confirm the wrapper has 12px left and right padding and the content/cards remain readable without horizontal overflow.
- [ ] Capture a full-page or clearly framed screenshot at each viewport. Include the deployed full SHA, browser/version, viewport, test role and timestamp in the evidence record; use synthetic or redacted data so customer and ticket information is not exposed.
- [ ] If either inset is wrong, assets appear stale, or content overflows, leave the bug/fix UAT status open. Record the screenshot, build output, browser console errors and observed values; investigate the deployed SHA and asset/cache state before considering a code change. Do not patch CSS manually on the site.

| Date / timezone | CRM Signals full SHA | Frappe build | Browser / version | Role | Viewport | Expected left/right | Observed left/right | Screenshot / evidence | Result |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | 1440 × 900 | 24px / 24px | | | |
| | | | | | 390 × 844 | 12px / 12px | | | |

The test is complete only when both screenshots and observed values are reviewed and linked. Keep BUG-2026-001 / FIX-2026-001 marked UAT-open until then.

## 12. Release decision

| Gate | Status (Pass / Fail / Blocked) | Evidence link / artifact | Owner | Date |
|---|---|---|---|---|
| Supported versions and installed apps | | | | |
| Migration and schema verification | | | | |
| Backup / restore / rollback | | | | |
| Permission parity | | | | |
| D1/D2 finance reconciliation | | | | |
| Webhook security | | | | |
| Scheduler / email / realtime | | | | |
| Settings and business semantics | | | | |
| D3 Helpdesk version/schema/field permissions and SLA calendar acceptance | | | | |
| E Explorer context, role/field permissions, source states, paging and provider inventory | | | | |

**Decision:** Not approved / Approved for limited pilot / Approved for production

**Approvers:** Technical owner: ______  Business owner: ______  Finance/security (as applicable): ______

A blocked or failed P0 gate means no production sign-off. Record remediation as an issue with an owner and retest evidence.
