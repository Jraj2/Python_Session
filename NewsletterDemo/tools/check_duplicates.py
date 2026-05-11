"""
Checks a research JSON file against the topics archive to detect duplicate content.
Usage: python tools/check_duplicates.py --research .tmp/research_xxx.json
Exits with code 1 if overlap > threshold (use --force to override).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TMP = ROOT / ".tmp"
ARCHIVE = TMP / "topics_log.json"
OVERLAP_THRESHOLD = 0.6


def load_archive() -> list:
    if not ARCHIVE.exists():
        return []
    return json.loads(ARCHIVE.read_text())


def save_archive(archive: list) -> None:
    TMP.mkdir(exist_ok=True)
    ARCHIVE.write_text(json.dumps(archive, indent=2))


def url_set(sources: list) -> set:
    return {s["url"] for s in sources if s.get("url")}


def check(research_path: Path, force: bool = False) -> float:
    data = json.loads(research_path.read_text())
    topic = data.get("topic", "")
    new_urls = url_set(data.get("sources", []))

    if not new_urls:
        print("No URLs in research file — skipping duplicate check.")
        return 0.0

    archive = load_archive()
    max_overlap = 0.0
    worst_issue = None

    for entry in archive[-10:]:  # check against last 10 newsletters only
        old_urls = set(entry.get("urls", []))
        if not old_urls:
            continue
        overlap = len(new_urls & old_urls) / len(new_urls)
        if overlap > max_overlap:
            max_overlap = overlap
            worst_issue = entry.get("topic", "unknown")

    if max_overlap >= OVERLAP_THRESHOLD:
        msg = (
            f"WARNING: {max_overlap:.0%} URL overlap with previous newsletter "
            f"'{worst_issue}'. Consider a more specific or different angle."
        )
        if force:
            print(msg + " (--force: continuing anyway)")
        else:
            print(msg)
            print("Re-run with --force to proceed despite overlap.")
            sys.exit(1)
    else:
        print(f"Duplicate check passed ({max_overlap:.0%} overlap with recent issues).")

    return max_overlap


def record(research_path: Path) -> None:
    data = json.loads(research_path.read_text())
    archive = load_archive()
    archive.append({
        "topic": data.get("topic", ""),
        "searched_at": data.get("searched_at", ""),
        "urls": list(url_set(data.get("sources", []))),
    })
    save_archive(archive)
    print(f"Recorded in topics archive ({len(archive)} total entries).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", required=True, help="Path to research JSON file")
    parser.add_argument("--force", action="store_true", help="Proceed even if overlap threshold exceeded")
    parser.add_argument("--record", action="store_true", help="Add this research to the archive (run after send)")
    args = parser.parse_args()

    path = Path(args.research)
    if not path.exists():
        sys.exit(f"File not found: {path}")

    if args.record:
        record(path)
    else:
        check(path, force=args.force)
