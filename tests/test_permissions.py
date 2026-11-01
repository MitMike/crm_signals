"""Unit tests for CRM Signal record access policy."""

import importlib
import sys
import types


class FakeDB:
    def __init__(self, owners=None, assigned=False):
        self.owners = owners or {}
        self.assigned = assigned

    def get_value(self, doctype, name, field):
        return self.owners.get((doctype, name))

    def exists(self, *args, **kwargs):
        return self.assigned

    def escape(self, value):
        return "'" + value.replace("'", "''") + "'"


def load_permissions(monkeypatch, roles=None, parent_access=True, assigned=False, owners=None):
    fake = types.ModuleType("frappe")
    fake.session = types.SimpleNamespace(user="rep@example.com")
    fake.db = FakeDB(owners, assigned)
    fake.get_roles = lambda user: roles or ["Sales User"]
    fake.has_permission = lambda *args, **kwargs: parent_access
    fake.PermissionError = type("PermissionError", (Exception,), {})

    def get_list(doctype, filters=None, pluck=None, **kwargs):
        if not parent_access:
            return []
        if doctype == "Lead" and filters == {"owner": "rep@example.com"}:
            return ["LEAD-OWNED"]
        if doctype == "Customer" and filters == {"owner": "rep@example.com"}:
            return ["CUST-OWNED"]
        if doctype == "Lead" and filters and filters.get("name"):
            return ["LEAD-ASSIGNED"]
        if doctype == "Customer" and filters and filters.get("name"):
            return ["CUST-ASSIGNED"]
        return []

    def get_all(doctype, filters=None, pluck=None):
        if doctype == "ToDo" and filters and filters.get("reference_type") == "Lead":
            return ["LEAD-ASSIGNED"]
        if doctype == "ToDo" and filters and filters.get("reference_type") == "Customer":
            return ["CUST-ASSIGNED"]
        return []

    fake.get_list = get_list
    fake.get_all = get_all
    monkeypatch.setitem(sys.modules, "frappe", fake)
    sys.modules.pop("crm_signals.permissions", None)
    return importlib.import_module("crm_signals.permissions")


class Signal:
    owner = "integration@example.com"
    lead = "LEAD-0001"
    customer = None


def test_manager_permission_falls_back_to_doc_type_permissions(monkeypatch):
    permissions = load_permissions(monkeypatch, roles=["Sales Manager"])
    assert permissions.crm_signal_has_permission(Signal(), "manager@example.com", "read") is None


def test_sales_user_read_requires_parent_read_permission(monkeypatch):
    permissions = load_permissions(
        monkeypatch, parent_access=False, assigned=True,
        owners={("Lead", "LEAD-0001"): "owner@example.com"},
    )
    assert permissions.crm_signal_has_permission(Signal(), "rep@example.com", "read") is False


def test_active_assignee_can_read_and_write_related_signal(monkeypatch):
    permissions = load_permissions(
        monkeypatch, parent_access=True, assigned=True,
        owners={("Lead", "LEAD-0001"): "owner@example.com"},
    )
    signal = Signal()
    assert permissions.crm_signal_has_permission(signal, "rep@example.com", "read") is True
    assert permissions.crm_signal_has_permission(signal, "rep@example.com", "write") is True


def test_parent_owner_can_read_and_write_related_signal(monkeypatch):
    permissions = load_permissions(
        monkeypatch, parent_access=True,
        owners={("Lead", "LEAD-0001"): "rep@example.com"},
    )
    signal = Signal()
    assert permissions.crm_signal_has_permission(signal, "rep@example.com", "read") is True
    assert permissions.crm_signal_has_permission(signal, "rep@example.com", "write") is True


def test_unrelated_sales_user_cannot_read_signal_even_if_parent_read_is_allowed(monkeypatch):
    permissions = load_permissions(
        monkeypatch, parent_access=True,
        owners={("Lead", "LEAD-0001"): "someone-else@example.com"},
    )
    assert permissions.crm_signal_has_permission(Signal(), "rep@example.com", "read") is False


def test_unlinked_signal_is_not_visible_to_unrelated_sales_user(monkeypatch):
    permissions = load_permissions(monkeypatch)
    signal = Signal()
    signal.lead = None
    assert permissions.crm_signal_has_permission(signal, "rep@example.com", "read") is False


def test_sales_user_list_query_uses_permission_aware_flat_in_lists(monkeypatch):
    permissions = load_permissions(monkeypatch)
    condition = permissions.crm_signal_query("rep@example.com")
    assert "`lead` IN" in condition
    assert "`customer` IN" in condition
    assert "LEAD-OWNED" in condition
    assert "LEAD-ASSIGNED" in condition
    assert "CUST-OWNED" in condition
    assert "SELECT" not in condition.upper()
    assert "UNION" not in condition.upper()

def test_list_query_owner_clause_is_limited_to_unlinked_signals(monkeypatch):
    permissions = load_permissions(monkeypatch, parent_access=False)
    condition = permissions.crm_signal_query("rep@example.com")

    assert "`tabCRM Signal`.owner" in condition
    assert "`tabCRM Signal`.lead IS NULL" in condition
    assert "`tabCRM Signal`.customer IS NULL" in condition
    assert "`lead` IN" not in condition
    assert "`customer` IN" not in condition
