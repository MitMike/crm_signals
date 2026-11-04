"""Fast tests that do not require a running Frappe bench."""

import ast
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "crm_signals"


def test_pilot_repository_discovery_contract():
    project = (ROOT / "pyproject.toml").read_text()
    hooks = APP_ROOT / "hooks.py"
    assert 'name = "crm_signals"' in project
    assert "[tool.bench.frappe-dependencies]" in project
    assert 'frappe = ">=15.0.0,<17.0.0"' in project
    assert hooks.is_file()
    # Frappe v16's esbuild app scanner checks for these markers under
    # apps/<app>/<app>/ before registering its public asset directory.
    assert (APP_ROOT / "modules.txt").is_file()
    assert (APP_ROOT / "patches.txt").is_file()


def test_default_module_and_doctype_follow_frappe_layout():
    modules = (APP_ROOT / "modules.txt").read_text().splitlines()
    assert "Crm Signals" in modules
    module_root = APP_ROOT / "crm_signals"
    assert (module_root / "__init__.py").is_file()
    assert (module_root / "doctype/crm_signal/crm_signal.json").is_file()
    assert not (APP_ROOT / "doctype/crm_signal/crm_signal.json").exists()


def test_doctype_json_is_valid_and_field_options_are_consistent():
    metadata = json.loads(
        (APP_ROOT / "crm_signals/doctype/crm_signal/crm_signal.json").read_text()
    )
    fields = {field["fieldname"]: field for field in metadata["fields"]}
    assert fields["signal_type"]["reqd"] == 1
    assert fields["message"]["reqd"] == 1
    assert set(fields["priority"]["options"].splitlines()) == {
        "Low", "Medium", "High", "Urgent"
    }
    assert fields["lead"]["options"] == "Lead"
    assert fields["customer"]["options"] == "Customer"


def test_python_sources_parse():
    for path in APP_ROOT.rglob("*.py"):
        ast.parse(path.read_text(), filename=str(path))


def test_webhook_is_not_guest_whitelisted_or_permission_bypassed():
    source = (APP_ROOT / "api.py").read_text()
    tree = ast.parse(source)
    target = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        and node.name == "ingest_signal"
    )
    decorators = [ast.unparse(item) for item in target.decorator_list]
    assert decorators == ["frappe.whitelist(methods=['POST'])"]
    assert "ignore_permissions=True" not in source
    assert "frappe.db.commit()" not in source
    assert "allow_guest=True" not in source


def test_event_handlers_notify_through_shared_recipient_resolver():
    source = (APP_ROOT / "events.py").read_text()
    assert "notify_signal(signal)" in source
    assert "frappe.publish_realtime(" not in source


def test_permission_hooks_are_registered():
    hooks = (APP_ROOT / "hooks.py").read_text()
    assert '"CRM Signal": "crm_signals.permissions.crm_signal_has_permission"' in hooks
    assert '"CRM Signal": "crm_signals.permissions.crm_signal_query"' in hooks



def test_dashboard_page_workspace_and_permission_aware_api():
    page_root = APP_ROOT / "crm_signals/page/crm_signals_dashboard"
    page_json = json.loads((page_root / "crm_signals_dashboard.json").read_text())
    page_script = (page_root / "crm_signals_dashboard.js").read_text()
    page_style = page_root / "crm_signals_dashboard.css"
    assert page_json["page_name"] == "crm-signals-dashboard"
    assert page_json["module"] == "Crm Signals"
    assert {item["role"] for item in page_json["roles"]} == {
        "Sales User",
        "Sales Manager",
        "System Manager",
    }
    assert page_style.is_file()
    assert 'frappe.pages["crm-signals-dashboard"]' in page_script
    assert 'method: "crm_signals.api.get_dashboard_data"' in page_script

    workspace = json.loads(
        (APP_ROOT / "crm_signals/workspace/crm_signals/crm_signals.json").read_text()
    )
    assert workspace["label"] == "GME CRM Signals"
    assert workspace["title"] == "GME CRM Signals"
    assert json.loads(workspace["content"])[0]["type"] == "shortcut"
    assert workspace["shortcuts"][1]["link_to"] == "crm-signals-dashboard"

    api = (APP_ROOT / "api.py").read_text()
    assert "def get_dashboard_data():" in api
    assert "frappe.get_list(" in api
    assert '"CRM Signal"' in api
    assert 'frappe.has_permission("CRM Signal", ptype="read")' in api
    assert "frappe.db.sql(" not in api
    permissions = (APP_ROOT / "permissions.py").read_text()
    assert "def _get_visible_party_names" in permissions
    assert "frappe.get_list(" in permissions
    assert "UNION" not in permissions
    assert "SELECT" not in permissions.upper()


