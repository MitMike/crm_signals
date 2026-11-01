"""Bench-backed tests for authenticated webhook ingestion and source-event identity."""

import unittest
from unittest.mock import patch

try:
    import frappe
    from frappe.tests.utils import FrappeTestCase
except ModuleNotFoundError as error:
    if error.name != "frappe":
        raise
    frappe = None

    class FrappeTestCase(unittest.TestCase):
        pass

from crm_signals.event_identity import build_source_event_key

if frappe is not None:
    from crm_signals.api import ingest_signal


def _make_integration_user(suffix):
    return frappe.get_doc(
        {
            "doctype": "User",
            "email": f"crm-signal-api-{suffix}@example.com",
            "first_name": "CRM Signal API Test",
            "user_type": "System User",
            "enabled": 1,
            "send_welcome_email": 0,
            "roles": [{"role": "Sales User"}],
        }
    ).insert(ignore_permissions=True)


@unittest.skipIf(frappe is None, "Requires the Frappe Bench integration environment")
class TestCRMSignalWebhookIntegration(FrappeTestCase):
    def test_same_user_event_is_deduplicated_and_other_users_are_namespaced(self):
        suffix = frappe.generate_hash(length=8)
        first_user = _make_integration_user(f"{suffix}-one")
        second_user = _make_integration_user(f"{suffix}-two")
        lead = frappe.get_doc(
            {
                "doctype": "Lead",
                "company_name": f"CRM Signal API Test {suffix}",
                "email_id": f"crm-signal-api-lead-{suffix}@example.com",
                "status": "Lead",
            }
        ).insert(ignore_permissions=True)
        frappe.db.set_value("Lead", lead.name, "owner", first_user.name)

        settings = frappe.get_single("CRM Signals Settings")
        previous_settings = {
            "enabled": settings.enabled,
            "enable_external_ingestion": settings.enable_external_ingestion,
            "enable_quotation_signals": settings.enable_quotation_signals,
            "enable_opportunity_signals": settings.enable_opportunity_signals,
            "enable_daily_digest": settings.enable_daily_digest,
        }
        settings.enabled = 1
        settings.enable_external_ingestion = 1
        settings.enable_quotation_signals = 0
        settings.enable_opportunity_signals = 0
        settings.enable_daily_digest = 0
        settings.save(ignore_permissions=True)

        previous_user = frappe.session.user
        previous_form_dict = frappe.local.form_dict
        try:
            frappe.set_user(first_user.name)
            frappe.local.form_dict = {
                "signal_type": "Website Visit",
                "priority": "Medium",
                "message": "Visited the pricing page",
                "lead": lead.name,
                "source_event_id": "event-42",
            }
            with patch("frappe.publish_realtime") as publish:
                first = ingest_signal()
                duplicate = ingest_signal()
                self.assertEqual(publish.call_count, 1)

            frappe.set_user(second_user.name)
            frappe.local.form_dict = {
                "signal_type": "Website Visit",
                "priority": "Medium",
                "message": "Visited the pricing page",
                "lead": lead.name,
                "source_event_id": "event-42",
            }
            with patch("frappe.publish_realtime"):
                other_source = ingest_signal()
        finally:
            frappe.local.form_dict = previous_form_dict
            frappe.set_user(previous_user)
            for fieldname, value in previous_settings.items():
                frappe.db.set_value("CRM Signals Settings", None, fieldname, value)

        first_key = build_source_event_key("API Integration", first_user.name, "event-42")
        second_key = build_source_event_key("API Integration", second_user.name, "event-42")
        self.assertFalse(first["deduplicated"])
        self.assertTrue(duplicate["deduplicated"])
        self.assertEqual(first["signal"], duplicate["signal"])
        self.assertFalse(other_source["deduplicated"])
        self.assertNotEqual(first["signal"], other_source["signal"])
        self.assertNotEqual(first_key, second_key)
        self.assertEqual(
            frappe.get_all(
                "CRM Signal",
                filters={"source_event_key": first_key},
                pluck="name",
            ),
            [first["signal"]],
        )
        self.assertEqual(
            frappe.get_all(
                "CRM Signal",
                filters={"source_event_key": second_key},
                pluck="name",
            ),
            [other_source["signal"]],
        )
