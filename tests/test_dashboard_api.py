"""Tests for the CRM Signals dashboard API without a live bench."""

import importlib
import sys
import types


def load_api(monkeypatch, user="sales.user@example.com", allowed=True, version="15.0.0"):
    frappe = types.ModuleType("frappe")
    frappe.__path__ = []
    frappe._ = lambda message: message
    frappe.whitelist = lambda **kwargs: (lambda function: function)
    frappe.session = types.SimpleNamespace(user=user)
    frappe.__version__ = version
    frappe.has_permission = lambda *args, **kwargs: allowed

    class AuthenticationError(Exception):
        pass

    class PermissionError(Exception):
        pass

    frappe.AuthenticationError = AuthenticationError
    frappe.PermissionError = PermissionError
    frappe.ValidationError = type("ValidationError", (Exception,), {})
    frappe.MandatoryError = type("MandatoryError", (Exception,), {})
    frappe.LinkValidationError = type("LinkValidationError", (Exception,), {})

    def throw(message, exc=None):
        raise (exc or Exception)(message)

    frappe.throw = throw
    queries = []

    aggregate_count = {"COUNT": "*", "as": "total"} if int(version.split(".")[0]) >= 16 else "count(name) as total"

    def get_list(doctype, fields=None, filters=None, **kwargs):
        queries.append({"doctype": doctype, "fields": fields, "filters": filters, **kwargs})
        if fields == [aggregate_count]:
            if not filters:
                return [{"total": 14}]
            if filters.get("is_read") == 0:
                return [{"total": 6}]
            if filters.get("priority") == ["in", ["High", "Urgent"]]:
                return [{"total": 3}]
            if "creation" in filters:
                return [{"total": 4}]
        if fields == ["signal_type", aggregate_count]:
            return [
                types.SimpleNamespace(signal_type="Website Visit", total=9),
                types.SimpleNamespace(signal_type="High-Value Quote", total=5),
            ]
        if "message" in fields:
            return [
                {
                    "name": "SIG-0001",
                    "creation": "2026-10-31 09:00:00",
                    "signal_type": "Website Visit",
                    "priority": "High",
                    "message": "Visited pricing page",
                    "lead": "LEAD-0001",
                    "customer": None,
                    "is_read": 0,
                }
            ]
        raise AssertionError(f"Unexpected query: {fields!r}")

    frappe.get_list = get_list
    utils = types.ModuleType("frappe.utils")
    utils.add_days = lambda date, days: "2026-10-24"
    utils.nowdate = lambda: "2026-10-31"

    monkeypatch.setitem(sys.modules, "frappe", frappe)
    monkeypatch.setitem(sys.modules, "frappe.utils", utils)
    sys.modules.pop("crm_signals.api", None)
    module = importlib.import_module("crm_signals.api")
    return module, queries, frappe


def test_dashboard_returns_permission_filtered_metrics_and_recent_signals(monkeypatch):
    api, queries, _ = load_api(monkeypatch)
    result = api.get_dashboard_data()

    assert result["stats"] == {
        "total": 14,
        "unread": 6,
        "high_priority": 3,
        "last_7_days": 4,
    }
    assert result["by_type"] == [
        {"signal_type": "Website Visit", "total": 9},
        {"signal_type": "High-Value Quote", "total": 5},
    ]
    assert result["recent"][0]["name"] == "SIG-0001"
    assert all(query["doctype"] == "CRM Signal" for query in queries)
    assert all("ignore_permissions" not in query for query in queries)


def test_dashboard_requires_authenticated_user(monkeypatch):
    api, _, _ = load_api(monkeypatch, user="Guest")
    try:
        api.get_dashboard_data()
    except Exception as exc:
        assert isinstance(exc, api.frappe.AuthenticationError)
    else:
        raise AssertionError("Guest should not be able to read dashboard data")


def test_dashboard_requires_read_permission(monkeypatch):
    api, _, _ = load_api(monkeypatch, allowed=False)
    try:
        api.get_dashboard_data()
    except Exception as exc:
        assert isinstance(exc, api.frappe.PermissionError)
    else:
        raise AssertionError("User without CRM Signal read permission must be rejected")



def test_dashboard_uses_structured_aggregates_on_frappe_v16(monkeypatch):
    api, queries, _ = load_api(monkeypatch, version="16.0.0")
    result = api.get_dashboard_data()

    assert result["stats"]["total"] == 14
    assert any(
        query["fields"] == [{"COUNT": "*", "as": "total"}]
        for query in queries
    )
    assert any(
        query["fields"] == ["signal_type", {"COUNT": "*", "as": "total"}]
        for query in queries
    )
