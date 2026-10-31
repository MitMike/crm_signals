"""Fast tests that do not require a running Frappe bench."""

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_doctype_json_is_valid_and_field_options_are_consistent():
    metadata = json.loads(
        (ROOT / "crm_signals/doctype/crm_signal/crm_signal.json").read_text()
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
    for path in (ROOT / "crm_signals").rglob("*.py"):
        ast.parse(path.read_text(), filename=str(path))


def test_webhook_is_not_guest_whitelisted_or_permission_bypassed():
    source = (ROOT / "crm_signals/api.py").read_text()
    tree = ast.parse(source)
    target = next(
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "ingest_signal"
    )
    decorators = [ast.unparse(item) for item in target.decorator_list]
    assert decorators == ["frappe.whitelist()"]
    assert "ignore_permissions=True" not in source
    assert "frappe.db.commit()" not in source
    assert "allow_guest=True" not in source


def test_event_handlers_notify_through_shared_recipient_resolver():
    source = (ROOT / "crm_signals/events.py").read_text()
    assert "notify_signal(signal)" in source
    assert "frappe.publish_realtime(" not in source
