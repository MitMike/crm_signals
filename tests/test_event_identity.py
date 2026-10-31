"""Tests for stable event identity hashing."""

from crm_signals.event_identity import build_source_event_key


def test_same_source_event_produces_the_same_key():
    first = build_source_event_key("Quotation", "QTN-0001", "submit:2026-11-01 08:30:00")
    second = build_source_event_key("Quotation", "QTN-0001", "submit:2026-11-01 08:30:00")
    assert first == second
    assert len(first) == 64


def test_different_source_or_event_identity_produces_a_different_key():
    first = build_source_event_key("Quotation", "QTN-0001", "submit:1")
    assert first != build_source_event_key("Quotation", "QTN-0002", "submit:1")
    assert first != build_source_event_key("Opportunity", "QTN-0001", "submit:1")
    assert first != build_source_event_key("Quotation", "QTN-0001", "submit:2")


def test_incomplete_source_identity_is_not_deduplicated():
    assert build_source_event_key("Quotation", "QTN-0001", None) is None
