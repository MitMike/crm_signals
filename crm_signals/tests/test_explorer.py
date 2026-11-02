"""Focused tests for the permission-aware Explorer core adapters."""

import base64
import json
import unittest
from contextlib import contextmanager
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
    from crm_signals import explorer


@contextmanager
def _as_administrator():
    previous_user = frappe.session.user
    frappe.set_user("Administrator")
    try:
        yield
    finally:
        frappe.set_user(previous_user)


class _Meta:
    def has_field(self, fieldname):
        return True


def _item(source_id, event_id, timestamp):
    return {
        "source_id": source_id,
        "source_event_id": event_id,
        "timestamp": timestamp,
    }


@unittest.skipIf(frappe is None, "Requires the Frappe Bench integration environment")
class TestExplorerTimeline(FrappeTestCase):
    def test_fractional_page_length_is_rejected(self):
        with self.assertRaises(frappe.ValidationError):
            explorer.get_explorer_timeline("Lead", "LEAD-0001", page_length=1.5)

    def test_cursor_round_trip_preserves_snapshot_and_offsets(self):
        offsets = {"crm_signal": 2, "quotation": 1, "opportunity": 0}
        cursor = explorer._encode_cursor("2026-11-02 10:00:00", offsets, 20, "Lead:LEAD-0001")

        decoded = explorer._decode_cursor(cursor, 20, "Lead:LEAD-0001")

        self.assertEqual(decoded["as_of"], "2026-11-02 10:00:00")
        self.assertEqual(decoded["offsets"], offsets)

    def test_cursor_cannot_be_reused_for_another_context(self):
        offsets = {"crm_signal": 0, "quotation": 0, "opportunity": 0}
        cursor = explorer._encode_cursor("2026-11-02 10:00:00", offsets, 20, "Lead:LEAD-0001")

        with self.assertRaises(frappe.ValidationError):
            explorer._decode_cursor(cursor, 20, "Customer CUST-0001")

    def test_cursor_rejects_non_object_payload(self):
        cursor = base64.urlsafe_b64encode(b"[]").decode("ascii").rstrip("=")

        with self.assertRaises(frappe.ValidationError):
            explorer._decode_cursor(cursor, 20, "Lead:LEAD-0001")

    def test_merge_uses_stable_tie_break_and_per_source_offsets(self):
        pages = {
            "crm_signal": {
                "status": "available",
                "rows": [
                    {"item": _item("crm_signal", "SIG-2", "2026-11-02 10:00:00"), "position": 0},
                    {"item": _item("crm_signal", "SIG-1", "2026-11-02 09:00:00"), "position": 1},
                ],
                "raw_count": 2,
                "leading_skipped": 0,
            },
            "quotation": {
                "status": "available",
                "rows": [
                    {"item": _item("quotation", "QTN-1", "2026-11-02 10:00:00"), "position": 0}
                ],
                "raw_count": 1,
                "leading_skipped": 0,
            },
            "opportunity": {
                "status": "empty",
                "rows": [],
                "raw_count": 0,
                "leading_skipped": 0,
            },
        }

        items, offsets, has_more = explorer._merge_source_pages(
            pages,
            {"crm_signal": 0, "quotation": 0, "opportunity": 0},
            2,
        )

        self.assertEqual(
            [(item["source_id"], item["source_event_id"]) for item in items],
            [("quotation", "QTN-1"), ("crm_signal", "SIG-2")],
        )
        self.assertEqual(offsets, {"crm_signal": 1, "quotation": 1, "opportunity": 0})
        self.assertTrue(has_more)

    def test_merge_advances_past_rows_hidden_by_a_permission_recheck(self):
        pages = {
            "crm_signal": {
                "status": "available",
                "rows": [
                    {"item": _item("crm_signal", "SIG-3", "2026-11-02 09:00:00"), "position": 2}
                ],
                "raw_count": 3,
                "leading_skipped": 2,
            },
            "quotation": {"status": "empty", "rows": [], "raw_count": 0, "leading_skipped": 0},
            "opportunity": {"status": "empty", "rows": [], "raw_count": 0, "leading_skipped": 0},
        }

        items, offsets, has_more = explorer._merge_source_pages(
            pages,
            {"crm_signal": 0, "quotation": 0, "opportunity": 0},
            1,
        )

        self.assertEqual([item["source_event_id"] for item in items], ["SIG-3"])
        self.assertEqual(offsets["crm_signal"], 3)
        self.assertFalse(has_more)

    def test_timeline_returns_safe_summaries_and_marks_unreadable_sources_unavailable(self):
        def get_list(doctype, **kwargs):
            if doctype == "Lead":
                return [{"name": "LEAD-0001"}]
            if doctype == "CRM Signal":
                return [
                    {
                        "name": "SIG-0001",
                        "creation": "2026-11-02 10:00:00",
                        "signal_type": "Website Visit",
                        "priority": "High",
                        "message": "private message body must not be copied",
                        "lead": "LEAD-0001",
                        "customer": None,
                    }
                ]
            if doctype == "Quotation":
                return [
                    {
                        "name": "QTN-0001",
                        "creation": "2026-11-02 09:00:00",
                        "quotation_to": "Lead",
                        "party_name": "LEAD-0001",
                        "status": "Open",
                    }
                ]
            if doctype == "Opportunity":
                return []
            return []

        def has_permission(doctype, ptype="read", doc=None, user=None):
            return doctype != "Quotation"

        with (
            _as_administrator(),
            patch.object(frappe.db, "exists", return_value=True),
            patch.object(frappe, "has_permission", side_effect=has_permission),
            patch.object(frappe, "get_meta", return_value=_Meta()),
            patch.object(frappe, "get_list", side_effect=get_list),
            patch.object(explorer, "now_datetime", return_value="2026-11-02 11:00:00"),
        ):
            result = explorer.get_explorer_timeline("Lead", "LEAD-0001", page_length=10)

        self.assertEqual(result["context"]["party_doctype"], "Lead")
        self.assertEqual(
            [source["status"] for source in result["sources"]],
            ["available", "unavailable", "empty"],
        )
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["summary"], "Website Visit · High")
        self.assertNotIn("message", result["items"][0])
        self.assertNotIn("private message body", json.dumps(result))
        self.assertEqual(result["items"][0]["source_route"], "/app/crm-signal/SIG-0001")

    def test_missing_source_doctype_is_not_connected_not_empty(self):
        def exists(doctype, name):
            return name != "Quotation"

        def get_list(doctype, **kwargs):
            return [{"name": "LEAD-0001"}] if doctype == "Lead" else []

        with (
            _as_administrator(),
            patch.object(frappe.db, "exists", side_effect=exists),
            patch.object(frappe, "has_permission", return_value=True),
            patch.object(frappe, "get_meta", return_value=_Meta()),
            patch.object(frappe, "get_list", side_effect=get_list),
            patch.object(explorer, "now_datetime", return_value="2026-11-02 11:00:00"),
        ):
            result = explorer.get_explorer_timeline("Lead", "LEAD-0001")

        self.assertEqual(result["sources"][1]["status"], "not_connected")


if __name__ == "__main__":
    unittest.main()
