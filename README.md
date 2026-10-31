# CRM Signals for Frappe & ERPNext

A small Frappe app that adds event-driven CRM signals, Desk notifications, and a scheduled sales digest. **This is an extension to ERPNext CRM, not a complete CRM implementation.**

## Implemented scope
- CRM Signal DocType for signal type, priority, Lead/Customer reference, message, and read state.
- Authenticated POST endpoint at /api/method/crm_signals.api.ingest_signal.
- Document hooks for high-value submitted quotations and a configured Opportunity status transition.
- Realtime notifications routed to related document owners and active ToDo assignees; no site-wide fallback.
- Record-level read/write permission hooks for linked-party owners and assignees.
- Scheduled digest for Leads not modified in more than three days and submitted quotations expiring today; only enabled System User Sales Managers receive it.

## Compatibility
The source targets Frappe/ERPNext v15 and v16 APIs, but compatibility is **unverified until CI and clean-site acceptance tests pass on both version lines**. See IMPLEMENTATION_PLAN.md. The supplied archive contained no test evidence for its original v15/v16 compatibility claim.

## Installation
```bash
bench --site <site-name> install-app crm_signals
bench --site <site-name> migrate
bench build --app crm_signals
bench restart
```

## Webhook authentication
Use a dedicated integration user and Frappe API key/secret over HTTPS. The endpoint does not allow Guest access. Grant only the create permission required by the integration. Do not use Administrator credentials. Enforce TLS and gateway rate limiting, rotate credentials, and never put secrets in source control or logs. See SECURITY.md.

Example:
```bash
curl -X POST 'https://<site>/api/method/crm_signals.api.ingest_signal' \
  -H 'Authorization: token <api_key>:<api_secret>' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'signal_type=Website Visit' \
  --data-urlencode 'message=Visited product pricing page' \
  --data-urlencode 'lead=LEAD-00001'
```

## Configuration still required
- Confirm high-value quotation threshold (currently 200,000 in the source's numeric currency units; message formatting currently displays ₹ and must be aligned with company currency policy).
- Confirm which Opportunity statuses should trigger activity signals.
- Confirm Lead inactivity semantics and whether the digest should use Lead modification time or actual communication activity.
- Verify record-level permissions in Desk/list/report/export workflows on both supported versions.
- Validate exact field/status semantics on the deployed ERPNext v15/v16 site.

## Developer checks
Run:
```bash
python -m compileall -q crm_signals
python -m pytest -q
```
