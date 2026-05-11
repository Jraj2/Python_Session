"""
Searches Tavily for a given topic and saves structured results to .tmp/.
Usage: python tools/research_topic.py --topic "AI trends" --days 7 --results 8
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

ROOT = Path(__file__).parent.parent
TMP = ROOT / ".tmp"
TMP.mkdir(exist_ok=True)


def research(topic: str, days: int, num_results: int) -> Path:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        sys.exit("TAVILY_API_KEY not set in .env")

    client = TavilyClient(api_key=api_key)
    print(f"Searching Tavily: '{topic}' (last {days} days, {num_results} results)...")

    response = client.search(
        query=topic,
        search_depth="advanced",
        max_results=num_results,
        days=days,
        include_answer=True,
    )

    results = {
        "topic": topic,
        "searched_at": datetime.utcnow().isoformat(),
        "days_back": days,
        "answer_summary": response.get("answer", ""),
        "sources": [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
                "score": r.get("score", 0),
            }
            for r in response.get("results", [])
        ],
    }

    if len(results["sources"]) < 3:
        print(f"WARNING: Only {len(results['sources'])} sources returned. Consider broadening the query.")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = TMP / f"research_{timestamp}.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"Saved {len(results['sources'])} sources -> {out_path}")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--results", type=int, default=8)
    args = parser.parse_args()

    path = research(args.topic, args.days, args.results)
    print(path)
