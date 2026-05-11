"""
CLI for managing the newsletter subscriber list (subscribers.csv).
Commands:
  add --email foo@bar.com --name "First Name"
  remove --email foo@bar.com
  list
  export --output active_subscribers.csv
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
SUBSCRIBERS_FILE = ROOT / "subscribers.csv"
COLUMNS = ["email", "first_name", "subscribed_date", "unsubscribed_date", "active"]


def load() -> pd.DataFrame:
    if not SUBSCRIBERS_FILE.exists():
        return pd.DataFrame(columns=COLUMNS)
    return pd.read_csv(SUBSCRIBERS_FILE, dtype={"active": bool})


def save(df: pd.DataFrame) -> None:
    df.to_csv(SUBSCRIBERS_FILE, index=False)


def cmd_add(email: str, first_name: str) -> None:
    df = load()
    email = email.strip().lower()
    if email in df["email"].values:
        existing = df[df["email"] == email].iloc[0]
        if existing["active"]:
            print(f"{email} is already an active subscriber.")
        else:
            # Re-subscribe
            df.loc[df["email"] == email, "active"] = True
            df.loc[df["email"] == email, "subscribed_date"] = datetime.utcnow().date().isoformat()
            df.loc[df["email"] == email, "unsubscribed_date"] = None
            save(df)
            print(f"Re-subscribed {email}.")
        return

    new_row = pd.DataFrame([{
        "email": email,
        "first_name": first_name or "",
        "subscribed_date": datetime.utcnow().date().isoformat(),
        "unsubscribed_date": None,
        "active": True,
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    save(df)
    active_count = df[df["active"] == True].shape[0]
    print(f"Added {email}. Total active subscribers: {active_count}")


def cmd_remove(email: str) -> None:
    df = load()
    email = email.strip().lower()
    if email not in df["email"].values:
        print(f"{email} not found in subscriber list.")
        return
    df.loc[df["email"] == email, "active"] = False
    df.loc[df["email"] == email, "unsubscribed_date"] = datetime.utcnow().date().isoformat()
    save(df)
    print(f"Unsubscribed {email} (record preserved for audit trail).")


def cmd_list() -> None:
    df = load()
    active = df[df["active"] == True]
    print(f"Active subscribers: {len(active)}")
    print(f"Total records (including unsubscribed): {len(df)}")
    if not active.empty:
        print()
        print(active[["email", "first_name", "subscribed_date"]].to_string(index=False))


def cmd_export(output_path: str) -> None:
    df = load()
    active = df[df["active"] == True]
    out = Path(output_path)
    active.to_csv(out, index=False)
    print(f"Exported {len(active)} active subscribers to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Newsletter subscriber management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_add = subparsers.add_parser("add")
    p_add.add_argument("--email", required=True)
    p_add.add_argument("--name", default="", dest="first_name")

    p_remove = subparsers.add_parser("remove")
    p_remove.add_argument("--email", required=True)

    subparsers.add_parser("list")

    p_export = subparsers.add_parser("export")
    p_export.add_argument("--output", default="active_subscribers.csv")

    args = parser.parse_args()

    if args.command == "add":
        cmd_add(args.email, args.first_name)
    elif args.command == "remove":
        cmd_remove(args.email)
    elif args.command == "list":
        cmd_list()
    elif args.command == "export":
        cmd_export(args.output)
