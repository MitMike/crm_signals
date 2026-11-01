"""Bench integration tests for source event identity."""

import unittest
from unittest.mock import MagicMock, patch

try:
    import frappe
    from frappe.exceptions import UniqueValidationError
    from frappe.tests.utils import FrappeTestCase
except ModuleNotFoundError as error:
    if error.name != "frappe":
        raise
    frappe = None
    UniqueValidationError = Exception

    class FrappeTestCase(unittest.TestCase):
        pass


@unittest.skipIf(frappe is None, "Requires Frappe Bench")
class TestCRMSourceEventUniqueKey(FrappeTestCase):
    def test_duplicate_source_event_is_rejected_and_legacy_rows_remain_valid(self):
        suffix = frappe.generate_hash(length=8)
        values = {
            "doctype": "CRM Signal",
            "signal_type": "Website Visit",
            "priority": "Medium",
            "message": "Legacy signal without source identity",
        }
        first_legacy = frappe.get_doc(dict(values)).insert(ignore_permissions=True)
        second_legacy = frappe.get_doc(dict(values)).insert(ignore_permissions=True)
        self.assertIsNone(first_legacy.source_event_key)
        self.assertIsNone(second_legacy.source_event_key)

        values.update(
            {
                "message": "Idempotent source event",
                "source_doctype": "API Integration",
                "source_name": f"integration-{suffix}",
                "source_event_id": "event-1",
            }
        )
        frappe.get_doc(dict(values)).insert(ignore_permissions=True)
        with self.assertRaises(UniqueValidationError):
            frappe.get_doc(dict(values)).insert(ignore_permissions=True)

    def test_insert_signal_once_recovers_from_a_unique_key_race(self):
        from crm_signals.events import insert_signal_once

        source = {
            "signal_type": "Website Visit",
            "message": "Concurrent duplicate event",
            "priority": "Medium",
            "source_doctype": "API Integration",
            "source_name": f"integration-{frappe.generate_hash(length=8)}",
            "source_event_id": "race-event-1",
        }

        with patch("crm_signals.notifications.notify_signal") as notify:
            existing, created = insert_signal_once(**source)
            self.assertTrue(created)
            self.assertEqual(notify.call_count, 1)

            duplicate_doc = MagicMock()
            unique_error = type("UniqueValidationError", (Exception,), {})(
                "simulated unique-key race"
            )
            duplicate_doc.insert.side_effect = unique_error

            # Simulate the read-before-insert race: the initial SELECT misses
            # the row, INSERT loses to another transaction, and the locking
            # read must return the already committed winner.
            with patch.object(frappe.db, "get_value", return_value=None):
                with patch("frappe.get_doc", side_effect=[duplicate_doc, existing]):
                    recovered, recovered_created = insert_signal_once(**source)

            self.assertFalse(recovered_created)
            self.assertEqual(recovered.name, existing.name)
            self.assertEqual(notify.call_count, 1)
