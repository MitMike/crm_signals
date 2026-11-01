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
    from crm_signals import signal_outbox
    from crm_signals.crm_signals.doctype.crm_signal_outbox.crm_signal_outbox import replay_failed_signal_outbox
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
    def test_outbox_uses_deterministic_source_key_as_name(self):
        meta = frappe.get_meta("CRM Signal Outbox")
        self.assertEqual(meta.autoname, "field:source_event_key")

    def test_outbox_records_are_read_only_for_system_managers(self):
        meta = frappe.get_meta("CRM Signal Outbox")
        permission = next(
            row for row in meta.permissions if row.role == "System Manager"
        )
        self.assertEqual(permission.read, 1)
        self.assertFalse(permission.write)
        self.assertFalse(permission.create)
        for fieldname in (
            "status",
            "signal_type",
            "priority",
            "message",
            "source_doctype",
            "source_name",
            "source_event_id",
            "source_event_key",
        ):
            self.assertTrue(meta.get_field(fieldname).read_only, fieldname)

    def test_manual_replay_requires_system_manager_and_preserves_attempt_history(self):
        suffix = frappe.generate_hash(length=8)
        outbox = frappe.get_doc({
            "doctype": "CRM Signal Outbox",
            "signal_type": "High-Value Quote",
            "message": f"Manual replay test {suffix}",
            "priority": "High",
            "source_doctype": "Quotation",
            "source_name": f"OUTBOX-MANUAL-{suffix}",
            "source_event_id": f"manual:{suffix}",
            "source_event_key": build_source_event_key("Quotation", f"OUTBOX-MANUAL-{suffix}", f"manual:{suffix}"),
            "status": "Failed",
            "attempt_count": 10,
            "last_error": "RuntimeError",
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        original_user = frappe.session.user
        try:
            frappe.set_user("Administrator")
            with patch("frappe.enqueue") as enqueue_job:
                result = replay_failed_signal_outbox(outbox.name)
            saved = frappe.get_doc("CRM Signal Outbox", outbox.name)
            self.assertEqual(result["status"], "Pending")
            self.assertEqual(saved.status, "Pending")
            self.assertEqual(saved.attempt_count, 10)
            self.assertEqual(saved.last_error, "RuntimeError")
            self.assertEqual(saved.replay_count, 1)
            self.assertEqual(saved.last_replayed_by, "Administrator")
            enqueue_job.assert_called_once()
            self.assertTrue(enqueue_job.call_args.kwargs["enqueue_after_commit"])
            self.assertTrue(saved.get_comments())
        finally:
            frappe.set_user(original_user)
            frappe.delete_doc("CRM Signal Outbox", outbox.name, ignore_permissions=True, force=True)
            frappe.db.commit()

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

    def test_failed_post_commit_delivery_is_retried_without_losing_source_event(self):
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
            patch("frappe.enqueue") as enqueue_job,
        ):
            outbox_name = enqueue_signal_event(**payload)
            enqueue_job.assert_called_once()
            self.assertTrue(enqueue_job.call_args.kwargs["enqueue_after_commit"])
            result = process_signal_outbox_event(outbox_name)

        outbox = frappe.get_doc("CRM Signal Outbox", outbox_name)
        self.assertEqual(result["status"], "pending")
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
            patch("frappe.enqueue"),
        ):
            outbox_name = enqueue_signal_event(**payload)
            process_signal_outbox_event(outbox_name)
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
            patch("frappe.enqueue"),
        ):
            outbox_name = enqueue_signal_event(**payload)
            process_signal_outbox_event(outbox_name)

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
            "source_event_key": build_source_event_key("Quotation", f"OUTBOX-FUTURE-{suffix}", f"future:{suffix}"),
            "next_retry_at": frappe.utils.now_datetime() + timedelta(minutes=30),
        }).insert(ignore_permissions=True)
        due = frappe.get_doc({
            **common,
            "source_name": f"OUTBOX-DUE-{suffix}",
            "source_event_id": f"due:{suffix}",
            "source_event_key": build_source_event_key("Quotation", f"OUTBOX-DUE-{suffix}", f"due:{suffix}"),
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


    def test_two_workers_enqueue_the_same_source_event_once(self):
        suffix = frappe.generate_hash(length=8)
        source_name = f"OUTBOX-ENQUEUE-RACE-{suffix}"
        source_event_id = f"submit:{suffix}"
        event_key = build_source_event_key("Quotation", source_name, source_event_id)
        payload = {
            "signal_type": "High-Value Quote",
            "message": f"Outbox enqueue race test {suffix}",
            "priority": "High",
            "source_doctype": "Quotation",
            "source_name": source_name,
            "source_event_id": source_event_id,
        }
        site = frappe.local.site
        both_reads_complete = threading.Barrier(2)
        thread_state = threading.local()
        original_lookup = signal_outbox._find_outbox_name

        def synchronized_lookup(key):
            name = original_lookup(key)
            if not getattr(thread_state, "initial_lookup_complete", False):
                thread_state.initial_lookup_complete = True
                both_reads_complete.wait(timeout=20)
            return name

        def enqueue_in_worker():
            frappe.init(site=site)
            frappe.connect(site=site)
            frappe.set_user("Administrator")
            try:
                name = enqueue_signal_event(**payload)
                frappe.db.commit()
                return name
            finally:
                frappe.destroy()

        outbox_name = None
        signal_name = None
        try:
            with (
                patch.object(
                    signal_outbox,
                    "_find_outbox_name",
                    side_effect=synchronized_lookup,
                ),
                patch("crm_signals.notifications.notify_signal") as notify_signal,
                patch("frappe.enqueue") as enqueue_job,
                ThreadPoolExecutor(max_workers=2) as executor,
            ):
                futures = [executor.submit(enqueue_in_worker) for _ in range(2)]
                outbox_names = [future.result(timeout=60) for future in futures]

            self.assertEqual(outbox_names[0], outbox_names[1])
            self.assertEqual(enqueue_job.call_count, 2)
            self.assertTrue(all(
                call.kwargs.get("enqueue_after_commit")
                for call in enqueue_job.call_args_list
            ))
            with patch("crm_signals.notifications.notify_signal") as notify_signal:
                process_signal_outbox_event(outbox_names[0])
            self.assertEqual(notify_signal.call_count, 1)
            outbox_name = outbox_names[0]
            signal_names = frappe.get_all(
                "CRM Signal",
                filters={"source_event_key": event_key},
                pluck="name",
            )
            self.assertEqual(len(signal_names), 1)
            signal_name = signal_names[0]
            self.assertEqual(
                frappe.db.get_value("CRM Signal Outbox", outbox_name, "signal"),
                signal_name,
            )
        finally:
            if not outbox_name:
                outbox_name = frappe.db.get_value(
                    "CRM Signal Outbox", {"source_event_key": event_key}, "name"
                )
            if outbox_name and frappe.db.exists("CRM Signal Outbox", outbox_name):
                signal_name = signal_name or frappe.db.get_value(
                    "CRM Signal Outbox", outbox_name, "signal"
                )
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
            "source_event_key": build_source_event_key("Quotation", source_name, source_event_id),
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
