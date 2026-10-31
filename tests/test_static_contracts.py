"""Fast tests that do not require a running Frappe bench."""

import ast
import json
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
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
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
    assert page_style.is_file()
    assert 'frappe.pages["crm-signals-dashboard"]' in page_script
    assert 'method: "crm_signals.api.get_dashboard_data"' in page_script

    workspace = json.loads(
        (APP_ROOT / "crm_signals/workspace/crm_signals/crm_signals.json").read_text()
    )
    assert workspace["title"] == "CRM Signals"
    assert json.loads(workspace["content"])[0]["type"] == "shortcut"
    assert workspace["shortcuts"][0]["link_to"] == "crm-signals-dashboard"

    api = (APP_ROOT / "api.py").read_text()
    assert "def get_dashboard_data():" in api
    assert 'frappe.get_list("CRM Signal"' in api
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
