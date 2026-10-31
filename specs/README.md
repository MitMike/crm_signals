# Specifications

Product and engineering changes start with a short spec before implementation.

Each spec must include:

1. **Problem and user** — who needs the change and what decision or action it supports.
2. **Goals and non-goals** — what is included and what is explicitly deferred.
3. **Source of truth** — DocTypes, fields, integrations and permission rules.
4. **Metric or behavior definitions** — filters, date windows, currency basis and edge cases. Avoid ambiguous terms such as “revenue” when the calculation is actually invoiced value or cash received.
5. **Acceptance criteria** — observable, testable statements written before implementation.
6. **Validation mapping** — unit, integration and browser E2E tests that prove each acceptance criterion.
7. **Risks and rollout** — migrations, permissions, compatibility and operational checks.

## Required test progression

- **Unit tests** validate calculation rules, edge cases, permission-denied behavior and invalid inputs.
- **Bench integration tests** install the app on a real Frappe/ERPNext site and run tests inside the Bench Python environment.
- **Browser E2E tests** log in through Frappe and exercise the actual Desk page and its API. Seeded records should be unique and cleaned up after each test.
- **Migration checks** must be added when a change introduces patches or schema changes.

A spec is not complete because the code exists. Its acceptance criteria must be linked to passing tests, and any unsupported source must be reported as unavailable rather than replaced with guessed data.
