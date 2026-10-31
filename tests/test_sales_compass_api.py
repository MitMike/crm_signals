"""Tests for the S.A.H.D.E.V. sales compass endpoint without a live bench."""

import importlib
import sys
import types


def load_sales_api(monkeypatch, *, lead_read=True, opportunity_read=True, invoice_read=True, payment_read=True, user="sales@example.com", version="15.0.0"):
    frappe = types.ModuleType("frappe")
    frappe.__path__ = []
    frappe._ = lambda message: message
    frappe.whitelist = lambda **kwargs: (lambda function: function)
    frappe.session = types.SimpleNamespace(user=user)
    frappe.__version__ = version

    class AuthenticationError(Exception):
        pass

    class PermissionError(Exception):
        pass

    frappe.AuthenticationError = AuthenticationError
    frappe.PermissionError = PermissionError

    class FakeDB:
        def exists(self, doctype, name):
            return doctype == "DocType" and name in {"Lead", "Opportunity", "Sales Invoice", "Payment Entry"}

    frappe.db = FakeDB()
    frappe.has_permission = lambda doctype, ptype="read": {
        "Lead": lead_read,
        "Opportunity": opportunity_read,
        "Sales Invoice": invoice_read,
        "Payment Entry": payment_read,
    }.get(doctype, True)

    class FakeMeta:
        fields = {
            "Lead": {"status"},
            "Opportunity": {
                "status", "opportunity_amount", "currency", "creation",
                "opportunity_from", "party_name", "customer_name", "expected_closing",
            },
            "Sales Invoice": {
                "currency", "posting_date", "grand_total", "outstanding_amount",
                "is_return", "is_pos", "paid_amount", "due_date", "customer",
                "customer_name", "party_account_currency",
            },
            "Payment Entry": {
                "payment_type", "party_type", "posting_date", "received_amount",
                "paid_to_account_currency",
            },
        }

        def __init__(self, doctype):
            self.doctype = doctype

        def has_field(self, fieldname):
            return fieldname in self.fields.get(self.doctype, set())

    frappe.get_meta = lambda doctype: FakeMeta(doctype)

    queries = []

    def get_list(doctype, fields=None, filters=None, **kwargs):
        query = {"doctype": doctype, "fields": fields, "filters": filters, **kwargs}
        queries.append(query)

        if doctype == "Sales Invoice":
            if filters and "due_date" in filters:
                if "customer" in fields:
                    return [{
                        "name": "SINV-OVERDUE-1",
                        "customer": "CUST-0001",
                        "customer_name": "Acme Ltd",
                        "posting_date": "2026-10-01",
                        "due_date": "2026-10-15",
                        "currency": "USD",
                        "party_account_currency": "INR",
                        "outstanding_amount": 45000,
                    }]
                return [{"total": 2}]
            if filters and filters.get("is_pos") == 1:
                return [
                    {"currency": "INR", "total_amount": 3000, "record_count": 2}
                ]
            if filters and "outstanding_amount" in filters:
                return [
                    {"party_account_currency": "INR", "total_amount": 75000, "record_count": 2},
                    {"party_account_currency": "EUR", "total_amount": 300, "record_count": 1},
                ]
            return [
                {"currency": "INR", "total_amount": 250000, "record_count": 3},
                {"currency": "USD", "total_amount": 1000, "record_count": 1},
            ]

        if doctype == "Payment Entry":
            return [
                {"paid_to_account_currency": "INR", "total_amount": 55000, "record_count": 2},
                {"paid_to_account_currency": "USD", "total_amount": 500, "record_count": 1},
            ]

        if doctype == "Lead" and filters and "creation" in filters:
            return [{"total": 5}]
        if doctype == "Lead":
            return [
                {"status": "Open", "total": 7},
                {"status": "Converted", "total": 2},
                {"status": "Do Not Contact", "total": 1},
            ]
        if doctype == "Opportunity" and "name" in fields:
            return [
                {
                    "name": "OPP-0001",
                    "creation": "2026-10-31 09:00:00",
                    "status": "Open",
                    "opportunity_from": "Customer",
                    "party_name": "Acme Ltd",
                    "opportunity_amount": 120000,
                    "currency": "INR",
                    "expected_closing": "2026-11-15",
                }
            ]
        return [
            {"status": "Open", "currency": "INR", "total": 2, "total_amount": 120000},
            {"status": "Quotation", "currency": "INR", "total": 1, "total_amount": 60000},
            {"status": "Lost", "currency": "INR", "total": 1, "total_amount": 25000},
            {"status": "Open", "currency": "USD", "total": 1, "total_amount": 3000},
        ]

    frappe.get_list = get_list
    frappe.throw = lambda message, exc=None: (_ for _ in ()).throw((exc or Exception)(message))

    utils = types.ModuleType("frappe.utils")
    utils.nowdate = lambda: "2026-10-31"
    utils.add_days = lambda date, days: "2026-10-01"

    monkeypatch.setitem(sys.modules, "frappe", frappe)
    monkeypatch.setitem(sys.modules, "frappe.utils", utils)
    sys.modules.pop("crm_signals.api", None)
    return importlib.import_module("crm_signals.api"), queries, frappe


