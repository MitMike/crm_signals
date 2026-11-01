"""Bench-backed retry tests for the transactional CRM Signal event outbox."""

import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from types import SimpleNamespace
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
    from crm_signals.events import on_quotation_submit
    from crm_signals.signal_outbox import (
        SignalOutboxPersistenceError,
        _retry_delay_minutes,
        enqueue_signal_event,
        process_pending_signal_outbox,
        process_signal_outbox_event,
    )


@unittest.skipIf(frappe is None, "Requires the Frappe Bench integration environment")
class TestSignalOutbox(FrappeTestCase):
    def test_outbox_persistence_failure_is_distinct_from_delivery_failure(self):
        payload = {
            "signal_type": "High-Value Quote",
            "message": "Outbox persistence failure test",
            "priority": "High",
            "source_doctype": "Quotation",
            "source_name": "OUTBOX-PERSISTENCE-FAILURE",
            "source_event_id": "submit:persistence-failure",
        }
        with patch(
            "crm_signals.signal_outbox._get_or_create_outbox",
            side_effect=RuntimeError("database unavailable"),
        ):
            with self.assertRaises(SignalOutboxPersistenceError):
                enqueue_signal_event(**payload)

    def test_quotation_hook_aborts_when_outbox_cannot_be_persisted(self):
        quotation = SimpleNamespace(
            company="Example Company",
            base_grand_total=250,
            currency="USD",
            grand_total=250,
            quotation_to="Lead",
            party_name="LEAD-OUTBOX-TEST",
            name="QUOT-OUTBOX-TEST",
            modified="2026-11-01 12:00:00",
        )
        settings = {
            "enabled": True,
            "enable_quotation_signals": True,
            "quotation_threshold": 100,
            "threshold_currency": "USD",
        }
        with (
            patch("crm_signals.events.get_signal_settings", return_value=settings),
            patch("crm_signals.events.get_company_default_currency", return_value="USD"),
            patch(
                "crm_signals.events._party_links",
                return_value={"lead": None, "customer": None},
            ),
            patch(
                "crm_signals.signal_outbox._get_or_create_outbox",
                side_effect=RuntimeError("database unavailable"),
            ),
            patch("frappe.log_error"),
        ):
            with self.assertRaises(SignalOutboxPersistenceError):
                on_quotation_submit(quotation)

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
        event_key = build_source_event_key("Quotation", source_name, source_event_id)
        self.assertFalse(frappe.db.exists("CRM Signal", {"source_event_key": event_key}))

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

    def test_retry_exhaustion_moves_event_to_failed(self):
        suffix = frappe.generate_hash(length=8)
        payload = {
            "signal_type": "Opportunity Activity",
            "message": f"Outbox exhaustion test {suffix}",
            "priority": "Medium",
            "source_doctype": "Opportunity",
            "source_name": f"OUTBOX-OPP-{suffix}",
            "source_event_id": f"status:Open->Replied:{suffix}",
        }

        with (
            patch(
                "crm_signals.events.insert_signal_once",
                side_effect=RuntimeError("temporary database failure"),
            ),
            patch("frappe.log_error"),
        ):
            outbox_name = enqueue_signal_event(**payload)
            for _ in range(9):
                frappe.db.set_value(
                    "CRM Signal Outbox",
                    outbox_name,
                    "next_retry_at",
                    None,
                    update_modified=False,
                )
                result = process_signal_outbox_event(outbox_name)

        outbox = frappe.get_doc("CRM Signal Outbox", outbox_name)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(outbox.status, "Failed")
        self.assertEqual(outbox.attempt_count, 10)
        self.assertIsNone(outbox.next_retry_at)
        self.assertIsNone(outbox.signal)

        with patch("crm_signals.events.insert_signal_once") as insert_signal:
            skipped = process_signal_outbox_event(outbox_name)
        self.assertEqual(skipped["status"], "skipped")
        insert_signal.assert_not_called()

    def test_retry_worker_skips_events_before_next_retry_time(self):
        suffix = frappe.generate_hash(length=8)
        payload = {
            "signal_type": "High-Value Quote",
            "message": f"Outbox not-due test {suffix}",
            "priority": "High",
            "source_doctype": "Quotation",
            "source_name": f"OUTBOX-NOT-DUE-{suffix}",
            "source_event_id": f"submit:{suffix}",
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
        attempts = outbox.attempt_count
        result = process_signal_outbox_event(outbox_name)
        worker_result = process_pending_signal_outbox(limit=100)
        outbox.reload()

        self.assertEqual(result["status"], "not_due")
        self.assertEqual(worker_result["not_due"], 0)
        self.assertEqual(outbox.attempt_count, attempts)
        self.assertEqual(outbox.status, "Pending")

    def test_worker_filters_future_retries_before_applying_batch_limit(self):
        suffix = frappe.generate_hash(length=8)
        common = {
            "doctype": "CRM Signal Outbox",
            "signal_type": "High-Value Quote",
            "message": f"Outbox fairness test {suffix}",
            "priority": "High",
            "source_doctype": "Quotation",
            "status": "Pending",
            "attempt_count": 1,
        }
        future = frappe.get_doc({
            **common,
            "source_name": f"OUTBOX-FUTURE-{suffix}",
            "source_event_id": f"future:{suffix}",
            "next_retry_at": frappe.utils.now_datetime() + timedelta(minutes=30),
        }).insert(ignore_permissions=True)
        due = frappe.get_doc({
            **common,
            "source_name": f"OUTBOX-DUE-{suffix}",
            "source_event_id": f"due:{suffix}",
            "next_retry_at": None,
        }).insert(ignore_permissions=True)

        processed = []
        with (
            patch(
                "crm_signals.signal_outbox.process_signal_outbox_event",
                side_effect=lambda name: processed.append(name) or {"status": "completed"},
            ),
            patch("frappe.db.commit"),
        ):
            process_pending_signal_outbox(limit=1)

        self.assertEqual(processed, [due.name])
        self.assertNotIn(future.name, processed)

    def test_two_workers_process_one_outbox_event_once(self):
        suffix = frappe.generate_hash(length=8)
        source_name = f"OUTBOX-RACE-{suffix}"
        source_event_id = f"submit:{suffix}"
        outbox = frappe.get_doc({
            "doctype": "CRM Signal Outbox",
            "signal_type": "High-Value Quote",
            "message": f"Outbox concurrency test {suffix}",
            "priority": "High",
            "source_doctype": "Quotation",
            "source_name": source_name,
            "source_event_id": source_event_id,
            "status": "Pending",
            "attempt_count": 0,
        }).insert(ignore_permissions=True)
        outbox_name = outbox.name
        frappe.db.commit()

        site = frappe.local.site
        start_together = threading.Barrier(2)
        worker_errors = []

        def run_worker():
            try:
                frappe.init(site=site)
                frappe.connect(site=site)
                frappe.set_user("Administrator")
                start_together.wait(timeout=20)
                result = process_signal_outbox_event(outbox_name)
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

        signal_name = None
        try:
            with patch("crm_signals.notifications.notify_signal") as notify_signal:
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [executor.submit(run_worker) for _ in range(2)]
                    results = [future.result(timeout=60) for future in futures]

            self.assertEqual(worker_errors, [])
            self.assertEqual(
                sorted(result["status"] for result in results),
                ["completed", "skipped"],
            )
            self.assertEqual(notify_signal.call_count, 1)

            saved_outbox = frappe.get_doc("CRM Signal Outbox", outbox_name)
            signal_name = saved_outbox.signal
            self.assertTrue(signal_name)
            event_key = build_source_event_key("Quotation", source_name, source_event_id)
            self.assertEqual(
                frappe.get_all(
                    "CRM Signal",
                    filters={"source_event_key": event_key},
                    pluck="name",
                ),
                [signal_name],
            )
        finally:
            if not signal_name:
                signal_name = frappe.db.get_value(
                    "CRM Signal Outbox", outbox_name, "signal"
                )
            if frappe.db.exists("CRM Signal Outbox", outbox_name):
                frappe.delete_doc(
                    "CRM Signal Outbox",
                    outbox_name,
                    ignore_permissions=True,
                    force=True,
                )
            if signal_name and frappe.db.exists("CRM Signal", signal_name):
                frappe.delete_doc(
                    "CRM Signal",
                    signal_name,
                    ignore_permissions=True,
                    force=True,
                )
            frappe.db.commit()
