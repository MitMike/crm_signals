"""Tests for rendering the configurable CRM Signals daily digest."""

import importlib
import sys
import types


def load_tasks(monkeypatch):
    fake = types.ModuleType("frappe")
    fake.db = types.SimpleNamespace(get_single_value=lambda *args: "UTC")
    fake.get_all = lambda *args, **kwargs: []
    fake.get_meta = lambda doctype: types.SimpleNamespace(has_field=lambda field: True)
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
