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


def test_extra_digest_recipient_must_be_an_enabled_system_user(monkeypatch):
    settings = load_settings(monkeypatch)
    frappe = sys.modules["frappe"]
    frappe.db.get_value = lambda doctype, *args, **kwargs: (
        "USD"
        if doctype == "Company"
        else {"enabled": 1, "user_type": "System User"}
    )
    doc = types.SimpleNamespace(
        quotation_threshold=200000,
        threshold_currency=None,
        enable_quotation_signals=1,
        enable_opportunity_signals=1,
        opportunity_trigger_statuses="Replied",
        lead_stale_days=3,
        digest_time="08:30:00",
        digest_extra_recipients="sales@example.com",
    )

    settings.validate_settings_document(doc)

    assert doc.threshold_currency == "USD"


def test_unregistered_digest_recipient_is_rejected(monkeypatch):
    settings = load_settings(monkeypatch)
    frappe = sys.modules["frappe"]
    frappe.db.get_value = lambda doctype, *args, **kwargs: (
        "USD" if doctype == "Company" else None
    )
    doc = types.SimpleNamespace(
        quotation_threshold=200000,
        threshold_currency=None,
        enable_quotation_signals=1,
        enable_opportunity_signals=1,
        opportunity_trigger_statuses="Replied",
        lead_stale_days=3,
        digest_time="08:30:00",
        digest_extra_recipients="unknown@example.com",
    )

    try:
        settings.validate_settings_document(doc)
    except frappe.ValidationError as error:
        assert "not a registered User" in str(error)
    else:
        raise AssertionError("Unregistered digest recipients must be rejected")
