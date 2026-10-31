"""Unit tests for CRM Signals configuration parsing and presets."""

import importlib
import sys
import types


def load_settings(monkeypatch):
    fake = types.ModuleType("frappe")
    fake._ = lambda message: message
    fake.ValidationError = type("ValidationError", (Exception,), {})
    fake.throw = lambda message, exc=None: (_ for _ in ()).throw((exc or Exception)(message))
    fake.db = types.SimpleNamespace(
        get_single_value=lambda *args: "Default Company",
        get_value=lambda *args: "USD",
    )
    monkeypatch.setitem(sys.modules, "frappe", fake)
    monkeypatch.delitem(sys.modules, "crm_signals.settings", raising=False)
    return importlib.import_module("crm_signals.settings")


def test_status_parser_trims_and_deduplicates_case_insensitively(monkeypatch):
    settings = load_settings(monkeypatch)
    assert settings.parse_statuses("Replied\n Open \nreplied, Quotation") == [
        "Replied", "Open", "Quotation"
    ]


def test_recipient_parser_trims_and_deduplicates(monkeypatch):
    settings = load_settings(monkeypatch)
    assert settings.parse_recipients(
        "sales@example.com\n SALES@example.com,ops@example.com"
    ) == ["sales@example.com", "ops@example.com"]


def test_presets_have_explicit_digest_and_event_defaults(monkeypatch):
    settings = load_settings(monkeypatch)
    assert set(settings.PRESETS) == {"Balanced", "Sales Focused", "Executive"}
    assert settings.PRESETS["Balanced"]["lead_stale_days"] == 3
    assert settings.PRESETS["Sales Focused"]["lead_stale_days"] == 2
    assert settings.PRESETS["Executive"]["quotation_threshold"] == 500000
    assert all(
        config["opportunity_trigger_statuses"] == "Replied"
        for config in settings.PRESETS.values()
    )


def test_company_currency_comes_from_company_metadata(monkeypatch):
    settings = load_settings(monkeypatch)
    assert settings.get_company_default_currency("Example Ltd") == "USD"
