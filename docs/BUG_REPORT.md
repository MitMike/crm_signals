# Bug Report Register

This is the durable record of confirmed defects reported by users or found during engineering review. Keep entries open until the fix is merged, verified in the relevant environment, and the regression-prevention check is in place.

## Workflow

1. Give every defect a stable ID (`BUG-YYYY-NNN`).
2. Record the user-visible symptom, affected area/environment, reproduction evidence, expected behavior, actual behavior, severity and discovery date. Separate confirmed facts from hypotheses.
3. Link the fixing PR/commit and the matching entry in [Fix Report](FIX_REPORT.md).
4. Add a regression test or explicit verification step that would fail if the defect returned. Prefer an automated test; use a documented manual UAT check only when automation is not practical.
5. Search for the same pattern in related screens/components before closing.
6. Mark status accurately: **Open**, **Fix in review**, **Merged**, **Code-verified**, or **UAT-verified**. A merged PR is not automatically UAT-verified.
7. If a later change reintroduces a closed defect, reopen the same ID and link the regression-causing change. Do not create a duplicate report.

## Confirmed bugs

### BUG-2026-001 — CRM Signals dashboard lost horizontal inset

- **Status:** Fix in review
- **Reported:** 2026-11-02
- **Reported by:** User, from local UAT screenshot
- **Area:** CRM Signals Dashboard / page wrapper CSS
- **Environment:** Local Frappe UAT (`frappe.localhost`); browser screenshot supplied
- **Symptom:** Dashboard content starts flush against the left edge of the Desk content area; the previously present horizontal inset is missing.
- **Expected:** Dashboard content has consistent left and right spacing from the Desk content boundary, without changing the existing dashboard grid/card layout.
- **Confirmed cause:** `.crm-signals-dashboard` in `crm_signals/crm_signals/page/crm_signals_dashboard/crm_signals_dashboard.css` declared `padding: 20px 0 32px`, setting both horizontal paddings to zero.
- **Severity:** UI regression / usability; no data or permission impact identified.
- **Fix:** Restore 24px left and right padding while preserving 20px top and 32px bottom padding.
- **Fix PR:** [#78](https://github.com/MitMike/crm_signals/pull/78) (open at time of recording).
- **Regression prevention:** Keep the horizontal padding declaration explicit; add/retain a CSS/UI regression assertion or a documented UAT visual check at desktop and mobile widths. Verify related CRM Signals pages if they share this wrapper or stylesheet.
- **Closure evidence required:** PR merged; relevant CI green; UAT refreshed/rebuilt assets and cache; screenshot confirms the inset at desktop and mobile widths. Until the UAT check is recorded, do not label this UAT-verified.

## Entry template

Copy this block for each new confirmed defect:

### BUG-YYYY-NNN — Short, observable title

- **Status:** Open
- **Reported:**
- **Area:**
- **Environment / version:**
- **Symptom:**
- **Expected:**
- **Actual:**
- **Reproduction / evidence:**
- **Severity / impact:**
- **Confirmed cause:** Unknown until evidenced; do not guess.
- **Fix PR / commit:**
- **Regression test / prevention:**
- **Closure evidence required:**