def test_dashboard_displays_core_metrics_and_activity_navigation():
    script = (
        APP_ROOT / "crm_signals/page/crm_signals_dashboard/crm_signals_dashboard.js"
    ).read_text()
    for label in ["Total signals", "Unread", "High priority", "Last 7 days",
                  "Signals by type", "Recent activity"]:
        assert label in script
    assert 'frappe.set_route("List", "CRM Signal")' in script
    assert 'frappe.set_route("Form", "Lead", lead)' in script
    assert 'frappe.set_route("Form", "Customer", customer)' in script



def test_sahdev_sales_compass_page_and_workspace_shortcut():
    page_root = APP_ROOT / "crm_signals/page/sahdev_dashboard"
    page_json = json.loads((page_root / "sahdev_dashboard.json").read_text())
    page_script = (page_root / "sahdev_dashboard.js").read_text()
    assert page_json["page_name"] == "sahdev-dashboard"
    assert page_json["module"] == "Crm Signals"
    assert {item["role"] for item in page_json["roles"]} == {
        "Sales User",
        "Sales Manager",
        "System Manager",
    }
    assert (page_root / "sahdev_dashboard.css").is_file()
    assert 'frappe.pages["sahdev-dashboard"]' in page_script
    assert 'method: "crm_signals.api.get_sales_compass_data"' in page_script
    for label in ["Executive Compass", "New leads", "Active leads",
                  "Active opportunities", "Open pipeline value",
                  "Active pipeline by stage", "Recent opportunities"]:
        assert label in page_script

    workspace = json.loads(
        (APP_ROOT / "crm_signals/workspace/crm_signals/crm_signals.json").read_text()
    )
    content = json.loads(workspace["content"])
    assert content[0]["data"]["shortcut_name"] == "Sahdev Dashboard"
    assert workspace["shortcuts"][0]["link_to"] == "sahdev-dashboard"
    assert any(link.get("link_to") == "crm-signals-dashboard" for link in workspace["links"])


def test_sales_compass_api_uses_permission_aware_reads_and_currency_grouping():
    source = (APP_ROOT / "api.py").read_text()
    assert "def get_sales_compass_data():" in source
    assert '_sales_dashboard_doctype_meta("Lead")' in source
    assert '_sales_dashboard_doctype_meta("Opportunity")' in source
    assert 'frappe.get_list(' in source
    assert '_dashboard_aggregate_field("SUM", "opportunity_amount", "total_amount")' in source
    assert '_dashboard_aggregate_field("COUNT", "name", "total")' in source
    assert 'group_by=", ".join(group_by_fields)' in source
    assert '"ignore_permissions"' not in source
    assert "frappe.db.sql(" not in source



def test_sahdev_billing_realization_page_and_permission_aware_api():
    page_root = APP_ROOT / "crm_signals/page/sahdev_dashboard"
    script = (page_root / "sahdev_dashboard.js").read_text()
    style = (page_root / "sahdev_dashboard.css").read_text()
    for label in ["Billing realization", "Invoiced", "Customer receipts",
                  "POS receipts", "Open receivables", "Overdue customer invoices"]:
        assert label in script
    assert 'frappe.set_route("Form", "Sales Invoice", name)' in script
    assert "sahdev-billing-metrics" in style
    assert "padding: 20px 24px 36px" in style

    api = (APP_ROOT / "api.py").read_text()
    assert "def _get_sales_billing_data(period_start, today):" in api
    assert '_sales_dashboard_doctype_meta("Sales Invoice")' in api
    assert '_sales_dashboard_doctype_meta("Payment Entry")' in api
    assert '"Payment Entry"' in api
    assert '"Sales Invoice"' in api
    assert '_dashboard_aggregate_field("SUM", amount_field, "total_amount")' in api
    assert '"party_account_currency", "outstanding_amount"' in api
    assert 'ignore_permissions=True' not in api
    assert 'frappe.db.sql(' not in api
    
