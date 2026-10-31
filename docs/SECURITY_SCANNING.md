# Security scanning

The repository keeps security scanning separate from the normal quality and compatibility gates.

## Automated checks

- **Semgrep** scans application Python code on pushes, pull requests, and a weekly schedule using the Semgrep Python and security-audit rule packs.
- Findings are uploaded as SARIF to GitHub code scanning. The workflow fails when Semgrep reports an error-level finding.
- **Dependabot** checks the Python project dependencies and GitHub Actions weekly and opens update pull requests.

## Scope and limitations

The project currently declares no third-party Python runtime dependencies in `pyproject.toml`. Dependabot monitors that declaration as it changes. Semgrep scans the application source; it does not replace review of Frappe/ERPNext framework versions, deployment configuration, secrets handling, or site-specific permissions.

Review every finding in context. Do not suppress a finding solely to make CI green; document the reason and keep any suppression as narrow as possible.

## Local scan

Install Semgrep and run:

```bash
python -m pip install semgrep
semgrep scan --config p/python --config p/security-audit crm_signals
```
