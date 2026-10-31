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
    monkeypatch.setitem(sys.modules, "frappe", fake)
    sys.modules.pop("crm_signals.permissions", None)
    return importlib.import_module("crm_signals.permissions")


class Signal:
    owner = "integration@example.com"
    lead = "LEAD-0001"
    customer = None
    recipient_tokens = ""


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


def test_sales_user_list_query_limits_to_owner_assignment_or_own_signal(monkeypatch):
    permissions = load_permissions(monkeypatch)
    condition = permissions.crm_signal_query("rep@example.com")
    assert "recipient_tokens" in condition
    assert "SELECT" not in condition.upper()
    assert "UNION" not in condition.upper()
    assert "rep@example.com" in condition



def test_persisted_recipient_token_grants_related_read_access(monkeypatch):
    permissions = load_permissions(
        monkeypatch, parent_access=True,
        owners={("Lead", "LEAD-0001"): "lead-owner@example.com"},
    )
    signal = Signal()
    signal.recipient_tokens = "|" + permissions._recipient_token("rep@example.com") + "|"
    assert permissions.crm_signal_has_permission(signal, "rep@example.com", "read") is True


def test_recipient_list_query_uses_hashed_token_without_subqueries(monkeypatch):
    permissions = load_permissions(monkeypatch)
    condition = permissions.crm_signal_query("rep@example.com")
    assert permissions._recipient_token("rep@example.com") in condition
    assert "recipient_tokens LIKE" in condition
    assert "SELECT" not in condition.upper()
    assert "UNION" not in condition.upper()
