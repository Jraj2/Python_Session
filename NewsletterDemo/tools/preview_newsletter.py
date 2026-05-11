"""
Opens a newsletter HTML file in the system default browser for review.
This is the human approval gate — always run before send_newsletter.py.
Usage: python tools/preview_newsletter.py --file .tmp/newsletter_xxx.html
"""
import argparse
import sys
import webbrowser
from pathlib import Path


def preview(html_path: Path) -> None:
    if not html_path.exists():
        sys.exit(f"File not found: {html_path}")

    # webbrowser.open requires an absolute URI
    uri = html_path.resolve().as_uri()
    print(f"Opening newsletter preview in browser: {uri}")
    webbrowser.open(uri)
    print()
    print("=" * 60)
    print("REVIEW COMPLETE?")
    print("  - If it looks good, tell Claude: 'approve and send'")
    print("  - If changes needed, describe them and Claude will revise")
    print("  - To abort entirely: tell Claude 'cancel, do not send'")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to rendered newsletter HTML")
    args = parser.parse_args()
    preview(Path(args.file))
