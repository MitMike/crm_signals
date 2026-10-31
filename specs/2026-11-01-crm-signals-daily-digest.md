# CRM Signals — Daily sales digest

**Status:** Implemented baseline; target-site semantics and currency formatting require hardening.

## Problem and user

Sales Managers need one concise morning summary of Leads that may need attention and Quotation records expiring that day. The digest must not overstate the meaning of stale records or send information to disabled/unrelated accounts.

## Goals

- Run once daily at a configurable site-local time.
- Summarize Leads not modified for longer than a configured number of days.
- List submitted, open Quotations whose valid_till is today.
- Email only enabled System Users with the Sales Manager role, plus any explicitly configured recipients.
- Escape user-controlled content and format money in the correct currency.
- Isolate delivery failures and avoid duplicate sends for the same digest date.

## Current baseline

The existing scheduler invokes crm_signals.tasks.send_daily_signals_digest at 08:30. It counts Leads where modified is older than three days, and fetches Quotations with docstatus 1, status Open and valid_till equal to today. It sends to enabled System Users with Sales Manager role. Quotation names and party names are HTML-escaped.

The Lead metric is exactly "Leads not modified in more than 3 days". It is not proof of no call, email, meeting or other communication. Until a communication-based definition exists, do not label it "stalled", "untouched" or "no activity".

## Calculation contract

- Digest date: current date in the verified Frappe site timezone.
- Not-recently-modified Leads: count of Lead records with modified strictly earlier than current date minus configured stale_days. The default stale_days is 3.
- Expiring Quotations: docstatus = 1, status = Open and valid_till = digest date.
- Displayed amount: grand_total plus source/company currency. Do not prepend INR or any currency symbol unless the currency is actually known.
- Missing DocType, field or permission/configuration: report that section as unavailable in diagnostics; never pretend it is a successful zero.

## Recipient and delivery contract

- Resolve recipients from Has Role for Sales Manager and explicitly configured additional digest recipients.
- Filter to enabled System Users and deduplicate.
- Never send to Guest, disabled users or arbitrary addresses supplied in a document.
- Generate the digest from permission-safe, validated source data. The scheduler runs in a trusted server context, but site policy must still constrain the information sent to recipients.
- Use a digest-date idempotency key so a scheduler retry cannot send duplicate copies. Record the run state and recipient count without logging secrets or full sensitive document contents.
- A failed recipient delivery must be logged and retried according to Frappe mail queue behavior; it must not duplicate successfully delivered mail.

## Content and security

Escape every party name, document name and other user-controlled HTML value. Prefer Frappe's standard email templates/escaping utilities. Avoid inline raw HTML concatenation for untrusted values. Do not include credentials, tokens or full sensitive record payloads. Email links must be authenticated Desk routes.

## Acceptance criteria

| ID | Requirement | Validation |
|---|---|---|
| DIG-AC1 | Lead count follows the configured modified-date rule and threshold boundary | Unit tests at 2, 3 and 4 days |
| DIG-AC2 | Digest wording says "not modified", not "no activity" | Rendered email snapshot |
| DIG-AC3 | Only submitted Open Quotations valid today are listed | Bench fixture with open, expired, draft, cancelled and future quotes |
| DIG-AC4 | Amounts use the actual Company/source currency | Multi-currency Bench fixture |
| DIG-AC5 | Names and document IDs are HTML-escaped | Security test with HTML/script payloads |
| DIG-AC6 | Only enabled System User Sales Managers and configured users receive mail | Recipient unit + Bench tests |
| DIG-AC7 | Retry of same digest date does not duplicate delivery | Idempotency/retry test |
| DIG-AC8 | Missing schema/permissions are visible as unavailable diagnostics | Bench permission/configuration fixture |
| DIG-AC9 | Scheduler runs at the configured site-local time | Scheduler integration test on supported versions |

## Validation mapping

Add or extend tests/test_tasks.py for date boundaries, recipient selection, currency rendering, escaping and duplicate-run behavior. Exercise the installed scheduler in the Frappe Bench matrix. Include an email-rendering snapshot and a target-site smoke test with actual Sales Manager accounts.

## Open operational inputs

The target site must confirm timezone, stale_days, approved recipients, Company default currency and whether the Lead modified timestamp is an acceptable proxy for attention. The code defaults are preserved only as defaults; they are not business-policy confirmation.