def test_sales_compass_returns_permission_filtered_lead_and_opportunity_metrics(monkeypatch):
    api, queries, _ = load_sales_api(monkeypatch)

    result = api.get_sales_compass_data()

    assert result["period_days"] == 30
    assert result["leads"] == {
        "available": True,
        "created_last_30_days": 5,
        "active": 7,
    }
    opportunities = result["opportunities"]
    assert opportunities["available"] is True
    assert opportunities["total_count"] == 5
    assert opportunities["active_count"] == 4
    assert opportunities["stages"] == [
        {"status": "Open", "total": 3},
        {"status": "Quotation", "total": 1},
    ]
    assert opportunities["pipeline_by_currency"] == [
        {"currency": "INR", "total_amount": 180000.0},
        {"currency": "USD", "total_amount": 3000.0},
    ]
    assert opportunities["recent"][0]["name"] == "OPP-0001"
    assert all("ignore_permissions" not in query for query in queries)
    assert all(query["doctype"] in {"Lead", "Opportunity", "Sales Invoice", "Payment Entry"} for query in queries)

    billing = result["billing"]
    assert billing["available"] is True
    assert billing["invoiced_available"] is True
    assert billing["invoiced_by_currency"] == [
        {"currency": "INR", "total_amount": 250000.0, "record_count": 3},
        {"currency": "USD", "total_amount": 1000.0, "record_count": 1},
    ]
    assert billing["outstanding_by_currency"] == [
        {"party_account_currency": "INR", "total_amount": 75000.0, "record_count": 2},
        {"party_account_currency": "EUR", "total_amount": 300.0, "record_count": 1},
    ]
    assert billing["customer_receipts_by_currency"] == [
        {"currency": "INR", "total_amount": 55000.0, "record_count": 2},
        {"currency": "USD", "total_amount": 500.0, "record_count": 1},
    ]
    assert billing["pos_receipts_by_currency"] == [
        {"currency": "INR", "total_amount": 3000.0, "record_count": 2},
    ]
    assert billing["overdue_count"] == 2
    assert billing["overdue_invoices"][0]["name"] == "SINV-OVERDUE-1"
    assert all("ignore_permissions" not in query for query in queries)
    assert all(query["doctype"] in {"Lead", "Opportunity", "Sales Invoice", "Payment Entry"} for query in queries)


def test_sales_compass_marks_unreadable_sources_unavailable(monkeypatch):
    api, _, _ = load_sales_api(monkeypatch, lead_read=False, opportunity_read=False)

    result = api.get_sales_compass_data()

    assert result["leads"]["available"] is False
    assert result["opportunities"]["available"] is False
    assert result["leads"]["created_last_30_days"] is None


def test_sales_compass_requires_authenticated_user(monkeypatch):
    api, _, frappe = load_sales_api(monkeypatch, user="Guest")
    try:
        api.get_sales_compass_data()
    except Exception as exc:
        assert isinstance(exc, frappe.AuthenticationError)
    else:
        raise AssertionError("Guest must not be able to read the sales compass")



def test_sales_compass_uses_structured_aggregates_on_frappe_v16(monkeypatch):
    api, queries, _ = load_sales_api(monkeypatch, version="16.0.0")

    result = api.get_sales_compass_data()

    assert result["opportunities"]["active_count"] == 4
    assert any(
        isinstance(field, dict) and field.get("COUNT") == "*"
        for query in queries
        for field in query["fields"]
    )
    assert any(
        isinstance(field, dict) and field.get("SUM") == "opportunity_amount"
        for query in queries
        for field in query["fields"]
    )



def test_billing_marks_sales_invoice_source_unavailable_without_permission(monkeypatch):
    api, queries, _ = load_sales_api(monkeypatch, invoice_read=False)

    result = api.get_sales_compass_data()["billing"]

    assert result["available"] is False
    assert result["invoiced_available"] is False
    assert result["outstanding_available"] is False
    assert not any(query["doctype"] == "Sales Invoice" for query in queries)


def test_billing_marks_payment_entry_receipts_unavailable_without_permission(monkeypatch):
    api, queries, _ = load_sales_api(monkeypatch, payment_read=False)

    result = api.get_sales_compass_data()["billing"]

    assert result["available"] is True
    assert result["customer_receipts_available"] is False
    assert result["customer_receipts_by_currency"] == []
    assert any(query["doctype"] == "Sales Invoice" for query in queries)


def test_billing_uses_structured_aggregate_fields_on_frappe_v16(monkeypatch):
    api, queries, _ = load_sales_api(monkeypatch, version="16.0.0")

    result = api.get_sales_compass_data()["billing"]

    assert result["invoiced_available"] is True
    assert any(
        isinstance(field, dict) and field.get("SUM") == "grand_total"
        for query in queries if query["doctype"] == "Sales Invoice"
        for field in query["fields"]
    )
    assert any(
        isinstance(field, dict) and field.get("SUM") == "received_amount"
        for query in queries if query["doctype"] == "Payment Entry"
        for field in query["fields"]
    )
