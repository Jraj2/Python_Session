"""
Use Claude to suggest competitors based on the AIS business profile.
Interactive: prints suggestions, asks for confirmation, writes competitors.json.
Usage: python discover_competitors.py --profile-json data/business_profile.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"


def load_profile(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ask_claude(profile: dict) -> list[dict]:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")

    profile_text = json.dumps(profile, indent=2)

    response = client.messages.create(
        model=model,
        max_tokens=2000,
        system=(
            "You are a competitive intelligence analyst specializing in SaaS markets. "
            "Return only valid JSON — no preamble, no explanation."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Based on this business profile, identify 8-12 direct competitors:\n\n"
                    f"{profile_text}\n\n"
                    "Return a JSON array. Each object must have:\n"
                    "- name: company name\n"
                    "- website_url: homepage URL\n"
                    "- g2_slug: best-guess G2 product slug (lowercase-hyphenated)\n"
                    "- capterra_slug: best-guess Capterra slug\n"
                    "- trustpilot_slug: company domain for Trustpilot (e.g. 'company.com')\n"
                    "- careers_url: careers/jobs page URL\n"
                    "- rationale: one sentence why this is a direct competitor\n\n"
                    "Return only the JSON array, nothing else."
                ),
            }
        ],
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if Claude added them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def interactive_confirm(competitors: list[dict]) -> list[dict]:
    print("\n" + "=" * 60)
    print("SUGGESTED COMPETITORS")
    print("=" * 60)
    for i, c in enumerate(competitors, 1):
        print(f"\n{i}. {c['name']}")
        print(f"   Website : {c['website_url']}")
        print(f"   Careers : {c['careers_url']}")
        print(f"   Why     : {c['rationale']}")

    print("\n" + "-" * 60)
    print("Options:")
    print("  [Enter]  Accept all")
    print("  remove 3,5  Remove competitors by number (comma-separated)")
    print("  add         Add a competitor manually")
    print("-" * 60)

    confirmed = list(competitors)

    while True:
        choice = input("\n> ").strip().lower()

        if choice == "" or choice == "accept":
            break

        if choice.startswith("remove"):
            nums = [s.strip() for s in choice.replace("remove", "").split(",")]
            to_remove = set()
            for n in nums:
                try:
                    to_remove.add(int(n) - 1)
                except ValueError:
                    pass
            confirmed = [c for i, c in enumerate(confirmed) if i not in to_remove]
            print(f"Removed {len(to_remove)} competitor(s). {len(confirmed)} remaining.")

        elif choice == "add":
            name = input("Company name: ").strip()
            url = input("Website URL: ").strip()
            careers = input("Careers URL: ").strip()
            confirmed.append({
                "name": name,
                "website_url": url,
                "g2_slug": name.lower().replace(" ", "-"),
                "capterra_slug": name.lower().replace(" ", "-"),
                "trustpilot_slug": url.replace("https://", "").replace("http://", "").rstrip("/"),
                "careers_url": careers,
                "rationale": "Manually added",
            })
            print(f"Added {name}.")

        else:
            print("Unrecognized input. Press Enter to accept, or type 'remove 1,2' / 'add'.")

    return confirmed


def main():
    parser = argparse.ArgumentParser(description="Discover competitors using Claude")
    parser.add_argument(
        "--profile-json",
        default=str(DATA_DIR / "business_profile.json"),
        help="Path to business_profile.json",
    )
    args = parser.parse_args()

    if not os.path.exists(args.profile_json):
        print(f"ERROR: Profile not found at {args.profile_json}")
        print("Create data/business_profile.json first (see workflows/setup_business_profile.md)")
        sys.exit(1)

    profile = load_profile(args.profile_json)
    print(f"Loaded profile for: {profile.get('product_name', 'unknown')}")
    print("Asking Claude to identify competitors...")

    competitors = ask_claude(profile)
    confirmed = interactive_confirm(competitors)

    out_path = DATA_DIR / "competitors.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(confirmed, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Saved {len(confirmed)} competitors to {out_path}")
    print("\nNext step: verify careers_url and review site slugs for each competitor,")
    print("then run a single-competitor test per workflows/research_single_competitor.md")


if __name__ == "__main__":
    main()
