"""Bench-backed concurrency tests for idempotent daily digest queueing."""

import json
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

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
    from crm_signals import tasks


@unittest.skipIf(frappe is None, "Requires the Frappe Bench integration environment")
class TestDigestDeliveryConcurrency(FrappeTestCase):
    def test_overlapping_workers_queue_one_digest_per_recipient_and_date(self):
        """Two workers racing for the same recipient must create one queue request."""
        suffix = frappe.generate_hash(length=8)
        recipient = f"crm-signal-digest-{suffix}@example.com"
        settings = frappe.get_single("CRM Signals Settings")
        fields = (
            "enabled",
            "enable_daily_digest",
            "digest_time",
            "lead_stale_days",
            "last_digest_queued_date",
            "last_digest_queued_recipients",
            "last_digest_status",
        )
        previous = {field: settings.get(field) for field in fields}

        new_values = {
            "enabled": 1,
            "enable_daily_digest": 1,
            "digest_time": "00:00:00",
            "lead_stale_days": 3,
            "last_digest_queued_date": "2026-10-31",
            "last_digest_queued_recipients": "[]",
            "last_digest_status": "",
        }
        for field, value in new_values.items():
            frappe.db.set_value("CRM Signals Settings", None, field, value)
        frappe.db.commit()

        site = frappe.local.site
        both_workers_ready = threading.Barrier(2)
        thread_state = threading.local()
        original_locking_load = tasks._load_digest_settings_for_update
        worker_errors = []
        logged_errors = []
        original_log_error = frappe.log_error

        def capture_log_error(*, message, title):
            logged_errors.append((title, message))
            return original_log_error(message=message, title=title)

        def synchronized_locking_load():
            if not getattr(thread_state, "initial_load_complete", False):
                thread_state.initial_load_complete = True
                both_workers_ready.wait(timeout=20)
            return original_locking_load()

        def run_digest_worker():
            try:
                frappe.init(site=site)
                frappe.connect(site=site)
                frappe.set_user("Administrator")
                result = tasks.send_daily_signals_digest()
                frappe.db.commit()
                return result
            except Exception as error:
                worker_errors.append(repr(error))
                try:
                    frappe.db.rollback()
                except Exception:
                    pass
                raise
            finally:
                frappe.destroy()

        try:
            with (
                patch.object(
                    tasks,
                    "_site_now",
                    return_value=datetime(2026, 11, 1, 12, 0, tzinfo=ZoneInfo("UTC")),
                ),
                patch.object(tasks, "_resolve_digest_recipients", return_value=[recipient]),
                patch.object(tasks, "_build_recipient_digest", return_value="<p>test</p>"),
                patch.object(
                    tasks,
                    "_load_digest_settings_for_update",
                    side_effect=synchronized_locking_load,
                ),
                patch("frappe.sendmail") as sendmail,
                patch("frappe.log_error", side_effect=capture_log_error),
            ):
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [executor.submit(run_digest_worker) for _ in range(2)]
                    results = [future.result(timeout=60) for future in futures]

            self.assertEqual(worker_errors, [])
            self.assertEqual(logged_errors, [], msg=repr(logged_errors))
            self.assertEqual(
                sorted(result["status"] for result in results),
                ["already_queued", "queued"],
            )
            self.assertEqual(sendmail.call_count, 1)
            self.assertEqual(sendmail.call_args.kwargs["recipients"], [recipient])
            self.assertTrue(sendmail.call_args.kwargs["delayed"])

            saved_settings = frappe.get_doc(
                "CRM Signals Settings",
                "CRM Signals Settings",
                for_update=True,
            )
            self.assertEqual(
                json.loads(saved_settings.last_digest_queued_recipients or "[]"),
                [recipient],
            )
            self.assertEqual(str(saved_settings.last_digest_queued_date)[:10], "2026-11-01")
            frappe.db.commit()
        finally:
            for field, value in previous.items():
                frappe.db.set_value("CRM Signals Settings", None, field, value)
            frappe.db.commit()
