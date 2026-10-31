"""Tests for rendering the configurable CRM Signals daily digest."""

import importlib
import sys
import types


def load_tasks(monkeypatch):
    fake = types.ModuleType("frappe")
    fake.session = types.SimpleNamespace(user="Administrator")
    fake.set_user = lambda user: setattr(fake.session, "user", user)
    fake.db = types.SimpleNamespace(
        get_single_value=lambda *args: "UTC",
        exists=lambda *args: True,
    )
    fake.get_all = lambda *args, **kwargs: []
    fake.get_meta = lambda doctype: types.SimpleNamespace(has_field=lambda field: True)
    fake.log_error = lambda **kwargs: None
    fake.get_traceback = lambda: "simulated test traceback"
    fake.PermissionError = type("PermissionError", (Exception,), {})
    fake.throw = lambda message: (_ for _ in ()).throw(ValueError(message))
    monkeypatch.setitem(sys.modules, "frappe", fake)

    settings = types.ModuleType("crm_signals.settings")
    settings.get_signal_settings = lambda: {}
    settings.parse_recipients = lambda value: list(value)
    monkeypatch.setitem(sys.modules, "crm_signals.settings", settings)
    sys.modules.pop("crm_signals.tasks", None)
    return importlib.import_module("crm_signals.tasks")


def test_digest_uses_transaction_currency_and_escapes_user_values(monkeypatch):
    tasks = load_tasks(monkeypatch)
    quotation = types.SimpleNamespace(
        party_name="<script>alert(1)</script>",
        grand_total=1234.5,
        currency="USD",
        name="QTN-001",
    )
    content = tasks._render_digest(4, 3, [quotation])
    assert "USD 1,234.50" in content
    assert "&lt;script&gt;" in content
    assert "not modified in more than 3 days" in content
    assert "₹" not in content


def test_quote_amount_does_not_assume_a_currency_symbol(monkeypatch):
    tasks = load_tasks(monkeypatch)
    quotation = types.SimpleNamespace(grand_total=1250, currency=None)
    assert tasks._format_quote_amount(quotation) == "1,250.00"


def test_recipient_digest_queries_as_the_recipient_and_restores_scheduler_user(monkeypatch):
    tasks = load_tasks(monkeypatch)
    fake = sys.modules["frappe"]
    seen_users = []

    api = types.ModuleType("crm_signals.api")
    api._dashboard_aggregate_field = lambda operation, fieldname, alias: (
        f"{operation.lower()}({fieldname}) as {alias}"
    )
    monkeypatch.setitem(sys.modules, "crm_signals.api", api)

    def permission_aware_get_list(doctype, **kwargs):
        seen_users.append(fake.session.user)
        assert fake.session.user == "manager@example.com"
        if doctype == "Lead":
            return [{"total": 2}]
        return [
            types.SimpleNamespace(
                name="QTN-001",
                party_name="Visible customer",
                grand_total=1250,
                currency="USD",
            )
        ]

    fake.get_list = permission_aware_get_list

    content = tasks._build_recipient_digest(
        "manager@example.com",
        "2026-11-01",
        "2026-10-29",
        3,
    )

    assert seen_users == ["manager@example.com", "manager@example.com"]
    assert fake.session.user == "Administrator"
    assert "Visible customer" in content
    assert "2</td>" in content
    assert "USD 1,250.00" in content


def test_digest_marks_denied_source_unavailable_instead_of_zero(monkeypatch):
    tasks = load_tasks(monkeypatch)
    fake = sys.modules["frappe"]
    fake.PermissionError = type("PermissionError", (Exception,), {})

    api = types.ModuleType("crm_signals.api")
    api._dashboard_aggregate_field = lambda operation, fieldname, alias: (
        f"{operation.lower()}({fieldname}) as {alias}"
    )
    monkeypatch.setitem(sys.modules, "crm_signals.api", api)

    def permission_aware_get_list(doctype, **kwargs):
        if doctype == "Lead":
            raise fake.PermissionError("Lead read denied")
        return []

    fake.get_list = permission_aware_get_list

    content = tasks._build_recipient_digest(
        "manager@example.com",
        "2026-11-01",
        "2026-10-29",
        3,
    )

    assert "Leads not modified in more than 3 days</b></td><td>Unavailable" in content
    assert "Quotations expiring today</b></td><td>0" in content
    assert fake.session.user == "Administrator"


def test_digest_queue_tracker_only_skips_recipients_for_the_same_date(monkeypatch):
    tasks = load_tasks(monkeypatch)

    class Settings:
        def __init__(self, date, recipients):
            self.last_digest_queued_date = date
            self.last_digest_queued_recipients = recipients

        def get(self, field):
            return getattr(self, field)

    today = __import__("datetime").date(2026, 11, 1)
    settings = Settings("2026-11-01", '["manager@example.com"]')
    assert tasks._queued_recipients_for_date(settings, today) == {"manager@example.com"}
    assert tasks._queued_recipients_for_date(Settings("2026-10-31", '["manager@example.com"]'), today) == set()
