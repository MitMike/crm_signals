import json
from pathlib import Path

from crm_signals.settings import (
    DEFAULT_DIGEST_TIME,
    DEFAULT_HIGH_VALUE_THRESHOLD,
    DEFAULT_LEAD_STALE_DAYS,
    DEFAULT_OPPORTUNITY_SIGNAL_STATUSES,
)


ROOT = Path(__file__).resolve().parents[1]


def _doctype(path):
    return json.loads((ROOT / path).read_text())


def test_crm_signals_settings_is_singleton_with_company_currency_defaults():
    settings = _doctype(
        "crm_signals/crm_signals/doctype/crm_signals_settings/crm_signals_settings.json"
    )
    assert settings["issingle"] is True
    fields = {field["fieldname"]: field for field in settings["fields"]}
    assert fields["company"]["options"] == "Company"
    assert fields["company_currency"]["options"] == "Currency"
    assert fields["high_value_quotation_threshold"]["options"] == "company_currency"
    assert fields["opportunity_signal_statuses"]["default"] == "Replied"
    assert fields["lead_stale_days"]["default"] == "3"
    assert fields["digest_time"]["default"] == "08:30:00"
    assert fields["additional_digest_recipients"]["options"] == "CRM Signals Digest Recipient"


def test_digest_recipient_child_table_links_user():
    recipient = _doctype(
        "crm_signals/crm_signals/doctype/crm_signals_digest_recipient/crm_signals_digest_recipient.json"
    )
    assert recipient["istable"] is True
    fields = {field["fieldname"]: field for field in recipient["fields"]}
    assert fields["user"]["fieldtype"] == "Link"
    assert fields["user"]["options"] == "User"


def test_stage_one_defaults_are_explicit_and_unit_safe():
    assert DEFAULT_HIGH_VALUE_THRESHOLD == 200000
    assert DEFAULT_OPPORTUNITY_SIGNAL_STATUSES == ("Replied",)
    assert DEFAULT_LEAD_STALE_DAYS == 3
    assert DEFAULT_DIGEST_TIME == "08:30:00"
