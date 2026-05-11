# Workflow: Manage Subscribers

## Objective
Maintain the newsletter subscriber list in `subscribers.csv` — adding, removing, and auditing subscribers correctly.

## Tool
`tools/manage_subscribers.py`

## File Location
`subscribers.csv` in the project root. Columns: `email, first_name, subscribed_date, unsubscribed_date, active`

**Never delete rows.** Set `active=false` instead to preserve the audit trail. This is required for GDPR compliance.

---

## Operations

### Add a Subscriber
```
python tools/manage_subscribers.py add --email user@example.com --name "FirstName"
```
- If the email already exists and is active: informs you, does nothing
- If the email exists but is inactive (previously unsubscribed): re-subscribes them
- Otherwise: adds new row with today's date

### Remove / Unsubscribe
```
python tools/manage_subscribers.py remove --email user@example.com
```
Sets `active=false` and records `unsubscribed_date`. The record is preserved.

### List All Active Subscribers
```
python tools/manage_subscribers.py list
```
Shows active count, total records, and a table of active subscribers.

### Export Active Subscribers
```
python tools/manage_subscribers.py export --output active_list.csv
```
Exports only active subscribers to a separate CSV file.

---

## CAN-SPAM / Legal Requirements

**United States (CAN-SPAM Act):**
- Every commercial email must include a working unsubscribe mechanism
- Unsubscribe requests must be honored within **10 business days** (process them immediately)
- Each email must include your physical mailing address or a clear statement of who you are

**European Union (GDPR):**
- Only email people who explicitly opted in
- Honor unsubscribe requests immediately
- Do not delete records (keep them with `active=false` for proof of consent/withdrawal)

**The unsubscribe link** in each newsletter points to a URL with a unique token. When someone clicks it:
1. You will need a handler (a Google Form, a simple web page, or a manual process) that reads the token and calls `manage_subscribers.py remove`
2. For a quick manual process: check the send log for the token-to-email mapping and run the remove command yourself

---

## Notes
- Email addresses are stored in lowercase to avoid duplicates from case differences
- The `subscribers.csv` file is in `.gitignore` to prevent accidentally committing personal data — verify this before pushing to a public repo
- For lists larger than ~1,000 subscribers, consider migrating to Google Sheets or a proper CRM for easier management
