# Security scanning

The repository keeps dependency auditing separate from the normal quality and compatibility gates.

## Automated checks

- **Semgrep** scans application Python code on pushes, pull requests, and a weekly schedule using the Semgrep Python and security-audit rule packs.
- Findings are uploaded as SARIF to GitHub code scanning. The workflow fails when Semgrep reports an error-level finding.
- **Dependabot** checks the Python project dependencies, npm development tooling, and GitHub Actions weekly and opens update pull requests.
- **Dependency Security Audit** runs `pip-audit` against the installed Python environment and `npm audit` against the JavaScript tooling dependencies. It runs when dependency-related files change in a pull request, weekly, and on manual dispatch. npm findings at moderate severity or higher fail the job.

## Scope and limitations

The project currently declares no third-party Python runtime dependencies in `pyproject.toml`. Dependabot and `pip-audit` monitor the Python dependency declaration and installed environment as they change. The npm packages in `package.json` support linting, formatting and browser E2E tests; they are development/CI dependencies, not Frappe application runtime dependencies.

Semgrep scans the application source; it does not replace review of Frappe/ERPNext framework versions, deployment configuration, secrets handling, or site-specific permissions.

Review every finding in context. Do not suppress a finding solely to make CI green; document the reason and keep any suppression as narrow as possible.

## Local scans

Install and run Semgrep:

```bash
python -m pip install semgrep
semgrep scan --config p/python --config p/security-audit crm_signals
```

Run dependency audits:

```bash
python -m pip install pip-audit
pip-audit
npm install --ignore-scripts
npm audit --audit-level=moderate
```
