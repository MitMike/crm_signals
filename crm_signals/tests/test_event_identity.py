"""Bench integration tests for source event identity."""

import unittest

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
