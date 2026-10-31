# CRM Signals — Source Audit Report

**Input:** `crm_signals_v15_v16.zip` (14 source/package files)  
**Audit type:** Static source review  
**Audit date:** 2026-10-31  
**Target:** Frappe / ERPNext v15 and v16  
**Overall assessment:** Baseline not production-ready. Initial remediation and repeatable unit checks are now included; live-site acceptance remains outstanding.

## Executive assessment
The package is a CRM Signals extension, not a complete CRM. It implements a signal DocType, inbound endpoint, two document hooks, browser toast notifications, and a daily digest. It does not implement lead capture/qualification workflows, full contact lifecycle, sales pipeline management, campaigns, omnichannel communication, customer service, or full CRM analytics.

## Findings

### Critical — Guest can create CRM Signal records
**Baseline:** `api.py` used `@frappe.whitelist(allow_guest=True)`, inserted with `ignore_permissions=True`, and manually committed.  
**Impact:** Unauthenticated record creation, spam/data pollution, notification abuse, and bypass of role controls.  
**Remediation:** Guest access and manual commit removed; authenticated session required; input and references validated; normal document permission checks used; realtime publishing deferred until commit. Arbitrary recipient selection removed.  
**Remaining:** Verify authentication and permissions on real v15/v16 sites; configure gateway rate limits.

### High — Quotation party link may target the wrong DocType
**Baseline:** `party_name` was copied into Lead/Customer Link fields without validating the party type.  
**Impact:** Invalid links or misassociated signals.  
**Remediation:** Resolve `quotation_to` and validate the corresponding Lead/Customer.  
**Remaining:** Run Quotation fixtures against supported ERPNext site versions.

### High — Digest Lead status filter is unverified
**Baseline:** Filtered Lead status to `Open` and `Lead` without evidence these are valid site statuses.  
**Impact:** Incorrect count or query failure.  
**Remediation:** Removed guessed status values and labelled metric “Leads not modified in more than 3 days.” This remains a proxy, not proof of stalled sales activity.  
**Remaining:** Confirm business semantics and test against target schema.

### High — Opportunity signal mapping/status semantics are not verified
**Baseline:** Triggered only on `Replied` and read `customer`/`lead` fields directly.  
**Impact:** Missed or incorrectly linked activity.  
**Remediation:** Derive single party from `opportunity_from` and `party_name`.  
**Remaining:** `Replied` remains hard-coded until business status rules and target schema are confirmed.

### Medium — Realtime recipient policy was unsafe
**Baseline:** API accepted arbitrary `assigned_user`; otherwise event was published without user targeting. Hooks also published without a recipient rule.  
**Impact:** Over-broad delivery or disclosure.  
**Remediation:** Added shared recipient resolution from related Lead/Customer owner and active ToDo assignments. Notifications are published into per-user rooms after commit, with a minimal payload and no site-wide fallback.  
**Remaining:** Verify that those users can read the CRM Signal record under deployed permission rules.

### Medium — Digest HTML was not escaped
**Baseline:** Party names and quotation IDs interpolated into HTML directly.  
**Impact:** HTML injection in email.  
**Remediation:** Escape externally sourced names and IDs.

### Medium — No tests or compatibility evidence
**Baseline:** No tests, CI, or pinned framework dependencies; README claimed tested v15/v16.  
**Impact:** Compatibility cannot be established.  
**Remediation:** Added static contract tests, notification routing unit tests, and a Python-version GitHub Actions workflow. These do not replace database-backed Frappe v15/v16 integration tests. The README now treats compatibility as unverified.

## Component assessment

| Component | Baseline | Current state |
|---|---|---|
| Signal DocType | Basic fields/roles, no server validation | Basic server validation added; access model hardening remains |
| Inbound API | Critical guest write and permission bypass | Auth-only, validation added, normal create permission enforced |
| Quotation hook | Unsafe party mapping | Mapping corrected, live fixture pending |
| Opportunity hook | Unverified party/status fields | Mapping improved; status decision pending |
| Desk notification | Toast and list refresh | Minimal payload and per-user recipient targeting added; record permission test pending |
| Daily digest | Guessed status filter; unsafe HTML | HTML escaped; stale-modified proxy used; live semantics pending |
| Packaging/docs | Unsupported compatibility claim | Claim removed; roadmap and security notes added |

## Verification performed
- Inspected all 14 files in the supplied ZIP.
- Parsed DocType JSON successfully.
- Parsed Python source with `ast` and ran `compileall`.
- Ran 7 local tests covering DocType metadata, syntax, webhook security contracts, and per-user recipient routing.

## Not verified
- No Frappe/ERPNext bench or site was available.
- No database-backed integration tests, Desk browser tests, Socket.IO tests, or scheduler tests ran.
- No clean install/migration/uninstall test was performed on v15 or v16.

## Recommendation
Do not deploy until signal record read permissions are verified, the remaining P0/P1 slices are completed, and the acceptance matrix passes on clean, pinned v15 and v16 environments.
