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
        get_value=lambda doctype, name, field: {
            "sales.user@example.invalid": 1,
            "sales.manager@example.invalid": 1,
            "non.sales@example.invalid": 1,
            "disabled.user@example.invalid": 0,
        }.get(name),
    )
    fake.utils = types.SimpleNamespace(now_datetime=lambda: "2026-11-02 12:00:00")
    fake.get_installed_apps = lambda: ["frappe", "erpnext", "crm_signals", "helpdesk"]
    fake.get_roles = lambda user: {
        "sales.user@example.invalid": ["Sales User"],
        "sales.manager@example.invalid": ["Sales Manager"],
        "non.sales@example.invalid": ["Employee"],
        "disabled.user@example.invalid": ["Sales User"],
    }.get(user, [])
    fake.has_permission = lambda doctype, ptype="read", user=None, throw=False: (
        user != "non.sales@example.invalid"
    )
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
    meta.get_permitted_fieldnames = lambda user=None: (
        ["status"] if user == "sales.manager@example.invalid" else []
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



def test_preflight_reports_effective_test_user_doctype_and_field_permissions(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    users = {
        "sales_user": "sales.user@example.invalid",
        "sales_manager": "sales.manager@example.invalid",
        "non_sales": "non.sales@example.invalid",
    }

    report = diagnostics.get_site_preflight_report(test_users=users)
    matrix = report["effective_user_permissions"]

    assert matrix["available"] is True
    assert matrix["reason"] is None
    assert matrix["profiles"]["sales_user"]["status"] == "checked"
    assert matrix["profiles"]["sales_user"]["role_membership_valid"] is True
    assert matrix["profiles"]["sales_user"]["doctype_read"]["Lead"] is True
    assert matrix["profiles"]["sales_user"]["required_field_read"]["Lead"]["status"] is False
    assert matrix["profiles"]["sales_manager"]["required_field_read"]["Lead"]["status"] is True
    assert matrix["profiles"]["non_sales"]["role_membership_valid"] is True
    assert matrix["profiles"]["non_sales"]["doctype_read"]["Lead"] is False
    assert matrix["profiles"]["non_sales"]["required_field_read"]["Lead"]["status"] is False
    assert "record-level User Permissions" in matrix["scope"]
    assert all(username not in repr(report) for username in users.values())


def test_preflight_rejects_disabled_and_administrator_test_accounts(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    report = diagnostics.get_site_preflight_report(
        test_users={
            "sales_user": "disabled.user@example.invalid",
            "sales_manager": "Administrator",
        }
    )
    profiles = report["effective_user_permissions"]["profiles"]

    assert profiles["sales_user"]["status"] == "user_disabled"
    assert profiles["sales_user"]["account_active"] is False
    assert profiles["sales_manager"]["status"] == "administrator_not_allowed"
    assert profiles["sales_manager"]["account_active"] is None



def test_preflight_rejects_wrong_role_and_duplicate_test_accounts(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    report = diagnostics.get_site_preflight_report(
        test_users={
            "sales_user": "sales.manager@example.invalid",
            "sales_manager": "sales.manager@example.invalid",
        }
    )
    profiles = report["effective_user_permissions"]["profiles"]

    assert profiles["sales_manager"]["status"] == "checked"
    assert profiles["sales_user"]["status"] == "duplicate_test_user"
    assert profiles["sales_manager"]["role_membership_valid"] is True

def test_preflight_without_test_users_marks_effective_matrix_unavailable(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    report = diagnostics.get_site_preflight_report()

    assert report["effective_user_permissions"] == {
        "available": False,
        "reason": "test_users_not_supplied",
        "profiles": {},
        "scope": (
            "DocType-level and field-level read checks only; record-level User Permissions, "
            "ownership and document-share visibility must still be tested with representative records."
        ),
    }


def test_preflight_rejects_unknown_test_user_profile(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)

    try:
        diagnostics.get_site_preflight_report(test_users={"administrator": "someone@example.invalid"})
    except ValueError as error:
        assert str(error) == "Unsupported test user profile"
    else:
        raise AssertionError("unknown profile must be rejected")

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
        if "--show-toplevel" in command:
            output = "/bench/apps/crm_signals\n"
        elif "status" in command:
            output = ""
        else:
            output = f"{sha}\n"
        return types.SimpleNamespace(stdout=output)

    monkeypatch.setattr(diagnostics.subprocess, "run", fake_run)

    assert diagnostics._source_revision() == {"available": True, "commit_sha": sha}
    assert commands[0][0][-2:] == ["rev-parse", "--show-toplevel"]
    assert commands[1][0][-3:] == ["status", "--porcelain", "--untracked-files=all"]
    assert commands[2][0][-3:] == ["rev-parse", "--verify", "HEAD"]
    for _, options in commands:
        assert options["check"] is True
        assert options["capture_output"] is True
        assert options["timeout"] == 5


def test_preflight_source_revision_rejects_parent_git_repository(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    commands = []
    monkeypatch.setattr(
        diagnostics.importlib,
        "import_module",
        lambda app: types.SimpleNamespace(
            __file__="/bench/apps/crm_signals/crm_signals/__init__.py"
        ),
    )

    def parent_repository_run(command, **kwargs):
        commands.append(command)
        return types.SimpleNamespace(stdout="/bench/apps\n")

    monkeypatch.setattr(diagnostics.subprocess, "run", parent_repository_run)

    result = diagnostics._source_revision()
    assert result == {"available": False, "reason": "repository_root_mismatch"}
    assert len(commands) == 1
    assert "crm_signals" not in repr(result)


def test_preflight_source_revision_fails_closed_for_dirty_checkout(monkeypatch):
    diagnostics = load_diagnostics(monkeypatch)
    commands = []
    monkeypatch.setattr(
        diagnostics.importlib,
        "import_module",
        lambda app: types.SimpleNamespace(
            __file__="/bench/apps/crm_signals/crm_signals/__init__.py"
        ),
    )

    def dirty_run(command, **kwargs):
        commands.append(command)
        output = "/bench/apps/crm_signals\n" if "--show-toplevel" in command else " M private.py\n"
        return types.SimpleNamespace(stdout=output)

    monkeypatch.setattr(diagnostics.subprocess, "run", dirty_run)

    result = diagnostics._source_revision()
    assert result == {"available": False, "reason": "working_tree_dirty"}
    assert len(commands) == 2
    assert commands[0][-2:] == ["rev-parse", "--show-toplevel"]
    assert commands[1][-3:] == ["status", "--porcelain", "--untracked-files=all"]
    assert "private.py" not in repr(result)


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

    def fake_run(command, **kwargs):
        if "--show-toplevel" in command:
            output = "/bench/apps/crm_signals\n"
        elif "status" in command:
            output = ""
        else:
            output = "main\n"
        return types.SimpleNamespace(stdout=output)

    monkeypatch.setattr(diagnostics.subprocess, "run", fake_run)

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

    def missing_git(command, **kwargs):
        raise FileNotFoundError()

    monkeypatch.setattr(diagnostics.subprocess, "run", missing_git)

    assert diagnostics._source_revision() == {
        "available": False,
        "reason": "git_unavailable",
    }



def test_preflight_source_revision_rejects_real_enclosing_git_repository(monkeypatch, tmp_path):
    diagnostics = load_diagnostics(monkeypatch)
    app_root = tmp_path / "bench" / "apps" / "crm_signals"
    package_dir = app_root / "crm_signals"
    package_dir.mkdir(parents=True)
    module_file = package_dir / "__init__.py"
    module_file.touch()

    diagnostics.subprocess.run(
        ["git", "init", "--quiet", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )
    diagnostics.subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=CRM Signals test",
            "-c",
            "user.email=crm-signals-test@example.invalid",
            "commit",
            "--allow-empty",
            "-m",
            "parent repository",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )
    monkeypatch.setattr(
        diagnostics.importlib,
        "import_module",
        lambda app: types.SimpleNamespace(__file__=str(module_file)),
    )

    result = diagnostics._source_revision()

    assert result == {"available": False, "reason": "repository_root_mismatch"}


def test_preflight_source_revision_uses_real_clean_sha_and_rejects_untracked_file(
    monkeypatch, tmp_path
):
    diagnostics = load_diagnostics(monkeypatch)
    app_root = tmp_path / "bench" / "apps" / "crm_signals"
    package_dir = app_root / "crm_signals"
    package_dir.mkdir(parents=True)
    module_file = package_dir / "__init__.py"
    module_file.write_text("# real Git preflight fixture\n", encoding="utf-8")

    diagnostics.subprocess.run(
        ["git", "init", "--quiet", str(app_root)],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )

    def run_git(*args):
        return diagnostics.subprocess.run(
            ["git", "-C", str(app_root), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )

    run_git("add", "crm_signals/__init__.py")
    run_git(
        "-c",
        "user.name=CRM Signals test",
        "-c",
        "user.email=crm-signals-test@example.invalid",
        "commit",
        "-m",
        "clean preflight fixture",
    )
    expected_sha = run_git("rev-parse", "--verify", "HEAD").stdout.strip().lower()

    monkeypatch.setattr(
        diagnostics.importlib,
        "import_module",
        lambda app: types.SimpleNamespace(__file__=str(module_file)),
    )
    real_run = diagnostics.subprocess.run
    commands = []

    def tracked_run(command, **kwargs):
        commands.append(command)
        return real_run(command, **kwargs)

    monkeypatch.setattr(diagnostics.subprocess, "run", tracked_run)

    assert diagnostics._source_revision() == {
        "available": True,
        "commit_sha": expected_sha,
    }
    assert len(commands) == 3
    assert commands[0][-2:] == ["rev-parse", "--show-toplevel"]
    assert commands[1][-3:] == ["status", "--porcelain", "--untracked-files=all"]
    assert commands[2][-3:] == ["rev-parse", "--verify", "HEAD"]

    commands.clear()
    (package_dir / "local_override.py").write_text("VALUE = 1\n", encoding="utf-8")

    dirty_result = diagnostics._source_revision()

    assert dirty_result == {"available": False, "reason": "working_tree_dirty"}
    assert len(commands) == 2
    assert commands[0][-2:] == ["rev-parse", "--show-toplevel"]
    assert commands[1][-3:] == ["status", "--porcelain", "--untracked-files=all"]
    assert "local_override.py" not in repr(dirty_result)
