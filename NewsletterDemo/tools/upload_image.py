"""
Uploads a PNG to imgBB and returns the permanent hosted URL.
Usage: python tools/upload_image.py --file .tmp/charts/my_chart.png
Prints the hosted URL to stdout.
"""
import argparse
import base64
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()


def upload(image_path: Path) -> str:
    api_key = os.getenv("IMGBB_API_KEY")
    if not api_key:
        sys.exit("IMGBB_API_KEY not set in .env")

    if not image_path.exists():
        sys.exit(f"File not found: {image_path}")

    image_data = base64.b64encode(image_path.read_bytes()).decode("utf-8")

    print(f"Uploading {image_path.name} to imgBB...")
    resp = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": api_key, "image": image_data, "name": image_path.stem},
        timeout=30,
    )
    resp.raise_for_status()
    result = resp.json()

    if not result.get("success"):
        sys.exit(f"imgBB upload failed: {result}")

    url = result["data"]["url"]
    print(f"Uploaded → {url}")
    return url


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to PNG file to upload")
    args = parser.parse_args()

    hosted_url = upload(Path(args.file))
    print(hosted_url)
