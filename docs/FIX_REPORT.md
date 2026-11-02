# Fix Report Register

This is the durable record of defect fixes and the evidence that prevents regressions. Every fix must link to a bug ID in [Bug Report](BUG_REPORT.md). Do not record a fix as verified solely because code was written or a PR was opened.

## Fix policy

- Keep fixes minimal and scoped; avoid unrelated refactors.
- Fix the cause, not only the visible symptom.
- Add a regression test that fails on the old behavior whenever practical.
- Run the relevant lint, unit, integration and browser checks. Record what actually ran and what did not.
- Inspect related components/pages for the same defect pattern.
- Distinguish **CI-verified**, **merged**, and **UAT-verified**. These are separate states.
- For visual defects, capture/record before-and-after UAT evidence at representative desktop and mobile widths after asset rebuild/cache refresh.
- If a regression occurs, link it to the original bug and record which missing test or process allowed it through.

## Fixes

### FIX-2026-001 — Restore CRM Signals dashboard horizontal padding

- **Related bug:** [BUG-2026-001](BUG_REPORT.md#bug-2026-001--crm-signals-dashboard-lost-horizontal-inset)
- **Status:** In review; CI pending at time of recording
- **Date:** 2026-11-02
- **File:** `crm_signals/crm_signals/page/crm_signals_dashboard/crm_signals_dashboard.css`
- **Change:** Changed the dashboard wrapper from `padding: 20px 0 32px` to `padding: 20px 24px 32px`.
- **Scope:** One-line CSS correction. Existing vertical spacing, dashboard grid, cards and page behavior are unchanged.
- **PR:** [#78](https://github.com/MitMike/crm_signals/pull/78)
- **Regression prevention:** The bug register requires a CSS/UI regression assertion or documented UAT visual check; verify desktop and mobile widths and inspect related CRM Signals pages for the same zero-horizontal-padding pattern.
- **Validation evidence:** PR #78 opened. CI was queued/in progress when recorded. No UAT confirmation yet; local site requires the merged change to be pulled and assets/cache refreshed.
- **Remaining closure steps:** Confirm required CI; merge under branch protection; update UAT app; rebuild/clear relevant assets/cache; visually verify desktop and mobile; update both registers with evidence and final status.

## Entry template

### FIX-YYYY-NNN — Short fix title

- **Related bug:** BUG-YYYY-NNN
- **Status:** In review
- **Date:**
- **Files / components:**
- **Root cause:**
- **Change:**
- **PR / commit:**
- **Regression test added:**
- **Validation run and result:**
- **UAT evidence:**
- **Remaining work / limitations:**
