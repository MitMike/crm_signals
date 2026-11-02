# Engineering quality gates

## What runs automatically

Every push and pull request runs the main code checks. Bench compatibility runs on every pull request and on pushes to `main` (not on the same feature-branch commit twice):

- **Quality Checks:** Ruff lint, ESLint, Oxlint, Prettier checks for E2E/tooling files, Python compile, configuration validation and pytest across Python 3.10, 3.11, 3.12 and 3.14. Coverage is published as a build artifact. Ruff formatting is applied locally through the pre-commit formatter hook.
- **Bench Integration and E2E:** creates real Frappe + ERPNext sites on v15/Python 3.11 and v16/Python 3.14, installs this app, migrates the site and runs the Python suite inside the Bench environment. The v16 lane also starts Frappe and runs the Playwright browser test. It now also runs a read-only D1/D2 Sales Compass query-contract smoke against real ERPNext DocTypes on both supported lines; the separate pinned Frappe v16.5.0 lane runs the same check alongside the Helpdesk D3 contract and aggregate fixture.
- **Security Scanning:** runs Semgrep against application Python code and uploads SARIF findings to GitHub code scanning.

The **Dependency Security Audit** workflow runs on pull requests that change dependency-related files, weekly, and on manual dispatch. It runs `pip-audit` for Python and `npm audit` for JavaScript tooling; moderate- and higher-severity npm findings fail the audit.

The Playwright suite authenticates through Frappe, verifies the live S.A.H.D.E.V. dashboard and CRM Signals Console, exercises dashboard empty/unavailable states, checks Sales User/non-sales visibility, and opens CRM Signals Settings to apply a preset and customise it. The v16 Bench lane runs the browser suite against the installed app.

## Local commands

Python:

    python -m pip install -e .
    python -m pip install pytest pytest-cov ruff pre-commit
    ruff check crm_signals tests scripts
    ruff format crm_signals tests scripts
    python -m pytest -q --cov=crm_signals

JavaScript and browser E2E:

    npm ci
    npm run lint:js
    # Use npm install only when intentionally changing dependency versions.
    npm run format:check
    npm audit --audit-level=moderate
    npx playwright install chromium
    BASE_URL=http://test.local:8000 npm run test:e2e

Code size and complexity:

    python scripts/check_code_standards.py

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
9. Keep production source files and functions cohesive; use the graduated size/complexity rules below as review signals, not as a reason to split code mechanically.

## Merge policy

Configure the GitHub repository's branch protection/ruleset to require the Lint and static checks, Python unit tests, and Bench Integration and E2E checks before merging to the protected branch. Keep direct pushes to the protected branch disabled.


## File size and complexity policy

A line count is a maintainability signal, not a quality score. These limits apply to non-blank physical lines in hand-written source files; comments count so that the measure is predictable. Documentation, configuration, lockfiles, generated/minified bundles, vendored dependencies and build output are not source targets.

| Scope | Review warning | Hard CI limit |
|---|---:|---:|
| Production source file | 500 lines | 800 lines |
| Test/E2E source file | 800 lines | 1,200 lines |
| Production Python function/method | 50 lines | 100 lines |
| Production JavaScript function | — | 100 lines |
| Test Python function/method | 80 lines | 150 lines |
| Python/JavaScript cyclomatic complexity | Review above 10 | 15 |

Python complexity is enforced by Ruff's C901 rule. JavaScript complexity and function length are enforced by ESLint. Python function length and cross-language file length are enforced by the repository checker.

A warning requires a maintainability review and should normally result in a refactoring issue or a documented decision to retain the structure. A hard-limit failure blocks the quality workflow. Do not split cohesive modules or tests solely to satisfy a metric; extract by responsibility, dependency boundary or independently testable behavior.

The test thresholds are intentionally more permissive because test suites often group fixtures and lifecycle scenarios. Generated, minified and vendored assets are excluded. Any other file-level exception must be added to `scripts/code_standards_exceptions.json` with its exact repository-relative path and a reason. Keep exceptions narrow; do not add directory-wide or wildcard exemptions. Review the exception register periodically and remove entries when the underlying file is refactored.

Run the checker locally with `python scripts/check_code_standards.py`. Warnings do not fail the check; exceeding a hard limit does.


## Change-aware CI execution (ADR-074)

Pull requests now use path-aware execution while preserving the existing required check names:

- The Quality workflow always runs its static Python/configuration checks. JavaScript tooling installation, ESLint/Oxlint and Prettier run for JavaScript, tooling or E2E changes; the four-version Python unit matrix runs for Python, test, script or Python packaging changes. Pushes retain the full applicable quality checks.
- Bench Integration and E2E retains its existing required matrix check contexts, but PR matrix jobs are skipped for documentation-only, workspace-only and other non-runtime changes. Backend Python, DocType/Page, public asset, test and packaging changes still run both supported Frappe lanes. Pushes to `main` and manual dispatch retain the full matrix.
- The pinned Frappe v16.5.0 / ERPNext / Helpdesk validation is narrowed to backend, DocType/Page, public asset, test and packaging paths. It remains available by manual dispatch.
- Python and npm dependency caches are enabled where their lock/manifest inputs are known. Security scanning remains required for every PR; dependency audits retain their dependency-file and scheduled triggers.

Stable required-check gate jobs retain the exact status names expected by the main ruleset; they depend on the conditional test-execution jobs and fail if a relevant test run fails. This avoids relying on skipped matrix jobs to publish matrix-specific required contexts. Skipped execution jobs are intentional only when their change filter proves the relevant source surface was not modified. GitHub's required check contexts are preserved; no branch protection requirement is removed. A change to the filters, job names or required contexts must be tested against both metadata-only and runtime-code PRs before merge. The first CI run of this change is the validation of that behavior; do not assume time savings until measured.
