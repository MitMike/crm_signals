"""Bench-backed permission tests for CRM Signal notification routing."""

import unittest
from unittest.mock import patch

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase
except ModuleNotFoundError as error:
    if error.name == "frappe":
        raise unittest.SkipTest("Requires the Frappe Bench integration environment")
    raise

from crm_signals.notifications import notify_signal

def _make_system_user(suffix, role=None):
    user_data = {
        "doctype": "User",
        "email": f"crm-signal-list-{suffix}@example.com",
        "first_name": "CRM Signal List Test",
        "user_type": "System User",
        "enabled": 1,
        "send_welcome_email": 0,
    }
    if role:
        user_data["roles"] = [{"role": role}]
    return frappe.get_doc(user_data).insert(ignore_permissions=True)


def _make_lead(suffix):
    return frappe.get_doc(
        {
            "doctype": "Lead",
            "company_name": f"CRM Signal List Test {suffix}",
            "email_id": f"crm-signal-list-lead-{suffix}@example.com",
            "status": "Lead",
        }
    ).insert(ignore_permissions=True)


def _make_signal(lead=None):
    return frappe.get_doc(
        {
            "doctype": "CRM Signal",
            "signal_type": "Website Visit",
            "priority": "Medium",
            "message": "CRM Signal list permission test",
            "lead": lead,
        }
    ).insert(ignore_permissions=True)


class TestCRMSignalNotificationPermissions(FrappeTestCase):
    def test_recipient_must_be_able_to_read_linked_lead(self):
        suffix = frappe.generate_hash(length=8)
        owner_email = f"crm-signal-owner-{suffix}@example.com"
        assignee_email = f"crm-signal-assignee-{suffix}@example.com"

        owner = frappe.get_doc(
            {
                "doctype": "User",
                "email": owner_email,
                "first_name": "CRM Signal Owner",
                "user_type": "System User",
                "enabled": 1,
                "send_welcome_email": 0,
            }
        ).insert(ignore_permissions=True)
        assignee = frappe.get_doc(
            {
                "doctype": "User",
                "email": assignee_email,
                "first_name": "CRM Signal Assignee",
                "user_type": "System User",
                "enabled": 1,
                "send_welcome_email": 0,
                "roles": [{"role": "Sales User"}],
            }
        ).insert(ignore_permissions=True)
        frappe.clear_cache(user=assignee.name)

        lead = frappe.get_doc(
            {
                "doctype": "Lead",
                "company_name": f"CRM Signal Permission Test {suffix}",
                "email_id": f"crm-signal-lead-{suffix}@example.com",
                "status": "Lead",
            }
        ).insert(ignore_permissions=True)
        frappe.db.set_value("Lead", lead.name, "owner", owner.name)

        frappe.get_doc(
            {
                "doctype": "ToDo",
                "allocated_to": assignee.name,
                "reference_type": "Lead",
                "reference_name": lead.name,
                "description": "CRM Signals permission integration test",
                "status": "Open",
            }
        ).insert(ignore_permissions=True)

        signal = frappe.get_doc(
            {
                "doctype": "CRM Signal",
                "signal_type": "Website Visit",
                "priority": "Medium",
                "message": "Permission-scoped notification test",
                "lead": lead.name,
            }
        ).insert(ignore_permissions=True)

        self.assertFalse(
            frappe.has_permission("Lead", ptype="read", doc=lead.name, user=owner.name)
        )
        self.assertTrue(
            frappe.has_permission("Lead", ptype="read", doc=lead.name, user=assignee.name)
        )
        self.assertFalse(
            frappe.has_permission("CRM Signal", ptype="read", doc=signal.name, user=owner.name)
        )
        self.assertTrue(
            frappe.has_permission("CRM Signal", ptype="read", doc=signal.name, user=assignee.name)
        )

        with patch("frappe.publish_realtime") as publish:
            notify_signal(signal)

        self.assertEqual(
            [call.kwargs["user"] for call in publish.call_args_list],
            [assignee.name],
        )

    def test_linked_signal_owner_without_parent_read_cannot_list_signal(self):
        suffix = frappe.generate_hash(length=8)
        user = _make_system_user(suffix, role="Sales User")
        target_lead = _make_lead(f"target-{suffix}")
        allowed_lead = _make_lead(f"allowed-{suffix}")
        frappe.db.set_value("Lead", target_lead.name, "owner", user.name)

        linked_signal = _make_signal(target_lead.name)
        frappe.db.set_value("CRM Signal", linked_signal.name, "owner", user.name)
        unlinked_signal = _make_signal()
        frappe.db.set_value("CRM Signal", unlinked_signal.name, "owner", user.name)

        frappe.get_doc(
            {
                "doctype": "User Permission",
                "user": user.name,
                "allow": "Lead",
                "for_value": allowed_lead.name,
            }
        ).insert(ignore_permissions=True)
        frappe.clear_cache(user=user.name)

        self.assertFalse(
            frappe.has_permission(
                "Lead", ptype="read", doc=target_lead.name, user=user.name
            )
        )

        previous_user = frappe.session.user
        frappe.set_user(user.name)
        try:
            linked_visible = frappe.get_list(
                "CRM Signal", filters={"name": linked_signal.name}, pluck="name"
            )
            unlinked_visible = frappe.get_list(
                "CRM Signal", filters={"name": unlinked_signal.name}, pluck="name"
            )
        finally:
            frappe.set_user(previous_user)

        self.assertNotIn(linked_signal.name, linked_visible)
        self.assertIn(unlinked_signal.name, unlinked_visible)
