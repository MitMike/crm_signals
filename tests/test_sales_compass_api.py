"""Tests for the S.A.H.D.E.V. sales compass endpoint without a live bench."""

import importlib
import sys
import types


def _sales_invoice_rows(fields, filters):
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
        return [{"currency": "INR", "total_amount": 3000, "record_count": 2}]
    if filters and "outstanding_amount" in filters:
        return [
            {"party_account_currency": "INR", "total_amount": 75000, "record_count": 2},
            {"party_account_currency": "EUR", "total_amount": 300, "record_count": 1},
        ]
    return [
        {"currency": "INR", "total_amount": 250000, "record_count": 3},
        {"currency": "USD", "total_amount": 1000, "record_count": 1},
    ]


def _payment_entry_rows(fields, filters):
    return [
        {"paid_to_account_currency": "INR", "total_amount": 55000, "record_count": 2},
        {"paid_to_account_currency": "USD", "total_amount": 500, "record_count": 1},
    ]


def _lead_rows(fields, filters):
    if filters and "creation" in filters:
        return [{"total": 5}]
    return [
        {"status": "Open", "total": 7},
        {"status": "Converted", "total": 2},
        {"status": "Do Not Contact", "total": 1},
    ]


def _opportunity_rows(fields, filters):
    if "name" in fields:
        return [{
            "name": "OPP-0001",
            "creation": "2026-10-31 09:00:00",
            "status": "Open",
            "opportunity_from": "Customer",
            "party_name": "Acme Ltd",
            "opportunity_amount": 120000,
            "currency": "INR",
            "expected_closing": "2026-11-15",
        }]
    return [
        {"status": "Open", "currency": "INR", "total": 2, "total_amount": 120000},
        {"status": "Quotation", "currency": "INR", "total": 1, "total_amount": 60000},
        {"status": "Lost", "currency": "INR", "total": 1, "total_amount": 25000},
        {"status": "Open", "currency": "USD", "total": 1, "total_amount": 3000},
    ]


def _helpdesk_rows(fields, filters):
    if "status_category" in fields and "agreement_status" not in fields:
        return [
            {"status_category": "Open", "total": 4},
            {"status_category": "Paused", "total": 2},
            {"status_category": "Resolved", "total": 5},
        ]
    if "agreement_status" in fields:
        return [
            {"agreement_status": "Fulfilled", "total": 8},
            {"agreement_status": "Failed", "total": 2},
            {"agreement_status": "Paused", "total": 1},
            {"agreement_status": "Resolution Due", "total": 3},
        ]
    if fields and any((isinstance(field, dict) and field.get("AVG")) or (isinstance(field, str) and "avg(" in field.lower()) for field in fields):
        return [{"average_resolution_seconds": 7200}]
    if filters and "resolution_date" in filters:
        return [{"total": 5}]
    if filters and "sla" in filters:
        return [{"total": 6}]
    return [{"total": 12}]


def _fake_get_list(queries):
    handlers = {
        "Sales Invoice": _sales_invoice_rows,
        "Payment Entry": _payment_entry_rows,
        "HD Ticket": lambda fields, filters: _helpdesk_rows(fields, filters),
        "Lead": _lead_rows,
        "Opportunity": _opportunity_rows,
    }

    def get_list(doctype, fields=None, filters=None, **kwargs):
        queries.append({"doctype": doctype, "fields": fields, "filters": filters, **kwargs})
        handler = handlers.get(doctype)
        return handler(fields, filters) if handler else []

    return get_list


