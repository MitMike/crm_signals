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


def load_module(
    monkeypatch, owner_map, assignments, enabled_users, readable_users=None, signal_readable_users=None
):
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
    readable = set(enabled_users if readable_users is None else readable_users)
    signal_readable = set(
        enabled_users if signal_readable_users is None else signal_readable_users
    )
    fake.has_permission = lambda doctype, ptype="read", doc=None, user=None: (
        ptype == "read"
        and user in (signal_readable if doctype == "CRM Signal" else readable)
    )
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



def test_notification_failure_for_one_recipient_does_not_block_the_other(monkeypatch):
    module, published = load_module(
        monkeypatch,
        {("Lead", "LEAD-1"): "failed@example.com"},
        ["good@example.com"],
        ["failed@example.com", "good@example.com"],
    )
    fake_frappe = sys.modules["frappe"]

    def publish(**kwargs):
        if kwargs["user"] == "failed@example.com":
            raise RuntimeError("simulated realtime outage")
        published.append(kwargs)

    fake_frappe.publish_realtime = publish
    result = module.notify_signal(FakeSignal(lead="LEAD-1"))
    assert result == {"sent": 1, "failed": 1}
    assert [event["user"] for event in published] == ["good@example.com"]


def test_recipients_without_parent_read_permission_do_not_receive_alerts(monkeypatch):
    module, published = load_module(
        monkeypatch,
        {("Lead", "LEAD-1"): "owner@example.com"},
        ["assignee@example.com"],
        ["owner@example.com", "assignee@example.com"],
        readable_users=["assignee@example.com"],
    )

    recipients = module.get_signal_recipients(FakeSignal(lead="LEAD-1"))

    assert recipients == ["assignee@example.com"]
    assert published == []


def test_no_realtime_alert_is_sent_when_no_candidate_can_read_parent(monkeypatch):
    module, published = load_module(
        monkeypatch,
        {("Customer", "CUST-1"): "owner@example.com"},
        ["assignee@example.com"],
        ["owner@example.com", "assignee@example.com"],
        readable_users=[],
    )

    module.notify_signal(FakeSignal(customer="CUST-1"))

    assert published == []

def test_parent_reader_without_signal_read_permission_does_not_receive_alert(monkeypatch):
    module, published = load_module(
        monkeypatch,
        {("Lead", "LEAD-1"): "owner@example.com"},
        ["assignee@example.com"],
        ["owner@example.com", "assignee@example.com"],
        readable_users=["assignee@example.com"],
        signal_readable_users=[],
    )

    module.notify_signal(FakeSignal(lead="LEAD-1"))

    assert published == []

