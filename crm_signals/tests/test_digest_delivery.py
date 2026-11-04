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
        def capture_log_error(*, message, title):
            logged_errors.append((title, message))

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


    def test_digest_recipients_exclude_disabled_and_non_system_users(self):
        baseline_recipients = set(tasks._resolve_digest_recipients([]))
        suffix = frappe.generate_hash(length=8)

        def make_user(label, *, enabled=1, user_type="System User", role=None):
            data = {
                "doctype": "User",
                "email": f"crm-signal-digest-{label}-{suffix}@example.com",
                "first_name": f"CRM Signal Digest {label}",
                "user_type": user_type,
                "enabled": enabled,
                "send_welcome_email": 0,
            }
            if role:
                data["roles"] = [{"role": role}]
            return frappe.get_doc(data).insert(ignore_permissions=True)

        manager = make_user("manager", role="Sales Manager")
        disabled_manager = make_user("disabled-manager", enabled=0, role="Sales Manager")
        # An explicitly configured recipient must be a real Desk System User.
        # Give these non-manager accounts a Sales User role so the fixture does
        # not rely on a role-less account being promoted to System User.
        extra = make_user("extra", role="Sales User")
        disabled_extra = make_user("disabled-extra", enabled=0, role="Sales User")
        website_extra = make_user("website-extra", user_type="Website User")

        self.assertEqual(extra.user_type, "System User")
        self.assertEqual(disabled_extra.user_type, "System User")
        self.assertEqual(website_extra.user_type, "Website User")
        self.assertEqual(
            frappe.db.get_value("User", {"email": extra.email}, "name"),
            extra.name,
        )

        recipients = tasks._resolve_digest_recipients(
            [
                extra.email,
                disabled_extra.email,
                website_extra.email,
                extra.email,
                "missing-crm-signal-digest-user@example.com",
            ]
        )

        self.assertEqual(
            recipients,
            sorted(baseline_recipients | {manager.name, extra.name}),
        )
        self.assertNotIn(disabled_manager.name, recipients)
        self.assertNotIn(disabled_extra.name, recipients)
        self.assertNotIn(website_extra.name, recipients)

    def test_digest_queue_failure_isolated_retried_and_redacted(self):
        suffix = frappe.generate_hash(length=8)
        failed_recipient = f"crm-signal-digest-failed-{suffix}@example.com"
        successful_recipient = f"crm-signal-digest-success-{suffix}@example.com"
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

        logged_errors = []

        def capture_log_error(*, message, title):
            logged_errors.append((title, message))

        def queue_email(**kwargs):
            if kwargs["recipients"] == [failed_recipient]:
                raise RuntimeError(f"SMTP queue rejected {failed_recipient}")

        try:
            with (
                patch.object(
                    tasks,
                    "_site_now",
                    return_value=datetime(2026, 11, 1, 12, 0, tzinfo=ZoneInfo("UTC")),
                ),
                patch.object(
                    tasks,
                    "_resolve_digest_recipients",
                    return_value=[failed_recipient, successful_recipient],
                ),
                patch.object(tasks, "_build_recipient_digest", return_value="<p>test</p>"),
                patch("frappe.sendmail", side_effect=queue_email) as first_sendmail,
                patch("frappe.log_error", side_effect=capture_log_error),
            ):
                first_result = tasks.send_daily_signals_digest()
                frappe.db.commit()

            self.assertEqual(first_result["status"], "partial")
            self.assertEqual(first_result["recipient_count"], 1)
            self.assertEqual(first_result["failed_recipient_count"], 1)
            self.assertEqual(first_sendmail.call_count, 2)
            self.assertEqual(
                logged_errors,
                [(
                    "CRM Signals digest queue failed (recipient redacted)",
                    "Queue error type: RuntimeError",
                )],
            )
            self.assertNotIn(failed_recipient, repr(logged_errors))
            self.assertNotIn("SMTP queue rejected", repr(logged_errors))

            saved = frappe.get_doc("CRM Signals Settings", "CRM Signals Settings")
            self.assertEqual(
                json.loads(saved.last_digest_queued_recipients or "[]"),
                [successful_recipient],
            )

            with (
                patch.object(
                    tasks,
                    "_site_now",
                    return_value=datetime(2026, 11, 1, 12, 0, tzinfo=ZoneInfo("UTC")),
                ),
                patch.object(
                    tasks,
                    "_resolve_digest_recipients",
                    return_value=[failed_recipient, successful_recipient],
                ),
                patch.object(tasks, "_build_recipient_digest", return_value="<p>test</p>"),
                patch("frappe.sendmail") as retry_sendmail,
                patch("frappe.log_error", side_effect=capture_log_error),
            ):
                retry_result = tasks.send_daily_signals_digest()
                frappe.db.commit()

            self.assertEqual(retry_result["status"], "queued")
            self.assertEqual(retry_result["recipient_count"], 2)
            self.assertEqual(retry_result["failed_recipient_count"], 0)
            retry_sendmail.assert_called_once()
            self.assertEqual(
                retry_sendmail.call_args.kwargs["recipients"],
                [failed_recipient],
            )
            saved.reload()
            self.assertEqual(
                json.loads(saved.last_digest_queued_recipients or "[]"),
                sorted([failed_recipient, successful_recipient]),
            )
        finally:
            for field, value in previous.items():
                frappe.db.set_value("CRM Signals Settings", None, field, value)
            frappe.db.commit()
