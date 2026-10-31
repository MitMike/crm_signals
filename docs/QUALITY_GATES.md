# Engineering quality gates

## What runs automatically

Every push and pull request runs the main code and compatibility checks:

- **Quality Checks:** Ruff lint, ESLint, Oxlint, Prettier checks for E2E/tooling files, Python compile, configuration validation and pytest across Python 3.10, 3.11, 3.12 and 3.14. Coverage is published as a build artifact. Ruff formatting is applied locally through the pre-commit formatter hook.
- **Bench Integration and E2E:** creates real Frappe + ERPNext sites on v15/Python 3.11 and v16/Python 3.14, installs this app, migrates the site and runs the Python suite inside the Bench environment. The v16 lane also starts Frappe and runs the Playwright browser test.
- **Security Scanning:** runs Semgrep against application Python code and uploads SARIF findings to GitHub code scanning.

The **Dependency Security Audit** workflow runs on pull requests that change dependency-related files, weekly, and on manual dispatch. It runs `pip-audit` for Python and `npm audit` for JavaScript tooling; moderate- and higher-severity npm findings fail the audit.

The browser test authenticates through Frappe, opens /app/sahdev-dashboard, checks that the endpoint returns billing data and verifies that the Billing Realization section renders without browser JavaScript errors.

## Local commands

Python:

    python -m pip install -e .
    python -m pip install pytest pytest-cov ruff pre-commit
    ruff check crm_signals tests
    ruff format crm_signals tests
    python -m pytest -q --cov=crm_signals

JavaScript and browser E2E:

    npm ci
    npm run lint:js
    # Use npm install only when intentionally changing dependency versions.
    npm run format:check
    npm audit --audit-level=moderate
    npx playwright install chromium
    BASE_URL=http://test.local:8000 npm run test:e2e

Hooks:

    pre-commit install
    pre-commit run --all-files

## Development rules

1. Start a feature with a short spec in specs/.
2. Define metric calculations, source fields, permissions, empty/unavailable states and edge cases before writing UI.
3. Add unit tests for calculations and permission behavior.
4. Add a Bench-backed integration test when touching Frappe APIs, DocTypes, hooks, permissions or migrations.
5. Add or update Playwright E2E coverage for user-visible workflows.
6. Keep test data isolated and clean it up. Never write tests against production data.
7. Do not bypass Frappe permissions to make dashboards appear populated.
8. Treat green mocked tests as necessary, not sufficient: the Bench and E2E jobs are the compatibility gate.

## Merge policy

Configure the GitHub repository's branch protection/ruleset to require the Lint and static checks, Python unit tests, and Bench Integration and E2E checks before merging to the protected branch. Keep direct pushes to the protected branch disabled.
