# Development quality gates

This repository uses a layered quality process inspired by Frappe Guard, Frappe Wiki, and Frappe CRM.

## Local checks

Install tools:

```bash
python -m pip install ruff pre-commit pytest pip-audit
npm install --global prettier eslint
pre-commit install
```

Before pushing:

```bash
ruff check crm_signals tests
ruff format --check crm_signals tests
prettier --check "**/*.{js,css,json,yml,yaml}"
eslint "crm_signals/**/*.js"
pre-commit run --all-files
python -m pytest -q
pip-audit .
```

Pre-commit runs whitespace, conflict-marker, AST, JSON, TOML, YAML, Ruff, Prettier and ESLint checks on staged files.

## CI gates

Every push and pull request runs:
1. Ruff lint and format validation.
2. Prettier and ESLint.
3. Generic pre-commit checks.
4. Semgrep static analysis.
5. Dependency vulnerability audit.
6. Unit and static contract tests on Python 3.10, 3.11, 3.12 and 3.14.
7. A clean Frappe v16 Bench + MariaDB + Redis install, migration/build, and app test run on Python 3.14.

## Test strategy

- Unit tests: deterministic calculations, status handling, edge cases, and data contracts.
- Static contracts: Desk route registration, workspace shortcuts, hooks, metadata and security invariants.
- Bench integration: real Frappe APIs, DocType metadata, migrations, permissions, scheduler hooks and framework compatibility.
- Browser E2E (next phase): authenticated Chromium checks for Signals, Sales Compass, billing drill-down, role restrictions and empty/error states. E2E must run against the clean-site Bench integration fixture; mocked DOM tests are not a substitute.

## Pull request policy

Do not merge if any required gate fails. All user-facing metrics need:
- an explicit source DocType and field,
- an explicit date range and status filters,
- a documented currency basis,
- permission-aware retrieval,
- tests for empty data, permissions and boundary cases.

Frappe v15 runtime integration should remain a separate compatibility job once the supported version/site matrix is clarified. The primary deploy target for this app is the user's Frappe v16 / Python 3.14 environment.
