"""
Sends a rendered newsletter HTML to all active subscribers via SendGrid.
Usage:
  python tools/send_newsletter.py --file .tmp/newsletter_xxx.html --subject "My Subject"
  python tools/send_newsletter.py --file .tmp/newsletter_xxx.html --subject "..." --dry-run
Logs results to .tmp/send_log_{timestamp}.json.
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, Substitution

load_dotenv()

ROOT = Path(__file__).parent.parent
TMP = ROOT / ".tmp"
SUBSCRIBERS_FILE = ROOT / "subscribers.csv"
BATCH_SIZE = 100  # SendGrid allows up to 1000, keep lower for safety


def load_subscribers() -> list[dict]:
    if not SUBSCRIBERS_FILE.exists():
        sys.exit(f"subscribers.csv not found at {SUBSCRIBERS_FILE}. Run manage_subscribers.py to create it.")
    df = pd.read_csv(SUBSCRIBERS_FILE)
    active = df[df["active"] == True].to_dict("records")
    if not active:
        sys.exit("No active subscribers found. Add some with manage_subscribers.py.")
    return active


def make_unsubscribe_token(email: str, timestamp: str) -> str:
    import hashlib
    return hashlib.sha256(f"{email}:{timestamp}:newsletter".encode()).hexdigest()[:16]


def send(html_path: Path, subject: str, dry_run: bool = False) -> dict:
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SENDGRID_FROM_EMAIL")

    if not api_key:
        sys.exit("SENDGRID_API_KEY not set in .env")
    if not from_email:
        sys.exit("SENDGRID_FROM_EMAIL not set in .env")

    html_content = html_path.read_text(encoding="utf-8")
    subscribers = load_subscribers()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    print(f"{'[DRY RUN] ' if dry_run else ''}Sending to {len(subscribers)} subscribers...")

    results = {"sent": 0, "failed": 0, "errors": [], "dry_run": dry_run, "timestamp": timestamp}

    for i in range(0, len(subscribers), BATCH_SIZE):
        batch = subscribers[i : i + BATCH_SIZE]

        for sub in batch:
            email = sub["email"]
            first_name = sub.get("first_name", "there")
            token = make_unsubscribe_token(email, timestamp)
            unsubscribe_url = f"https://YOUR_DOMAIN/unsubscribe?token={token}&email={email}"

            personalized_html = html_content.replace("-unsubscribe_link-", unsubscribe_url)

            if dry_run:
                print(f"  [DRY RUN] Would send to: {email}")
                results["sent"] += 1
                continue

            try:
                message = Mail(
                    from_email=from_email,
                    to_emails=email,
                    subject=subject,
                    html_content=personalized_html,
                )
                sg = SendGridAPIClient(api_key)
                response = sg.send(message)
                if response.status_code in (200, 202):
                    results["sent"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({"email": email, "status": response.status_code})
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"email": email, "error": str(e)})

    log_path = TMP / f"send_log_{timestamp}.json"
    TMP.mkdir(exist_ok=True)
    log_path.write_text(json.dumps(results, indent=2))

    status = "[DRY RUN] " if dry_run else ""
    print(f"{status}Done. Sent: {results['sent']}, Failed: {results['failed']}")
    if results["errors"]:
        print(f"Errors logged to {log_path}")
    print(f"Full log: {log_path}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to rendered newsletter HTML")
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument("--dry-run", action="store_true", help="Print recipients without sending")
    args = parser.parse_args()

    html_path = Path(args.file)
    if not html_path.exists():
        sys.exit(f"HTML file not found: {html_path}")

    send(html_path, args.subject, dry_run=args.dry_run)
