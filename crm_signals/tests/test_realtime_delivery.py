"""Bench-backed tests for durable per-recipient realtime notification delivery."""

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


def _signal_publish_calls(publish, signal_name):
    """Return only CRM Signal publishes for the signal under test."""
    calls = []
    for call in publish.call_args_list:
        message = call.kwargs.get("message") or {}
        if (
            call.kwargs.get("event") == "crm_signal_received"
            and message.get("name") == signal_name
        ):
            calls.append(call)
    return calls


@unittest.skipIf(frappe is None, "Requires the Frappe Bench integration environment")
class TestRealtimeNotificationDelivery(FrappeTestCase):
    def _make_signal(self):
        suffix = frappe.generate_hash(length=8)
        return frappe.get_doc(
            {
                "doctype": "CRM Signal",
                "signal_type": "Website Visit",
                "priority": "High",
                "message": f"Realtime delivery test {suffix}",
            }
        ).insert(ignore_permissions=True)

    def test_stable_delivery_id_is_retried_without_duplicate_ledger_rows(self):
        from crm_signals.notifications import notify_signal
        from crm_signals.realtime_delivery import (
            process_signal_notification_delivery,
        )

        signal = self._make_signal()
        with (
            patch(
                "crm_signals.notifications.get_signal_recipients",
                return_value=["Administrator"],
            ),
            patch("frappe.publish_realtime") as publish,
        ):
            result = notify_signal(signal)
            delivery_name = frappe.db.get_value(
                "CRM Signal Notification Delivery",
                {"signal": signal.name, "recipient": "Administrator"},
                "name",
            )
            delivery = frappe.get_doc(
                "CRM Signal Notification Delivery", delivery_name
            )
            self.assertEqual(result["attempted"], 1)
            self.assertEqual(delivery.status, "Attempted")
            self.assertEqual(delivery.attempt_count, 1)
            delivery_calls = _signal_publish_calls(publish, signal.name)
            self.assertEqual(len(delivery_calls), 1)
            self.assertEqual(
                delivery_calls[0].kwargs["message"]["delivery_id"],
                delivery.delivery_key,
            )
            self.assertTrue(delivery_calls[0].kwargs["after_commit"])

            notify_signal(signal)
            self.assertEqual(len(_signal_publish_calls(publish, signal.name)), 1)
            delivery.db_set("next_retry_at", None, update_modified=False)
            retry = process_signal_notification_delivery(delivery.name)

        delivery.reload()
        self.assertEqual(retry["status"], "attempted")
        self.assertEqual(delivery.attempt_count, 2)
        delivery_calls = _signal_publish_calls(publish, signal.name)
        self.assertEqual(len(delivery_calls), 2)
        self.assertEqual(
            delivery_calls[-1].kwargs["message"]["delivery_id"],
            delivery.delivery_key,
        )
        self.assertEqual(
            frappe.db.count(
                "CRM Signal Notification Delivery",
                {"signal": signal.name, "recipient": "Administrator"},
            ),
            1,
        )

    def test_permission_revocation_cancels_due_delivery(self):
        from crm_signals.notifications import notify_signal
        from crm_signals.realtime_delivery import (
            process_signal_notification_delivery,
        )

        signal = self._make_signal()
        with (
            patch(
                "crm_signals.notifications.get_signal_recipients",
                return_value=["Administrator"],
            ),
            patch("frappe.publish_realtime") as publish,
        ):
            notify_signal(signal)
            delivery_name = frappe.db.get_value(
                "CRM Signal Notification Delivery",
                {"signal": signal.name, "recipient": "Administrator"},
                "name",
            )
            delivery = frappe.get_doc(
                "CRM Signal Notification Delivery", delivery_name
            )
            delivery.db_set("next_retry_at", None, update_modified=False)

            with patch(
                "crm_signals.notifications.get_signal_recipients",
                return_value=[],
            ):
                result = process_signal_notification_delivery(delivery.name)

        delivery.reload()
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(delivery.status, "Cancelled")
        self.assertEqual(delivery.last_error, "RecipientNoLongerEligible")
        self.assertEqual(len(_signal_publish_calls(publish, signal.name)), 1)

    def test_publish_failures_back_off_and_exhaust_to_failed(self):
        from crm_signals.realtime_delivery import (
            _get_or_create_delivery,
            process_signal_notification_delivery,
        )

        signal = self._make_signal()
        delivery = _get_or_create_delivery(signal.name, "Administrator")
        with (
            patch(
                "crm_signals.realtime_delivery.MAX_SIGNAL_NOTIFICATION_ATTEMPTS",
                2,
            ),
            patch(
                "crm_signals.notifications.get_signal_recipients",
                return_value=["Administrator"],
            ),
            patch(
                "frappe.publish_realtime",
                side_effect=RuntimeError("redis unavailable"),
            ),
            patch("frappe.log_error"),
        ):
            first = process_signal_notification_delivery(delivery.name)
            delivery.reload()
            self.assertEqual(first["status"], "pending")
            self.assertEqual(delivery.attempt_count, 1)
            self.assertIsNotNone(delivery.next_retry_at)

            delivery.db_set("next_retry_at", None, update_modified=False)
            second = process_signal_notification_delivery(delivery.name)

        delivery.reload()
        self.assertEqual(second["status"], "failed")
        self.assertEqual(delivery.status, "Failed")
        self.assertEqual(delivery.attempt_count, 2)
        self.assertEqual(delivery.last_error, "RuntimeError")

    def test_delivery_ledger_does_not_copy_notification_content(self):
        from crm_signals.realtime_delivery import _get_or_create_delivery

        signal = self._make_signal()
        delivery = _get_or_create_delivery(signal.name, "Administrator")
        meta = frappe.get_meta("CRM Signal Notification Delivery")
        self.assertFalse(meta.has_field("message"))
        self.assertEqual(delivery.signal, signal.name)
        self.assertEqual(delivery.recipient, "Administrator")
