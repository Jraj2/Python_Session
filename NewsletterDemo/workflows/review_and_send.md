# Workflow: Review and Send

## Objective
Present the rendered newsletter to the user for approval, then deliver it to all active subscribers via SendGrid.

## CRITICAL RULE
**Never call `send_newsletter.py` without explicit user approval after the preview step.** There is no unsend. A mistake reaches every subscriber simultaneously. This workflow exists to prevent that.

## Tools Used
- `tools/preview_newsletter.py` — opens HTML in browser
- `tools/send_newsletter.py` — delivers via SendGrid

## Inputs
| Input | Description |
|---|---|
| `html_path` | Path to `.tmp/newsletter_{ts}.html` |
| `meta_path` | Path to `.tmp/newsletter_{ts}_meta.json` (contains subject line) |

## Steps

### 1. Open Preview
```
python tools/preview_newsletter.py --file <html_path>
```

### 2. PAUSE — Ask for Approval
After the browser opens, say to the user:

> "Your newsletter is open in your browser. Does it look correct?
> - Say **'approve and send'** to deliver to all subscribers
> - Describe any changes and I'll revise
> - Say **'cancel'** to abort without sending"

Do not proceed until the user responds.

### 3a. If Changes Requested
Go back to `generate_newsletter.md` Step 5 with the requested edits incorporated. Re-preview.

### 3b. If Cancelled
Acknowledge and stop. The HTML file stays in `.tmp/` for reference.

### 3c. If Approved — Dry Run First
Get the subject line from the meta JSON or confirm with the user.

Run a dry run to show recipient count:
```
python tools/send_newsletter.py --file <html_path> --subject "<subject>" --dry-run
```

Show the user: "Ready to send to X subscribers. Confirm?"

### 4. Live Send (Only After Explicit Confirmation)
```
python tools/send_newsletter.py --file <html_path> --subject "<subject>"
```

### 5. Report Results
Read the send log (`.tmp/send_log_{ts}.json`) and report:
- Total sent
- Any failures or bounces (with email addresses)
- Location of the log file

Remind user to check the SendGrid dashboard in 24 hours for open rates.

## SendGrid Setup Checklist (first time only)
1. Create a free account at sendgrid.com
2. Go to Settings → Sender Authentication → Single Sender Verification
3. Verify your sending email address (Gmail is fine for testing)
4. Go to Settings → API Keys → Create API Key (Full Access)
5. Add to `.env`: `SENDGRID_API_KEY=` and `SENDGRID_FROM_EMAIL=`

## Error Handling
| Error | Action |
|---|---|
| 401 Unauthorized | API key is wrong or missing — check `.env` |
| 403 Forbidden | Sender email not verified in SendGrid console |
| 429 Rate Limited | SendGrid free tier: 100 emails/day. Upgrade or wait 24h |
| Partial failures | Log affected emails, do not retry automatically — check the log and retry manually |
