"""Tests for the read-only target-site preflight report."""

import importlib
import sys
import types


def load_diagnostics(monkeypatch):
    fake = types.ModuleType("frappe")
    fake.__version__ = "16.5.0"
    fake.db = types.SimpleNamespace(
        exists=lambda doctype, name: name in {
            "CRM Signal", "Lead", "Customer", "Opportunity", "Quotation",
            "Sales Invoice", "Payment Entry", "HD Ticket",
            "HD Service Level Agreement",
        },
        get_single_value=lambda *args: "Asia/Kolkata",
    )
    fake.utils = types.SimpleNamespace(now_datetime=lambda: "2026-11-02 12:00:00")
    fake.get_installed_apps = lambda: ["frappe", "erpnext", "crm_signals", "helpdesk"]
    fake.get_all = lambda doctype, **kwargs: {
        "Company": [
            {"name": "IN Company", "default_currency": "INR"},
            {"name": "EU Company", "default_currency": "EUR"},
            {"name": "UK Company", "default_currency": "GBP"},
        ],
        "Workflow": [
            {
                "name": "Lead Flow",
                "document_type": "Lead",
                "workflow_state_field": "workflow_state",
            },
        ],
        "Workflow Document State": [
            {"state": "Qualified", "doc_status": 0},
            {"state": "Converted", "doc_status": 1},
        ],
    }.get(doctype, [])
    meta = types.SimpleNamespace(
        module="CRM",
        fields=[
            types.SimpleNamespace(
                fieldname="status",
                label="Status",
                fieldtype="Select",
                options="Open\nClosed",
                permlevel=1,
            ),
        ],
        permissions=[
            {"role": "Sales User", "read": 1, "permlevel": 0},
            {"role": "Sales Manager", "read": 1, "permlevel": 0},
            {"role": "System Manager", "read": 1, "permlevel": 0},
            {"role": "Sales User", "read": 0, "permlevel": 1},
        ],
    )
    fake.get_meta = lambda doctype: meta
    monkeypatch.setitem(sys.modules, "frappe", fake)
    monkeypatch.setitem(
        sys.modules,
        "crm_signals.settings",
        types.SimpleNamespace(
            get_signal_settings=lambda: {
                "enabled": True,
                "enable_external_ingestion": False,
                "enable_quotation_signals": True,
                "enable_opportunity_signals": True,
                "enable_daily_digest": True,
                "opportunity_trigger_statuses": ["Replied"],
                "lead_stale_days": 3,
                "digest_time": "08:30:00",
                "digest_extra_recipients": ["private@example.com"],
                "quotation_threshold": 200000,
                "threshold_currency": "INR",
                "company_thresholds": [
                    {
                        "company": "EU Company",
                        "quotation_threshold": 50000,
                        "currency": "EUR",
                    },
                ],
            },
        ),
    )
    monkeypatch.delitem(sys.modules, "crm_signals.diagnostics", raising=False)
    return importlib.import_module("crm_signals.diagnostics")


