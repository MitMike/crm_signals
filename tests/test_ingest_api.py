"""Contract tests for authenticated, idempotent webhook ingestion."""

import importlib
import sys
import types


def _raise(message, exception=None):
    raise (exception or Exception)(message)


def load_api(monkeypatch, *, user="integration@example.com", settings=None, source_data=None):
    fake = types.ModuleType("frappe")
    fake.__path__ = []
    fake._ = lambda message: message
    fake.whitelist = lambda **kwargs: (lambda function: function)
    fake.session = types.SimpleNamespace(user=user)
    fake.local = types.SimpleNamespace(
        form_dict={
            "signal_type": "Website Visit",
            "message": "Visited pricing page",
            **(source_data or {}),
        }
    )

    class AuthenticationError(Exception):
        pass

    class PermissionError(Exception):
        pass

    class ValidationError(Exception):
        pass

    class LinkValidationError(Exception):
        pass

    fake.AuthenticationError = AuthenticationError
    fake.PermissionError = PermissionError
    fake.ValidationError = ValidationError
    fake.LinkValidationError = LinkValidationError
    fake.throw = _raise
    fake.db = types.SimpleNamespace(
        exists=lambda doctype, name: doctype in {"Lead", "Customer"} and name in {"LEAD-1", "CUST-1"}
    )
    monkeypatch.setitem(sys.modules, "frappe", fake)

    event_calls = []
    event_module = types.ModuleType("crm_signals.events")

    def insert_signal_once(**kwargs):
        event_calls.append(kwargs)
        signal = types.SimpleNamespace(name="SIG-0001")
        return signal, True

    event_module.insert_signal_once = insert_signal_once
    monkeypatch.setitem(sys.modules, "crm_signals.events", event_module)

    settings_module = types.ModuleType("crm_signals.settings")
    settings_module.get_signal_settings = lambda: settings or {
        "enabled": True,
        "enable_external_ingestion": True,
    }
    monkeypatch.setitem(sys.modules, "crm_signals.settings", settings_module)

    monkeypatch.delitem(sys.modules, "crm_signals.api", raising=False)
    api = importlib.import_module("crm_signals.api")
    return api, event_calls, fake


def test_webhook_event_id_is_scoped_to_integration_user(monkeypatch):
    api, calls, _ = load_api(
        monkeypatch,
        source_data={"source_event_id": "event-42"},
    )

    result = api.ingest_signal()

    assert result == {
        "status": "success",
        "signal": "SIG-0001",
        "deduplicated": False,
    }
    assert calls[0]["source_doctype"] == "API Integration"
    assert calls[0]["source_name"] == "integration@example.com"
    assert calls[0]["source_event_id"] == "event-42"
    assert calls[0]["ignore_permissions"] is False


def test_webhook_rejects_partial_source_identity(monkeypatch):
    api, calls, fake = load_api(
        monkeypatch,
        source_data={
            "source_doctype": "External CRM",
            "source_event_id": "event-42",
        },
    )

    try:
        api.ingest_signal()
    except fake.ValidationError as error:
        assert "supplied together" in str(error)
    else:
        raise AssertionError("Partial source identity must be rejected")
    assert calls == []


def test_webhook_requires_event_id_when_source_metadata_is_supplied(monkeypatch):
    api, calls, fake = load_api(
        monkeypatch,
        source_data={
            "source_doctype": "External CRM",
            "source_name": "Account-1",
        },
    )

    try:
        api.ingest_signal()
    except fake.ValidationError as error:
        assert "source_event_id is required" in str(error)
    else:
        raise AssertionError("Source metadata without event ID must be rejected")
    assert calls == []


def test_disabled_external_ingestion_fails_closed(monkeypatch):
    api, calls, fake = load_api(
        monkeypatch,
        settings={"enabled": True, "enable_external_ingestion": False},
    )

    try:
        api.ingest_signal()
    except fake.PermissionError as error:
        assert "disabled" in str(error)
    else:
        raise AssertionError("Disabled external ingestion must be rejected")
    assert calls == []


def test_guest_cannot_ingest(monkeypatch):
    api, calls, fake = load_api(monkeypatch, user="Guest")

    try:
        api.ingest_signal()
    except fake.AuthenticationError as error:
        assert "Authentication" in str(error)
    else:
        raise AssertionError("Guest ingestion must be rejected")
    assert calls == []
