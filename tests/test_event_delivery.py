"""Tests for unique source identity at the CRM Signal creation boundary."""

import importlib
import sys
import types


def load_events(monkeypatch, *, existing_name=None, duplicate_on_insert=False):
    fake = types.ModuleType("frappe")
    lookups = []

    class DuplicateEntryError(Exception):
        pass

    fake.DuplicateEntryError = DuplicateEntryError
    fake.db = types.SimpleNamespace(
        get_value=lambda *args: (lookups.append(args) or existing_name)
    )
    inserted = []
    loaded = []

    class FakeSignal:
        def __init__(self, values):
            self.values = values
            self.name = "SIG-0001"

        def insert(self, ignore_permissions=False):
            inserted.append(ignore_permissions)
            if duplicate_on_insert:
                raise DuplicateEntryError("unique key already exists")

    def get_doc(values, name=None):
        if isinstance(values, dict):
            signal = FakeSignal(values)
            loaded.append(signal)
            return signal
        return types.SimpleNamespace(name=name, loaded=True)

    fake.get_doc = get_doc
    monkeypatch.setitem(sys.modules, "frappe", fake)

    notifications = types.ModuleType("crm_signals.notifications")
    notifications.sent = []
    notifications.notify_signal = lambda signal: notifications.sent.append(signal.name)
    monkeypatch.setitem(sys.modules, "crm_signals.notifications", notifications)

    settings = types.ModuleType("crm_signals.settings")
    settings.get_company_default_currency = lambda company=None: "USD"
    settings.get_signal_settings = lambda: {
        "enabled": True,
        "enable_quotation_signals": True,
        "enable_opportunity_signals": True,
        "opportunity_trigger_statuses": ["Replied"],
        "quotation_threshold": 200000,
        "threshold_currency": "USD",
    }
    monkeypatch.setitem(sys.modules, "crm_signals.settings", settings)
    monkeypatch.delitem(sys.modules, "crm_signals.events", raising=False)
    module = importlib.import_module("crm_signals.events")
    return module, notifications, inserted, lookups, loaded, fake


def test_new_source_event_is_inserted_once_and_notified(monkeypatch):
    module, notifications, inserted, lookups, loaded, _ = load_events(monkeypatch)

    signal, created = module.insert_signal_once(
        "Website Visit",
        "Visited pricing",
        "Medium",
        source_doctype="API Integration",
        source_name="integration@example.com",
        source_event_id="event-1",
        ignore_permissions=False,
    )

    assert created is True
    assert signal is loaded[0]
    assert inserted == [False]
    assert len(lookups) == 1
    assert notifications.sent == [signal.name]
    assert signal.values["source_event_key"]


def test_existing_source_event_is_returned_without_insert_or_notification(monkeypatch):
    module, notifications, inserted, lookups, loaded, _ = load_events(
        monkeypatch,
        existing_name="SIG-EXISTING",
    )

    signal, created = module.insert_signal_once(
        "Website Visit",
        "Repeated event",
        "Medium",
        source_doctype="API Integration",
        source_name="integration@example.com",
        source_event_id="event-1",
    )

    assert created is False
    assert signal.name == "SIG-EXISTING"
    assert loaded == []
    assert inserted == []
    assert notifications.sent == []
    assert len(lookups) == 1


def test_unique_index_race_returns_existing_signal_without_duplicate_notification(monkeypatch):
    module, notifications, inserted, lookups, loaded, fake = load_events(
        duplicate_on_insert=True,
    )
    lookup_count = 0

    def race_lookup(*args):
        nonlocal lookup_count
        lookup_count += 1
        return None if lookup_count == 1 else "SIG-CONCURRENT"

    fake.db.get_value = race_lookup

    signal, created = module.insert_signal_once(
        "Website Visit",
        "Concurrent retry",
        "Medium",
        source_doctype="API Integration",
        source_name="integration@example.com",
        source_event_id="event-1",
    )

    assert created is False
    assert signal.name == "SIG-CONCURRENT"
    assert inserted == [True]
    assert loaded[0].values["source_event_key"]
    assert notifications.sent == []
