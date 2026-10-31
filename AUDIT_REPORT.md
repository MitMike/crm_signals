# CRM Signals — Source Audit Report

**Input:** crm_signals_v15_v16.zip (14 source/package files)  
**Audit type:** Static source review  
**Audit date:** 2026-10-31  
**Target:** Frappe / ERPNext v15 and v16  
**Overall assessment:** Baseline not production-ready. Initial remediation and repeatable unit checks are now included; live-site acceptance remains outstanding.

## Executive assessment
The package is a CRM Signals extension, not a complete CRM. It implements a signal DocType, inbound endpoint, two document hooks, browser toast notifications, and a daily digest. It does not implement lead capture/qualification workflows, full contact lifecycle, sales pipeline management, campaigns, omnichannel communication, customer service, or full CRM analytics.

## Findings

### Critical — Guest can create CRM Signal records
**Baseline:** api.py used guest whitelist, inserted with permission bypass, and manually committed.  
**Impact:** Unauthenticated record creation, spam/data pollution, notification abuse, and bypass of role controls.  
**Remediation:** Guest access and manual commit removed; endpoint restricted to POST; authenticated session and typed payload validation enforced; normal document permission checks used; realtime publishing deferred until commit. Arbitrary recipient selection removed.  
**Remaining:** Verify authentication and permissions on real v15/v16 sites; configure gateway rate limits.

### High — Quotation party link may target the wrong DocType
**Baseline:** party_name was copied into Lead/Customer Link fields without validating the party type.  
**Impact:** Invalid links or misassociated signals.  
**Remediation:** Resolve quotation_to and validate the corresponding Lead/Customer.  
**Remaining:** Run Quotation fixtures against supported ERPNext site versions.

### High — Digest Lead status filter is unverified
**Baseline:** Filtered Lead status to Open and Lead without evidence these are valid site statuses.  
**Impact:** Incorrect count or query failure.  
**Remediation:** Removed guessed status values and labelled metric “Leads not modified in more than 3 days.” This remains a proxy, not proof of stalled sales activity. Enabled System User recipient filtering added.  
**Remaining:** Confirm business semantics and test against target schema.

### High — Opportunity signal mapping/status semantics are not verified
**Baseline:** Triggered only on Replied and read customer/lead fields directly.  
**Impact:** Missed or incorrectly linked activity.  
**Remediation:** Derive single party from opportunity_from and party_name.  
**Remaining:** Replied remains hard-coded until business status rules and target schema are confirmed.

### Medium — Realtime recipient policy was unsafe
**Baseline:** API accepted arbitrary assigned_user; otherwise event was published site-wide. Hooks also published without a recipient rule.  
**Impact:** Over-broad delivery or disclosure.  
**Remediation:** Added shared recipient resolution from related Lead/Customer owner and active ToDo assignments. Notifications are published into per-user rooms after commit, with a minimal payload and no site-wide fallback.  
**Remaining:** Confirm actual recipient permissions against each deployed site's role configuration.

### High — CRM Signal records were broadly visible to Sales Users
**Baseline:** DocType permissions granted Sales User read/write across CRM Signal rows; no record-level hook restricted visibility.  
**Impact:** Sales users could browse signals for unrelated leads/customers.  
**Remediation:** Added Frappe has_permission and permission_query_conditions hooks. Non-manager users must own or be actively assigned to the related Lead/Customer and retain parent read access. Sales Manager/System Manager use their role permissions.  
**Remaining:** Verify list, direct fetch, report, export, and Desk form behavior on live v15/v16 sites.

### Medium — Digest HTML was not escaped
**Baseline:** Party names and quotation IDs interpolated into HTML directly.  
**Impact:** HTML injection in email.  
**Remediation:** Escape externally sourced names and IDs.

### Medium — No tests or compatibility evidence
**Baseline:** No tests, CI, or pinned framework dependencies; README claimed tested v15/v16.  
**Impact:** Compatibility cannot be established.  
**Remediation:** Added static contract tests, notification routing and permission unit tests, and a Python-version GitHub Actions workflow. These do not replace database-backed Frappe v15/v16 integration tests. The README now treats compatibility as unverified.

## Verification performed
- Inspected all 14 files in the supplied ZIP.
- Parsed DocType JSON successfully.
- Parsed Python source with ast and ran compileall.
- Ran 15 local tests covering DocType metadata, syntax, webhook security contracts, notification routing, and record access rules.

## Not verified
- No Frappe/ERPNext bench or site was available.
- No database-backed integration tests, Desk browser tests, Socket.IO tests, or scheduler tests ran.
- No clean install/migration/uninstall test was performed on v15 or v16.

## Recommendation
Do not deploy until the remaining P0/P1 work is completed and the acceptance matrix passes on clean, pinned v15 and v16 environments. In particular, verify record permissions and confirm Lead/Opportunity field and status semantics on both target versions.