def test_preflight_report_is_read_only_and_excludes_recipient_addresses(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    source_revision = {"available": True, "commit_sha": "a" * 40}
    monkeypatch.setattr(diagnostics, "_source_revision", lambda: source_revision)
    report = diagnostics.get_site_preflight_report()

    assert report["read_only"] is True
    assert report["http_whitelisted"] is False
    assert report["framework"]["frappe_version"] == "16.5.0"
    assert report["framework"]["crm_signals_source"] == source_revision
    assert report["crm_signals_settings"]["opportunity_trigger_statuses"] == ["Replied"]
    assert "private@example.com" not in repr(report)
    assert "Static metadata is not proof" in report["acceptance_warning"]
    assert not getattr(diagnostics.get_site_preflight_report, "is_whitelisted", False)


def test_preflight_company_thresholds_require_exact_currency_match(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    report = diagnostics.get_site_preflight_report()
    thresholds = {
        row["company"]: row
        for row in report["crm_signals_settings"]["company_thresholds"]
    }

    assert thresholds["IN Company"]["threshold_source"] == "legacy_exact_currency"
    assert thresholds["IN Company"]["threshold_amount"] == 200000
    assert thresholds["EU Company"]["threshold_source"] == "company_override"
    assert thresholds["EU Company"]["threshold_amount"] == 50000
    assert thresholds["EU Company"]["threshold_currency"] == "EUR"
    assert thresholds["UK Company"]["threshold_source"] == "suppressed_currency_mismatch"
    assert thresholds["UK Company"]["threshold_amount"] is None


def test_preflight_includes_workflow_states_and_static_field_permissions(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    report = diagnostics.get_site_preflight_report()

    workflow = report["active_lead_opportunity_workflows"]["items"][0]
    assert workflow["state_field"] == "workflow_state"
    assert [state["state"] for state in workflow["states"]] == ["Qualified", "Converted"]

    lead = report["doctypes"]["Lead"]
    assert lead["required_fields"] == [{"fieldname": "status", "present": True, "permlevel": 1}]
    assert lead["fields"][0]["permlevel"] == 1
    assert lead["fields"][0]["options"] == ["Open", "Closed"]
    assert lead["role_read_permissions"] == [
        {"role": "Sales User", "read": True, "permlevel": 0},
        {"role": "Sales Manager", "read": True, "permlevel": 0},
        {"role": "System Manager", "read": True, "permlevel": 0},
        {"role": "Sales User", "read": False, "permlevel": 1},
    ]
    assert lead["permission_boundary"] == "static DocPerm only; not effective user access"

    ticket = report["doctypes"]["HD Ticket"]
    assert all(not field["present"] for field in ticket["required_fields"])


def test_preflight_source_revision_reports_exact_full_sha(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    sha = "a" * 40
    commands = []

    monkeypatch.setattr(
        diagnostics.importlib,
        "import_module",
        lambda app: types.SimpleNamespace(
            __file__="/bench/apps/crm_signals/crm_signals/__init__.py"
        ),
    )

    def fake_run(command, **kwargs):
        commands.append((command, kwargs))
        return types.SimpleNamespace(stdout=f"{sha}\n")

    monkeypatch.setattr(diagnostics.subprocess, "run", fake_run)

    assert diagnostics._source_revision() == {"available": True, "commit_sha": sha}
    command, options = commands[0]
    assert command[0:2] == ["git", "-C"]
    assert command[-3:] == ["rev-parse", "--verify", "HEAD"]
    assert options["check"] is True
    assert options["capture_output"] is True
    assert options["timeout"] == 5


def test_preflight_source_revision_fails_closed_without_git_checkout(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    monkeypatch.setattr(
        diagnostics.importlib,
        "import_module",
        lambda app: types.SimpleNamespace(
            __file__="/bench/apps/crm_signals/crm_signals/__init__.py"
        ),
    )

    def failed_run(command, **kwargs):
        raise diagnostics.subprocess.CalledProcessError(
            128, command, stderr="private checkout path"
        )

    monkeypatch.setattr(diagnostics.subprocess, "run", failed_run)

    result = diagnostics._source_revision()
    assert result == {"available": False, "reason": "git_query_failed"}
    assert "private checkout path" not in repr(result)


def test_preflight_source_revision_rejects_non_sha_output(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    monkeypatch.setattr(
        diagnostics.importlib,
        "import_module",
        lambda app: types.SimpleNamespace(
            __file__="/bench/apps/crm_signals/crm_signals/__init__.py"
        ),
    )
    monkeypatch.setattr(
        diagnostics.subprocess,
        "run",
        lambda *args, **kwargs: types.SimpleNamespace(stdout="main\n"),
    )

    assert diagnostics._source_revision() == {
        "available": False,
        "reason": "invalid_revision",
    }



def test_preflight_source_revision_reports_git_timeout(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    monkeypatch.setattr(
        diagnostics.importlib,
        "import_module",
        lambda app: types.SimpleNamespace(
            __file__="/bench/apps/crm_signals/crm_signals/__init__.py"
        ),
    )

    def timed_out(command, **kwargs):
        raise diagnostics.subprocess.TimeoutExpired(command, timeout=5)

    monkeypatch.setattr(diagnostics.subprocess, "run", timed_out)

    assert diagnostics._source_revision() == {
        "available": False,
        "reason": "git_timeout",
    }


def test_preflight_source_revision_reports_missing_git(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    monkeypatch.setattr(
        diagnostics.importlib,
        "import_module",
        lambda app: types.SimpleNamespace(
            __file__="/bench/apps/crm_signals/crm_signals/__init__.py"
        ),
    )
    monkeypatch.setattr(
        diagnostics.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError()),
    )

    assert diagnostics._source_revision() == {
        "available": False,
        "reason": "git_unavailable",
    }
