# Frappe Pilot GitHub Import

## Why the repository was not detected

Pilot's GitHub resolver checks the selected branch at the repository root for:
1. `pyproject.toml`
2. A non-empty `[project].name`
3. A `<project-name>/hooks.py` file

The previous repository had `crm_signals/hooks.py`, but no root `pyproject.toml`. That is why the import dialog could not resolve an app.

## Fix applied

- Added root `pyproject.toml` with `[project].name = "crm_signals"`.
- Added the Flit build backend and dynamic version declaration.
- Declared bounded Frappe and ERPNext compatibility ranges for v15 and v16.
- Kept `crm_signals/hooks.py` at the path Pilot expects.
- Moved the CRM Signal DocType into the declared module directory: `crm_signals/crm_signals/doctype/crm_signal/`.

## Import steps

1. Confirm branch `main` contains the new root `pyproject.toml`.
2. Close the import dialog and reopen it (or clear/re-enter the repository URL) so Pilot re-runs repository resolution.
3. Enter `https://github.com/MitMike/crm_signals`.
4. Select `main`.
5. Pilot should resolve the app name as `crm_signals`.
6. Import it, then install it on a test site first.

## Compatibility declaration

```toml
[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<17.0.0"
erpnext = ">=15.0.0,<17.0.0"
```

These ranges express intended compatibility; they are not evidence of successful end-to-end testing on every v15/v16 release. Run clean-site installation and migration tests before production deployment.