def load_sales_api(
    monkeypatch,
    *,
    lead_read=True,
    opportunity_read=True,
    invoice_read=True,
    payment_read=True,
    helpdesk_read=True,
    sla_read=True,
    helpdesk_permitted_fields=None,
    lead_has_status=True,
    opportunity_has_status=True,
    invoice_has_is_return=True,
    user="sales@example.com",
    version="15.0.0",
    helpdesk_creation_column=True,
):
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
            return doctype == "DocType" and name in {"Lead", "Opportunity", "Sales Invoice", "Payment Entry", "HD Ticket", "HD Service Level Agreement"}

        def has_column(self, doctype, column):
            return doctype == "HD Ticket" and column == "creation" and helpdesk_creation_column

    frappe.db = FakeDB()
    permissions = {
        "Lead": lead_read,
        "Opportunity": opportunity_read,
        "Sales Invoice": invoice_read,
        "Payment Entry": payment_read,
        "HD Ticket": helpdesk_read,
        "HD Service Level Agreement": sla_read,
    }
    frappe.has_permission = lambda doctype, ptype="read": permissions.get(doctype, True)

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
            "HD Ticket": {"status_category", "resolution_date", "resolution_time", "sla", "agreement_status"},
            "HD Service Level Agreement": {"service_level", "enabled", "default_sla"},
        }

        def __init__(self, doctype):
            self.doctype = doctype

        def has_field(self, fieldname):
            configured_fields = {
                ("Lead", "status"): lead_has_status,
                ("Opportunity", "status"): opportunity_has_status,
                ("Sales Invoice", "is_return"): invoice_has_is_return,
            }
            if (self.doctype, fieldname) in configured_fields:
                return configured_fields[(self.doctype, fieldname)]
            return fieldname in self.fields.get(self.doctype, set())

        def get_permitted_fieldnames(self, user=None, permission_type="read"):
            if self.doctype == "HD Ticket" and helpdesk_permitted_fields is not None:
                return list(helpdesk_permitted_fields)
            return list(self.fields.get(self.doctype, set()))

    frappe.get_meta = lambda doctype: FakeMeta(doctype)
    queries = []
    frappe.get_list = _fake_get_list(queries)
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
        "active_available": True,
        "active": 7,
    }
    opportunities = result["opportunities"]
    assert opportunities["available"] is True
    assert opportunities["total_count"] == 5
    assert opportunities["status_available"] is True
    assert opportunities["stages_available"] is True
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
    assert all(query["doctype"] in {"Lead", "Opportunity", "Sales Invoice", "Payment Entry", "HD Ticket"} for query in queries)

    billing = result["billing"]
    assert billing["available"] is True
    assert billing["invoiced_available"] is True
    assert billing["invoiced_by_currency"] == [
        {"currency": "INR", "total_amount": 250000.0, "record_count": 3},
        {"currency": "USD", "total_amount": 1000.0, "record_count": 1},
    ]
    assert billing["outstanding_by_currency"] == [
        {"currency": "INR", "total_amount": 75000.0, "record_count": 2},
        {"currency": "EUR", "total_amount": 300.0, "record_count": 1},
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
    assert all(query["doctype"] in {"Lead", "Opportunity", "Sales Invoice", "Payment Entry", "HD Ticket"} for query in queries)


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

def test_sales_compass_marks_active_leads_unavailable_without_status_metadata(monkeypatch):
    api, queries, _ = load_sales_api(monkeypatch, lead_has_status=False)

    result = api.get_sales_compass_data()

    assert result["leads"]["available"] is True
    assert result["leads"]["created_last_30_days"] == 5
    assert result["leads"]["active_available"] is False
    assert result["leads"]["active"] is None
    assert not any(
        query["doctype"] == "Lead" and query.get("group_by") == "status"
        for query in queries
    )


def test_sales_compass_marks_opportunity_status_dependent_metrics_unavailable(monkeypatch):
    api, queries, _ = load_sales_api(monkeypatch, opportunity_has_status=False)

    result = api.get_sales_compass_data()
    opportunities = result["opportunities"]

    assert opportunities["available"] is True
    assert opportunities["total_count"] == 5
    assert opportunities["status_available"] is False
    assert opportunities["active_count"] is None
    assert opportunities["stages_available"] is False
    assert opportunities["stages"] == []
    assert opportunities["pipeline_value_available"] is False
    assert opportunities["pipeline_by_currency"] == []
    assert opportunities["recent"][0]["name"] == "OPP-0001"
    aggregate = next(
        query for query in queries
        if query["doctype"] == "Opportunity" and "name" not in query["fields"]
    )
    assert aggregate["group_by"] is None
    assert all(
        not isinstance(field, dict) or field.get("SUM") != "opportunity_amount"
        for field in aggregate["fields"]
    )


def test_billing_marks_return_sensitive_invoice_metrics_unavailable_without_is_return(monkeypatch):
    api, queries, _ = load_sales_api(monkeypatch, invoice_has_is_return=False)

    result = api.get_sales_compass_data()["billing"]

    assert result["available"] is True
    assert result["invoiced_available"] is False
    assert "is_return" in result["sales_invoice_unavailable_reason"]
    assert result["invoiced_by_currency"] == []
    assert result["outstanding_available"] is False
    assert result["outstanding_by_currency"] == []
    assert result["pos_receipts_available"] is False
    assert result["pos_receipts_by_currency"] == []
    assert result["overdue_available"] is False
    assert result["overdue_count"] is None
    assert result["overdue_invoices"] == []
    assert result["customer_receipts_available"] is True
    assert not any(query["doctype"] == "Sales Invoice" for query in queries)
    assert any(query["doctype"] == "Payment Entry" for query in queries)



def test_helpdesk_service_metrics_use_status_category_and_native_sla_outcomes(monkeypatch):
    api, queries, _ = load_sales_api(monkeypatch)
    result = api.get_sales_compass_data()["service"]

    assert result["source"] == "Frappe Helpdesk"
    assert result["available"] is True
    assert result["created_last_30_days"] == 12
    assert result["open_backlog"] == 4
    assert result["paused_backlog"] == 2
    assert result["resolved_last_30_days"] == 5
    assert result["average_resolution_hours"] == 2
    assert result["sla_eligible"] == 10
    assert result["sla_fulfilled"] == 8
    assert result["sla_failed"] == 2
    assert result["sla_compliance_percent"] == 80
    assert all("ignore_permissions" not in query for query in queries)
    assert not any("subject" in (query.get("fields") or []) for query in queries)


def test_helpdesk_ticket_metrics_available_when_sla_policy_is_not_readable(monkeypatch):
    api, _, _ = load_sales_api(monkeypatch, sla_read=False)
    result = api.get_sales_compass_data()["service"]

    assert result["available"] is True
    assert result["open_backlog"] == 4
    assert result["sla_available"] is False
    assert result["sla_compliance_percent"] is None


def test_helpdesk_metrics_unavailable_without_ticket_permission(monkeypatch):
    api, queries, _ = load_sales_api(monkeypatch, helpdesk_read=False)
    result = api.get_sales_compass_data()["service"]

    assert result["available"] is False
    assert result["created_last_30_days"] is None
    assert not any(query["doctype"] == "HD Ticket" for query in queries)


def test_helpdesk_metrics_do_not_report_zero_when_field_level_read_is_missing(monkeypatch):
    api, queries, _ = load_sales_api(
        monkeypatch,
        helpdesk_permitted_fields={"creation"},
    )
    result = api.get_sales_compass_data()["service"]

    assert result["available"] is True
    assert result["created_last_30_days"] == 12
    assert result["backlog_available"] is False
    assert result["open_backlog"] is None
    assert result["paused_backlog"] is None
    assert result["resolved_available"] is False
    assert result["resolution_time_available"] is False
    assert result["sla_available"] is False
    assert not any(
        query["doctype"] == "HD Ticket"
        and query.get("group_by") == "status_category"
        for query in queries
    )
    assert not any(
        query["doctype"] == "HD Ticket"
        and query.get("group_by") == "agreement_status"
        for query in queries
    )


def test_helpdesk_metrics_are_independently_available_for_permitted_fields(monkeypatch):
    api, queries, _ = load_sales_api(
        monkeypatch,
        helpdesk_permitted_fields={"creation", "status_category"},
    )
    result = api.get_sales_compass_data()["service"]

    assert result["available"] is True
    assert result["backlog_available"] is True
    assert result["open_backlog"] == 4
    assert result["paused_backlog"] == 2
    assert result["resolved_available"] is False
    assert result["sla_available"] is False
    assert not any(
        query["doctype"] == "HD Ticket" and "resolution_date" in (query.get("filters") or {})
        for query in queries
    )

def test_helpdesk_metrics_require_physical_creation_column(monkeypatch):
    api, queries, _ = load_sales_api(
        monkeypatch,
        helpdesk_creation_column=False,
    )
    result = api.get_sales_compass_data()["service"]

    assert result["available"] is False
    assert result["created_last_30_days"] is None
    assert not any(query["doctype"] == "HD Ticket" for query in queries)