def test_explorer_page_and_form_entry_points_are_registered():
    hooks = (APP_ROOT / "hooks.py").read_text()
    for doctype in ["Lead", "Customer", "Opportunity", "CRM Signal"]:
        assert f'"{doctype}": "public/js/crm_signals_explorer.js"' in hooks

    page_root = APP_ROOT / "crm_signals/page/crm_signals_explorer"
    page_json = json.loads((page_root / "crm_signals_explorer.json").read_text())
    page_script = (page_root / "crm_signals_explorer.js").read_text()
    assert page_json["page_name"] == "crm-signals-explorer"
    assert page_json["module"] == "Crm Signals"
    assert {item["role"] for item in page_json["roles"]} == {
        "Sales User",
        "Sales Manager",
        "System Manager",
    }
    assert (page_root / "crm_signals_explorer.css").is_file()
    assert 'frappe.pages["crm-signals-explorer"]' in page_script
    assert 'method: "crm_signals.explorer.get_explorer_timeline"' in page_script
    assert 'type: "GET"' in page_script
    assert "isCurrentRequest" in page_script

    form_script = (APP_ROOT / "public/js/crm_signals_explorer.js").read_text()
    assert 'frappe.set_route("crm-signals-explorer", contextDoctype, frm.doc.name)' in form_script
    assert '"High-Value Quote"' in form_script


def test_deployment_runbook_documents_company_thresholds_and_explorer_smoke_tests():
    runbook = (ROOT / "docs/DEPLOYMENT_RUNBOOK.md").read_text()
    assert "A Company-specific row takes precedence" in runbook
    assert "legacy site-wide threshold is a fallback only when its currency exactly matches" in runbook
    assert "no implicit FX conversion occurs" in runbook
    assert "each enabled Company has an approved Company-specific threshold or exact-currency legacy fallback" in runbook
    assert "Activity Timeline entry points from Lead, Customer, Opportunity and CRM Signal forms" in runbook
    assert "High-Value Quote signal must open the Highlight context" in runbook
    assert "The first release has one site-wide threshold currency" not in runbook

def test_change_aware_quality_filters_cover_workflows_and_packaging():
    workflow = (ROOT / ".github/workflows/quality.yml").read_text()
    python_filter = workflow.split("            python:", 1)[1].split(
        "            javascript:", 1
    )[0]
    javascript_filter = workflow.split("            javascript:", 1)[1].split(
        "\n\n  lint:", 1
    )[0]
    assert ".github/workflows/**" in python_filter
    assert "MANIFEST.in" in python_filter
    assert "requirements*.txt" in python_filter
    assert ".github/workflows/**" in javascript_filter
    assert "on:\n  push:\n    branches:\n      - main\n  pull_request:" in workflow

    assert workflow.count("needs.changes.result != 'success'") >= 5
    for version in ["310", "311", "312", "314"]:
        gate = workflow.split(f"  python-{version}-required:", 1)[1].split(
            "\n  python-", 1
        )[0]
        assert "if: always()" in gate
        assert "needs.changes.result != 'success'" in gate


def test_change_aware_bench_filters_cover_frappe_metadata_and_workflows():
    workflow = (ROOT / ".github/workflows/bench-e2e.yml").read_text()
    pinned = (ROOT / ".github/workflows/bench-target-v16-5.yml").read_text()
    expected_paths = [
        ".github/workflows/**",
        "crm_signals/**/*.json",
        "crm_signals/workspace/**",
        "crm_signals/patches.txt",
        "crm_signals/patches/**",
        "crm_signals/fixtures/**",
        "MANIFEST.in",
        "requirements*.txt",
    ]
    for path in expected_paths:
        assert path in workflow
        assert path in pinned

    for path in ["e2e/**", "playwright.config.ts"]:
        assert f"'{path}'" in workflow

    assert "workflow_dispatch:" in workflow
    assert "branches:" in workflow
    assert "- main" in workflow
    assert workflow.count("needs.changes.result != 'success'") >= 2
    for gate_name in ["bench-v15-required", "bench-v16-required"]:
        gate = workflow.split(f"  {gate_name}:", 1)[1].split(
            "\n  bench-", 1
        )[0]
        assert "if: always()" in gate
        assert "needs.changes.result != 'success'" in gate



def test_operator_webhook_curl_examples_use_line_continuations():
    for relative_path in ("README.md", "docs/ADMIN_GUIDE.md"):
        document = (ROOT / relative_path).read_text()
        code_blocks = document.split("```bash")[1:]
        commands = [
            block.split("```", 1)[0]
            for block in code_blocks
            if "curl -X POST " in block
        ]
        assert len(commands) == 1, relative_path
        lines = [line.rstrip() for line in commands[0].splitlines() if line.strip()]

        assert lines[0].startswith("curl -X POST "), relative_path
        assert lines[0].endswith("\\")
        assert all(line.endswith("\\") for line in lines[1:-1])
        assert not lines[-1].endswith("\\")


