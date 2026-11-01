"""Bench-backed permission tests for CRM Signal notification routing."""

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from crm_signals.notifications import notify_signal


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

        with patch("frappe.publish_realtime") as publish:
            notify_signal(signal)

        self.assertEqual(
            [call.kwargs["user"] for call in publish.call_args_list],
            [assignee.name],
        )
