"""Tests for server-owned CRM Signal source-event identities."""

import importlib
import sys
import types

from crm_signals.event_identity import build_source_event_key


def load_controller(monkeypatch):
    fake_frappe = types.ModuleType("frappe")
    fake_frappe.__path__ = []

    class ValidationError(Exception):
        pass

    fake_frappe.ValidationError = ValidationError
    fake_frappe.throw = lambda message: (_ for _ in ()).throw(ValidationError(message))

    fake_model = types.ModuleType("frappe.model")
    fake_model.__path__ = []
    fake_document = types.ModuleType("frappe.model.document")

    class Document:
        pass

    fake_document.Document = Document
    fake_model.document = fake_document
    fake_frappe.model = fake_model

    monkeypatch.setitem(sys.modules, "frappe", fake_frappe)
    monkeypatch.setitem(sys.modules, "frappe.model", fake_model)
    monkeypatch.setitem(sys.modules, "frappe.model.document", fake_document)
    module_name = "crm_signals.crm_signals.doctype.crm_signal.crm_signal"
    monkeypatch.delitem(sys.modules, module_name, raising=False)
    return importlib.import_module(module_name), ValidationError


def make_signal(controller, **overrides):
    values = {
        "signal_type": "Website Visit",
        "priority": "Medium",
        "lead": None,
        "customer": None,
        "message": "Visited pricing page",
        "source_doctype": "API Integration",
        "source_name": "integration@example.com",
        "source_event_id": "event-42",
        "source_event_key": "caller-supplied-forged-key",
    }
    values.update(overrides)
    signal = controller.CRMSignal()
    for field, value in values.items():
        setattr(signal, field, value)
    return signal


def test_source_event_key_is_always_derived_by_the_server(monkeypatch):
    controller, _ = load_controller(monkeypatch)
    signal = make_signal(controller)

    signal.validate()

    assert signal.source_event_key == build_source_event_key(
        "API Integration",
        "integration@example.com",
        "event-42",
    )
    assert signal.source_event_key != "caller-supplied-forged-key"


def test_source_identity_fields_are_trimmed_before_hashing(monkeypatch):
    controller, _ = load_controller(monkeypatch)
    signal = make_signal(
        controller,
        source_doctype=" API Integration ",
        source_name=" integration@example.com ",
        source_event_id=" event-42 ",
        source_event_key=None,
    )

    signal.validate()

    assert signal.source_doctype == "API Integration"
    assert signal.source_name == "integration@example.com"
    assert signal.source_event_id == "event-42"
    assert signal.source_event_key == build_source_event_key(
        "API Integration",
        "integration@example.com",
        "event-42",
    )


def test_partial_source_identity_is_rejected(monkeypatch):
    controller, validation_error = load_controller(monkeypatch)
    signal = make_signal(controller, source_event_id=None)

    try:
        signal.validate()
    except validation_error as error:
        assert "must be supplied together" in str(error)
    else:
        raise AssertionError("Partial source identity must be rejected")


def test_source_key_without_source_identity_is_cleared(monkeypatch):
    controller, _ = load_controller(monkeypatch)
    signal = make_signal(
        controller,
        source_doctype=None,
        source_name=None,
        source_event_id=None,
        source_event_key="caller-supplied-forged-key",
    )

    signal.validate()

    assert signal.source_event_key is None
