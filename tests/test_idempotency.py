import hashlib

from crm_signals.idempotency import build_source_event_key


def test_source_event_key_is_deterministic():
    first = build_source_event_key("erpnext", "Quotation", "QTN-0001", "submit:1")
    second = build_source_event_key("erpnext", "Quotation", "QTN-0001", "submit:1")

    assert first == second
    assert len(first) == hashlib.sha256().digest_size * 2


def test_source_event_key_is_scoped_to_source_and_namespace():
    baseline = build_source_event_key("erpnext", "Quotation", "QTN-0001", "submit:1")

    assert baseline != build_source_event_key("erpnext", "Quotation", "QTN-0002", "submit:1")
    assert baseline != build_source_event_key("provider-a", "Quotation", "QTN-0001", "submit:1")
    assert baseline != build_source_event_key("erpnext", "Opportunity", "QTN-0001", "submit:1")


def test_missing_source_event_id_disables_deduplication():
    assert build_source_event_key("erpnext", "Quotation", "QTN-0001", None) is None
