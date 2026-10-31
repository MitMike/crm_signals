# CRM Signals — Source and Packaging Audit

**Audit date:** 2026-10-31  
**Target:** Frappe Pilot GitHub importer and Frappe/ERPNext v15–v16  
**Overall assessment:** The Pilot app-discovery failure is explained and the repository packaging fix is committed. Live installation is not yet verified.

## Exact cause of the Pilot error
The Pilot GitHub resolver fetches `pyproject.toml` from the selected branch, reads `[project].name`, and then checks for `<project-name>/hooks.py`. The repository had `crm_signals/hooks.py`, but no root `pyproject.toml`; therefore Pilot had no project name to resolve.

## Packaging/layout issue found at the same time
The repository declared `Crm Signals` in `crm_signals/modules.txt`, but the DocType was stored at `crm_signals/doctype/crm_signal`. Frappe's app structure requires module DocTypes under the module's directory. The intended path is `crm_signals/crm_signals/doctype/crm_signal`.

## Fix committed
- Added root `pyproject.toml` with `[project].name = "crm_signals"`.
- Added Flit build metadata and dynamic version from the app package.
- Declared intended compatibility:
  - `frappe = ">=15.0.0,<17.0.0"`
  - `erpnext = ">=15.0.0,<17.0.0"`
- Preserved the expected `crm_signals/hooks.py` resolver path.
- Added the default `Crm Signals` module package and moved the DocType metadata/controller/client script into it.
- Added CI tests checking the Pilot discovery contract and canonical DocType location.

## Validation boundary
I confirmed the new repository tree contains root `pyproject.toml`, the named `crm_signals/hooks.py`, and the module DocType path. The exact Pilot resolver source was inspected. I have not run Pilot itself or a Frappe bench against this repository; the new range declarations are not proof of v15/v16 runtime compatibility.

## What to do in Pilot
1. Close and reopen the import dialog.
2. Enter `https://github.com/MitMike/crm_signals`.
3. Select `main`.
4. Pilot should now resolve the app as `crm_signals`.
5. Import it, then install on a test site first.

See [FRAPPE_PILOT_IMPORT.md](FRAPPE_PILOT_IMPORT.md) for the focused troubleshooting guide.