def test_target_site_permission_smoke_script_parses_as_bash():
    acceptance = (ROOT / "docs/TARGET_SITE_ACCEPTANCE.md").read_text()
    code_blocks = acceptance.split("```bash")[1:]
    scripts = [
        block.split("```", 1)[0]
        for block in code_blocks
        if "curl --disable --proto" in block
    ]
    assert len(scripts) == 1

    result = subprocess.run(
        ["bash", "-n"],
        input=scripts[0],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_operator_installation_pins_source_before_bench_setup():
    guide = (ROOT / "docs/ADMIN_GUIDE.md").read_text()
    runbook = (ROOT / "docs/DEPLOYMENT_RUNBOOK.md").read_text()
    acceptance = (ROOT / "docs/TARGET_SITE_ACCEPTANCE.md").read_text()
    readme = (ROOT / "README.md").read_text()

    for document in [guide, runbook, acceptance, readme]:
        assert "\nbench get-app crm_signals\n" not in document

    readme_first = readme.split("## Installation (pinned release)", 1)[1].split(
        "## Webhook authentication", 1
    )[0]
    readme_commands = readme_first.split("```bash", 1)[1].split("```", 1)[0]
    assert 'test "${#APP_SHA}" -eq 40' in readme_commands
    assert "bench get-app" not in readme_commands
    assert "git clone --origin upstream" in readme_commands
    assert "fetch upstream --tags" in readme_commands
    assert "rev-parse HEAD" in readme_commands
    assert (
        readme_commands.index("git clone --origin upstream")
        < readme_commands.index("fetch upstream --tags")
        < readme_commands.index("checkout --detach")
        < readme_commands.index("rev-parse HEAD")
        < readme_commands.index("bench setup requirements crm_signals")
        < readme_commands.index("install-app crm_signals")
    )

    guide_first = guide.split("### First installation", 1)[1].split(
        "### Upgrade an existing installation", 1
    )[0]
    assert "bench get-app crm_signals" not in guide_first
    assert "git clone --origin upstream" in guide_first
    assert (
        guide_first.index("git clone --origin upstream")
        < guide_first.index("checkout --detach")
    )
    assert (
        guide_first.index("checkout --detach")
        < guide_first.index("bench setup requirements crm_signals")
    )
    assert (
        guide_first.index("bench setup requirements crm_signals")
        < guide_first.index("install-app crm_signals")
    )

    guide_upgrade = guide.split("### Upgrade an existing installation", 1)[1].split(
        "## Configure CRM Signals", 1
    )[0]
    assert "fetch upstream --tags" in guide_upgrade
    assert "fetch origin" not in guide_upgrade
    assert (
        guide_upgrade.index("checkout --detach")
        < guide_upgrade.index("bench setup requirements crm_signals")
    )

    runbook_first = runbook.split("For a first installation", 1)[1].split(
        "For an existing installation", 1
    )[0]
    acceptance_first = acceptance.split(
        "### First installation — pin before Bench setup", 1
    )[1].split("### Existing installation upgrade", 1)[0]
    for document, first_install in [
        (runbook, runbook_first),
        (acceptance, acceptance_first),
    ]:
        assert "git clone --origin upstream" in document
        assert "fetch upstream --tags" in document
        assert "bench setup requirements crm_signals" in document
        assert "bench get-app crm_signals" in document
        assert "rev-parse HEAD" in document
        assert (
            first_install.index("checkout --detach")
            < first_install.index("bench setup requirements crm_signals")
        )

    for workflow_path in [
        ROOT / ".github/workflows/bench-e2e.yml",
        ROOT / ".github/workflows/bench-target-v16-5.yml",
    ]:
        workflow = workflow_path.read_text()
        clone_command = (
            'git clone --origin upstream "${{ github.workspace }}" apps/crm_signals'
        )
        checkout_command = (
            'git -C apps/crm_signals checkout --detach "$CRM_SIGNALS_SHA"'
        )
        verify_command = (
            'test "$(git -C apps/crm_signals rev-parse HEAD)" = "$CRM_SIGNALS_SHA"'
        )
        assert clone_command in workflow
        assert checkout_command in workflow
        assert verify_command in workflow
        assert "bench setup requirements crm_signals" in workflow
        assert "bench get-app --skip-assets crm_signals" not in workflow
        assert workflow.index('test "${#CRM_SIGNALS_SHA}" -eq 40') < workflow.index(
            clone_command
        )
        assert workflow.index(clone_command) < workflow.index(
            checkout_command
        ) < workflow.index(verify_command)
        assert workflow.index(verify_command) < workflow.index(
            "bench setup requirements crm_signals"
        ) < workflow.index("bench --site test.local install-app crm_signals")

def test_support_guides_describe_existing_adapter_and_custom_scope_boundary():
    guide = (ROOT / "docs/CRM_SIGNALS_SUPPORT_CONFIGURATION_GUIDE.html").read_text()
    discovery = (ROOT / "docs/D3_SUPPORT_SLA_DISCOVERY_GUIDE.html").read_text()
    assert (
        "standard Frappe Helpdesk adapter is already implemented"
        in guide
    )
    assert "We build a small adapter" not in guide
    assert "Read-only discovery guide" not in guide
    assert "custom sources require separate approval and scope" in guide
    assert (
        "standard adapter does not cover a custom or different ticket DocType"
        in discovery
    )
    assert "approve a separate adapter scope" in discovery


def test_crm_signals_dashboard_retains_horizontal_inset():
    stylesheet = (
        APP_ROOT / "crm_signals/page/crm_signals_dashboard/crm_signals_dashboard.css"
    ).read_text()
    assert ".crm-signals-dashboard {" in stylesheet
    assert "padding: 20px 24px 32px;" in stylesheet


def test_bench_playwright_workflows_use_lockfile_install_and_mask_e2e_passwords():
    workflow_paths = [
        ROOT / ".github/workflows/bench-e2e.yml",
        ROOT / ".github/workflows/bench-target-v16-5.yml",
    ]
    install = "npm ci --ignore-scripts --no-audit --no-fund"
    browser_install = "npx playwright install --with-deps chromium"

    for path in workflow_paths:
        workflow = path.read_text()
        assert install in workflow
        assert "npm install " not in workflow
        assert workflow.index(install) < workflow.index(browser_install)

        for name in ["sales_password", "employee_password"]:
            mask = f'echo "::add-mask::${name}"'
            output = f'echo "{name}=${name}" >> "$GITHUB_OUTPUT"'
            assert mask in workflow
            assert output in workflow
            assert workflow.index(mask) < workflow.index(output)

def test_playwright_login_wait_supports_frappe_16_5_login_route():
    spec = (ROOT / "e2e/sahdev-dashboard.spec.ts").read_text()
    assert "const url = new URL(response.url());" in spec
    assert '["/login", "/api/method/login"].includes(url.pathname)' in spec
    assert 'response.request().method() === "POST"' in spec



def test_playwright_sales_user_permission_test_checks_authenticated_identity():
    spec = (ROOT / "e2e/sahdev-dashboard.spec.ts").read_text()
    assert '"frappe.auth.get_logged_user"' in spec
    assert ".toBe(email)" in spec
    assert "currentUserRoles" not in spec
    assert "frappe.core.doctype.user.user.get_current_user_roles" not in spec

def test_e2e_non_sales_account_uses_explicit_desk_role():
    source = (APP_ROOT / "ci.py").read_text()
    assert 'E2E_NON_SALES_ROLE = "CRM Signals E2E Non-Sales"' in source
    assert '"desk_access": 1' in source
    assert "non_sales_role = _ensure_e2e_non_sales_role()" in source
    assert "non_sales_role not in employee_roles" in source
    assert 'frappe.throw("E2E non-sales role boundary is invalid")' in source
    assert 'frappe.get_roles("e2e-employee@example.com")' in source

def test_pinned_v16_5_runs_sales_user_direct_form_permission_e2e():
    spec = (ROOT / "e2e/sahdev-dashboard.spec.ts").read_text()
    workflow = (ROOT / ".github/workflows/bench-target-v16-5.yml").read_text()
    assert (
        'test("Sales User CRM Signal form permission boundary"'
        in spec
    )
    assert '"/api/method/frappe.desk.form.load.getdoc"' in spec
    assert '`/app/crm-signal/' in spec
    assert 'response.request().method() === "GET"' in spec
    assert 'url.searchParams.get("doctype") === "CRM Signal"' in spec
    assert 'url.searchParams.get("name") === name' in spec
    assert "expect(restrictedFormResponse.status()).toBe(403)" in spec
    assert "expect(restrictedBody).not.toContain(linkedMessage)" in spec
    assert "expect(allowedFormResponse.status()).toBe(200)" in spec
    assert "expect(loadedSignal?.message).toBe(unlinkedMessage)" in spec
    assert (
        '--grep "Sales User"'
        in workflow
    )


def test_e2e_api_token_credentials_are_private_and_masked():
    source = (APP_ROOT / "ci.py").read_text()
    helper = (APP_ROOT / "ci_api_credentials.py").read_text()
    assert "def prepare_e2e_sales_api_credentials():" in source
    assert (
        "from crm_signals.ci_api_credentials import "
        "prepare_e2e_sales_api_credentials"
    ) in source
    assert "generate_keys(\"e2e-sales-user@example.com\")" in helper
    assert "previous_user = frappe.session.user" in helper
    assert "frappe.set_user(previous_user)" in helper
    assert "os.fchmod(handle.fileno(), 0o600)" in helper
    assert 'return {"credentials_written": True}' in helper

    workflow_paths = [
        ROOT / ".github/workflows/bench-e2e.yml",
        ROOT / ".github/workflows/bench-target-v16-5.yml",
    ]
    for path in workflow_paths:
        workflow = path.read_text()
        assert "prepare_e2e_sales_api_credentials" in workflow
        assert 'echo "::add-mask::$api_key"' in workflow
        assert 'echo "::add-mask::$api_secret"' in workflow
        assert 'echo "api_key=$api_key" >> "$GITHUB_OUTPUT"' in workflow
        assert 'echo "api_secret=$api_secret" >> "$GITHUB_OUTPUT"' in workflow
        assert workflow.index('echo "::add-mask::$api_key"') < workflow.index(
            'echo "api_key=$api_key" >> "$GITHUB_OUTPUT"'
        )
        assert workflow.index('echo "::add-mask::$api_secret"') < workflow.index(
            'echo "api_secret=$api_secret" >> "$GITHUB_OUTPUT"'
        )
        assert 'trap \'rm -f "$credential_file"\' EXIT' in workflow
        assert (
            "E2E_SALES_API_KEY: ${{ steps.sales_api_credentials.outputs.api_key }}"
            in workflow
        )
        assert (
            "E2E_SALES_API_SECRET: ${{ steps.sales_api_credentials.outputs."
            "api_secret }}" in workflow
        )
        assert workflow.index("prepare_e2e_site") < workflow.index(
            "prepare_e2e_sales_api_credentials"
        ) < workflow.index("Run Playwright E2E")


def test_sales_user_api_token_permission_e2e_uses_isolated_node_fetch():
    spec = (ROOT / "e2e/sahdev-dashboard.spec.ts").read_text()
    assert (
        'test("Sales User API token respects linked Lead User Permission"'
        in spec
    )
    helper = spec.split("async function frappeMethodGetWithToken(", 1)[1]
    helper = helper.split("\n}\n", 1)[0]
    assert "process.env.BASE_URL" in helper
    assert "await fetch(" in helper
    assert 'redirect: "manual"' in helper
    assert "page: Page" not in helper
    assert "page.evaluate" not in helper
    assert "Authorization: `token ${apiKey}:${apiSecret}`" in helper
    assert '"frappe.auth.get_logged_user"' in spec
    assert "expect(restrictedRead.status).toBe(403)" in spec
    assert "expect(allowedRead.status).toBe(200)" in spec
    assert "expect(visibleNames).toEqual([unlinkedSignal!.name])" in spec


def test_sales_user_api_token_e2e_checks_response_content_boundary():
    spec = (ROOT / "e2e/sahdev-dashboard.spec.ts").read_text()
    assert "expect(restrictedBody).not.toContain(linkedMessage)" in spec
    assert "expect(allowedBody.message?.message).toBe(unlinkedMessage)" in spec


def test_sales_user_api_token_e2e_preserves_non_json_response_bodies():
    spec = (ROOT / "e2e/sahdev-dashboard.spec.ts").read_text()
    helper = spec.split("async function frappeMethodGetWithToken(", 1)[1]
    helper = helper.split("\n}\n", 1)[0]
    assert "const responseText = await response.text()" in helper
    assert "let body: unknown = responseText" in helper
    assert "body = JSON.parse(responseText)" in helper


def test_sales_user_rest_resource_api_token_permission_e2e_uses_isolated_node_fetch():
    spec = (ROOT / "e2e/sahdev-dashboard.spec.ts").read_text()
    assert (
        'test("Sales User REST resource API token respects linked Lead User Permission"'
        in spec
    )
    helper = spec.split("async function frappeResourceGetWithToken(", 1)[1]
    helper = helper.split("\n}\n", 1)[0]
    assert "process.env.BASE_URL" in helper
    assert "/api/resource/" in helper
    assert "await fetch(url" in helper
    assert 'Accept: "application/json"' in helper
    assert 'redirect: "manual"' in helper
    assert "Authorization" in helper and "apiKey" in helper and "apiSecret" in helper
    assert "page.evaluate" not in helper
    assert "expect(restrictedRead.status).toBe(403)" in spec
    assert "expect(allowedRead.status).toBe(200)" in spec
    assert "expect(allowedData?.name).toBe(unlinkedSignal!.name)" in spec
    assert "expect(visibleNames).toEqual([unlinkedSignal!.name])" in spec
    assert "expect(restrictedBody).not.toContain(linkedMessage)" in spec


def test_sales_user_rest_resource_api_token_e2e_preserves_non_json_bodies():
    spec = (ROOT / "e2e/sahdev-dashboard.spec.ts").read_text()
    helper = spec.split("async function frappeResourceGetWithToken(", 1)[1]
    helper = helper.split("\n}\n", 1)[0]
    assert "const responseText = await response.text()" in helper
    assert "let body: unknown = responseText" in helper
    assert "body = JSON.parse(responseText)" in helper


def test_target_site_acceptance_script_checks_rest_resource_permission_boundary():
    acceptance = (ROOT / "docs/TARGET_SITE_ACCEPTANCE.md").read_text()
    assert '/api/resource/CRM%20Signal/$LINKED_RESTRICTED_SIGNAL' in acceptance
    assert '/api/resource/CRM%20Signal/$UNLINKED_OWNED_SIGNAL' in acceptance
    assert "restricted REST resource expected HTTP 403" in acceptance
    assert "REST resource list did not contain exactly the unlinked owned record" in acceptance



def test_target_site_acceptance_sales_api_smoke_is_valid_bash():
    acceptance = (ROOT / "docs/TARGET_SITE_ACCEPTANCE.md").read_text()
    marker = acceptance.index("set -euo pipefail")
    fence_start = acceptance.rfind("```bash", 0, marker)
    fence_end = acceptance.index("\n```", marker)
    script = acceptance[fence_start + len("```bash") : fence_end]
    subprocess.run(["bash", "-n"], input=script, text=True, check=True)


def test_sales_user_print_permission_requires_row_level_read_access():
    source = (APP_ROOT / "permissions.py").read_text()
    assert 'if permission_type in {"read", "print"}:' in source
    assert "requires row-level read access" in source


def test_sales_user_print_view_e2e_checks_linked_denial_and_owned_access():
    spec = (ROOT / "e2e/sahdev-dashboard.spec.ts").read_text()
    assert (
        'test("Sales User print view respects linked Lead User Permission"'
        in spec
    )
    assert "`/printview?doctype=CRM%20Signal&name=${encodeURIComponent(linkedSignal!.name)}&format=Standard&no_letterhead=1`" in spec
    assert "expect(restrictedResponse?.status()).toBe(403)" in spec
    assert "expect(restrictedBody).not.toContain(linkedMessage)" in spec
    assert "expect(allowedResponse?.status()).toBe(200)" in spec
    assert "expect(allowedBody).toContain(unlinkedMessage)" in spec

def test_sales_user_report_view_and_csv_export_e2e_preserve_row_permissions():
    spec = (ROOT / "e2e/sahdev-dashboard.spec.ts").read_text()
    assert (
        'test("Sales User report view and CSV export respect linked Lead User Permission"'
        in spec
    )
    assert '"frappe.desk.reportview.get_list"' in spec
    assert '"frappe.desk.reportview.export_query"' in spec
    assert "expect(reportRows.map((row) => row.name)).toEqual([" in spec
    assert "expect(csv).not.toContain(linkedSignal!.name)" in spec
    assert "expect(csv).not.toContain(linkedMessage)" in spec

def test_target_site_acceptance_checks_report_view_and_csv_export_permissions():
    acceptance = (ROOT / "docs/TARGET_SITE_ACCEPTANCE.md").read_text()
    assert "frappe.desk.reportview.get_list" in acceptance
    assert "frappe.desk.reportview.export_query" in acceptance
    assert 'LINKED_RESTRICTED_MESSAGE="CRM Signals E2E linked restricted signal"' in acceptance
    assert 'UNLINKED_OWNED_MESSAGE="CRM Signals E2E unlinked owned signal"' in acceptance
    assert "Report View disclosed the linked restricted message" in acceptance
    assert "Report View omitted or changed the unlinked owned record/message" in acceptance
    assert "CSV export disclosed the linked restricted record name/message" in acceptance
    assert "CSV export omitted the unlinked owned record/message" in acceptance
    assert "restricted RPC response disclosed the linked message" in acceptance
    assert "restricted REST resource response disclosed the record name/message" in acceptance
    assert acceptance.count('document.get("message") != sys.argv[3]') == 2
    assert "if sys.argv[2] in rows_text:" in acceptance
    assert "if names != {sys.argv[3]} or sys.argv[4] not in rows_text:" in acceptance
    assert "if sys.argv[2] in csv_text or sys.argv[3] in csv_text:" in acceptance
    assert "if sys.argv[4] not in csv_text or sys.argv[5] not in csv_text:" in acceptance
    assert "if sys.argv[2] in names or sys.argv[4] in recent_text:" in acceptance
    assert "if sys.argv[3] not in names or sys.argv[5] not in recent_text:" in acceptance


def test_sales_user_crm_signals_dashboard_api_preserves_linked_party_permissions():
    spec = (ROOT / "e2e/sahdev-dashboard.spec.ts").read_text()
    assert (
        'test("Sales User CRM Signals dashboard API respects linked Lead User Permission"'
        in spec
    )
    assert '"crm_signals.api.get_dashboard_data"' in spec
    assert "expect(recent.some((row) => row.name === linkedSignal!.name)).toBe(false)" in spec
    assert "expect(recentText).not.toContain(linkedMessage)" in spec


def test_non_sales_dashboard_api_respects_effective_source_permissions():
    spec = (ROOT / "e2e/sahdev-dashboard.spec.ts").read_text()
    assert (
        'test("Users without a Sales role cannot open the Compass"'
        in spec
    )
    assert "expect(compass?.leads?.available).toBe(false)" in spec
    assert "expect(compass?.opportunities?.available).toBe(false)" in spec
    assert "expect(compass?.billing?.available).toBe(false)" in spec
    assert "expect(compass?.service?.available).toBe(false)" in spec
    assert "expect(signalsResponse.status).toBe(403)" in spec


def test_target_site_acceptance_checks_non_sales_dashboard_api_permissions():
    acceptance = (ROOT / "docs/TARGET_SITE_ACCEPTANCE.md").read_text()
    assert "EXPECTED_NON_SALES_USER" in acceptance
    assert "CRM_SIGNALS_NON_SALES_API_KEY" in acceptance
    assert "CRM_SIGNALS_NON_SALES_API_SECRET" in acceptance
    assert "curl --disable --proto" in acceptance
    assert "non-sales CRM Signals dashboard expected HTTP 403" in acceptance
    assert "crm_signals.api.get_sales_compass_data" in acceptance
    assert "non-sales source without read permission was marked available" in acceptance


def test_target_site_permission_matrix_tracks_each_access_path_independently():
    acceptance = (ROOT / "docs/TARGET_SITE_ACCEPTANCE.md").read_text()
    matrix = acceptance.split("## 4. Permission parity matrix", 1)[1].split(
        "### Direct CRM Signal form loading", 1
    )[0]
    for access_path in (
        "Signal list",
        "Direct signal form",
        "RPC API",
        "REST resource API",
        "Report View",
        "CSV export",
        "Print view",
        "Dashboard UI",
        "Dashboard API",
        "Digest email",
        "Realtime",
    ):
        assert f"| {access_path} |" in matrix
    assert "Do not infer a result from another column" in matrix


def test_operator_shell_examples_parse_without_execution():
    documents = (
        "README.md",
        "docs/ADMIN_GUIDE.md",
        "docs/DEPLOYMENT_RUNBOOK.md",
        "docs/TARGET_SITE_ACCEPTANCE.md",
    )
    shell_fence = re.compile(
        r"\x60{3}(?:bash|sh|shell)\s*\n(.*?)\x60{3}", re.DOTALL
    )

    for relative_path in documents:
        content = (ROOT / relative_path).read_text()
        scripts = shell_fence.findall(content)
        assert scripts, relative_path

        for block_number, script in enumerate(scripts, start=1):
            result = subprocess.run(
                ["bash", "-n"],
                input=script,
                text=True,
                capture_output=True,
                check=False,
            )
            assert result.returncode == 0, (
                f"{relative_path} shell block {block_number} is invalid:\n"
                f"{result.stderr}"
            )
