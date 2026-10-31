"""Unit tests for recipient selection using a tiny mocked Frappe surface."""

import importlib
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class FakeDB:
    def __init__(self, owners=None):
        self.owners = owners or {}

    def get_value(self, doctype, name, field):
        return self.owners.get((doctype, name))


class FakeSignal:
    def __init__(self, lead=None, customer=None, name="SIG-1"):
        self.lead = lead
        self.customer = customer
        self.name = name
        self.signal_type = "Website Visit"
        self.priority = "Medium"
        self.message = "Sample CRM signal message"


def load_module(monkeypatch, owner_map, assignments, enabled_users):
    fake = types.ModuleType("frappe")
    fake.db = FakeDB(owner_map)
    published = []

    def get_all(doctype, filters=None, pluck=None):
        if doctype == "ToDo":
            return assignments
        if doctype == "User":
            requested = set(filters["name"][1])
            return [user for user in enabled_users if user in requested]
        raise AssertionError(f"Unexpected DocType: {doctype}")

    fake.get_all = get_all
    fake.publish_realtime = lambda **kwargs: published.append(kwargs)
    monkeypatch.setitem(sys.modules, "frappe", fake)
    sys.modules.pop("crm_signals.notifications", None)
    module = importlib.import_module("crm_signals.notifications")
    return module, published


def test_recipients_are_related_owner_and_active_assignees_only(monkeypatch):
    module, _ = load_module(
        monkeypatch,
        {("Lead", "LEAD-1"): "owner@example.com"},
        ["assignee@example.com", "disabled@example.com", None],
        ["owner@example.com", "assignee@example.com"],
    )
    recipients = module.get_signal_recipients(FakeSignal(lead="LEAD-1"))
    assert recipients == ["assignee@example.com", "owner@example.com"]


def test_unlinked_signal_has_no_recipients_or_site_wide_notification(monkeypatch):
    module, published = load_module(monkeypatch, {}, [], ["manager@example.com"])
    signal = FakeSignal()
    assert module.get_signal_recipients(signal) == []
    module.notify_signal(signal)
    assert published == []


def test_notification_targets_each_resolved_user(monkeypatch):
    module, published = load_module(
        monkeypatch,
        {("Customer", "CUST-1"): "owner@example.com"},
        ["owner@example.com", "rep@example.com"],
        ["owner@example.com", "rep@example.com"],
    )
    module.notify_signal(FakeSignal(customer="CUST-1"))
    assert {event["user"] for event in published} == {
        "owner@example.com", "rep@example.com"
    }
    assert all(event["after_commit"] is True for event in published)
    assert all(event["message"]["message"] == "Sample CRM signal message" for event in published)

