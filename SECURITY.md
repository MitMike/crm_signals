# Security Notes

## Webhook authentication
The webhook is a server-to-server integration endpoint. Do not expose it anonymously. Authenticate as a dedicated Frappe user using supported API key/secret authentication over HTTPS, and grant only the permissions needed to create CRM Signal records. Rotate credentials and keep them in an external secret manager. Never put secrets in URLs, browser code, source control, or logs.

## Data handling
Signals and Lead/Customer references may contain confidential customer information. Do not broadcast complete records to every Desk session. Notify only authorized recipients and fetch full details through permission-checked APIs.

## Deployment requirements
- HTTPS end to end.
- Rate limiting at the reverse proxy/API gateway.
- Dedicated integration user; never Administrator credentials.
- Audit integration access and webhook invocations.
- Review role permissions and retention before production use.
