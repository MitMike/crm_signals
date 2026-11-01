"""Bench-backed retry tests for the transactional CRM Signal event outbox."""

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

if frappe is not None:
    from crm_signals.event_identity import build_source_event_key
    from crm_signals.signal_outbox import (
        _retry_delay_minutes,
        enqueue_signal_event,
        process_signal_outbox_event,
    )


@unittest.skipIf(frappe is None, "Requires the Frappe Bench integration environment")
class TestSignalOutbox(FrappeTestCase):
    def test_failed_immediate_delivery_is_retried_without_losing_source_event(self):
        suffix = frappe.generate_hash(length=8)
        source_name = f"OUTBOX-TEST-{suffix}"
        source_event_id = f"submit:{suffix}"
        payload = {
            "signal_type": "High-Value Quote",
            "message": f"Outbox retry integration test {suffix}",
            "priority": "High",
            "source_doctype": "Quotation",
            "source_name": source_name,
            "source_event_id": source_event_id,
        }

        with (
            patch(
                "crm_signals.events.insert_signal_once",
                side_effect=RuntimeError("temporary database failure"),
            ),
            patch("frappe.log_error"),
        ):
            outbox_name = enqueue_signal_event(**payload)

        outbox = frappe.get_doc("CRM Signal Outbox", outbox_name)
        self.assertEqual(outbox.status, "Pending")
        self.assertEqual(outbox.attempt_count, 1)
        self.assertEqual(outbox.last_error, "RuntimeError")
        self.assertIsNotNone(outbox.next_retry_at)

        # Make the retry due without sleeping; the scheduler uses the same worker.
        outbox.db_set("next_retry_at", None, update_modified=False)
        with patch("crm_signals.notifications.notify_signal"):
            result = process_signal_outbox_event(outbox_name)

        outbox.reload()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(outbox.status, "Completed")
        self.assertEqual(outbox.attempt_count, 1)
        self.assertIsNotNone(outbox.completed_at)
        self.assertTrue(outbox.signal)

        event_key = build_source_event_key("Quotation", source_name, source_event_id)
        signals = frappe.get_all(
            "CRM Signal",
            filters={"source_event_key": event_key},
            pluck="name",
        )
        self.assertEqual(signals, [outbox.signal])

        # Replaying the same source event reuses the completed outbox row.
        with patch("crm_signals.notifications.notify_signal"):
            replayed_name = enqueue_signal_event(**payload)
        self.assertEqual(replayed_name, outbox_name)
        self.assertEqual(
            frappe.get_all(
                "CRM Signal",
                filters={"source_event_key": event_key},
                pluck="name",
            ),
            [outbox.signal],
        )

    def test_outbox_retry_backoff_is_bounded(self):
        self.assertEqual(_retry_delay_minutes(1), 1)
        self.assertEqual(_retry_delay_minutes(2), 2)
        self.assertEqual(_retry_delay_minutes(3), 4)
        self.assertEqual(_retry_delay_minutes(7), 60)
        self.assertEqual(_retry_delay_minutes(10), 60)
