"""Unit tests for CRM Signals configuration parsing and presets."""

from crm_signals.settings import PRESETS, parse_recipients, parse_statuses


def test_status_parser_trims_and_deduplicates_case_insensitively():
    assert parse_statuses("Replied\n Open \nreplied, Quotation") == [
        "Replied",
        "Open",
        "Quotation",
    ]


def test_recipient_parser_trims_and_deduplicates():
    assert parse_recipients("sales@example.com\n SALES@example.com,ops@example.com") == [
        "sales@example.com",
        "ops@example.com",
    ]


def test_presets_have_explicit_digest_and_event_defaults():
    assert set(PRESETS) == {"Balanced", "Sales Focused", "Executive"}
    assert PRESETS["Balanced"]["lead_stale_days"] == 3
    assert PRESETS["Sales Focused"]["lead_stale_days"] == 2
    assert PRESETS["Executive"]["quotation_threshold"] == 500000
    assert all(config["opportunity_trigger_statuses"] == "Replied" for config in PRESETS.values())
