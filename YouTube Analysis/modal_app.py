"""
YouTube Analysis — Modal deployment (Modal v1)
Scheduled: every Monday 08:00 IST (02:30 UTC)
Output: Modal Volume 'yt-analysis-outputs' -> youtube_analysis_YYYY-MM-DD.pdf

Deploy:   python -m modal deploy modal_app.py
Test run: python -m modal run modal_app.py
Download: python -m modal volume get yt-analysis-outputs youtube_analysis_YYYY-MM-DD.pdf
"""
import datetime
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import modal

app = modal.App("yt-analysis")

# Bake project source into the image (copy=True ensures it's available for scheduled runs)
# .env and generated artifacts are excluded so secrets never leave the local machine
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "google-api-python-client",
        "anthropic",
        "reportlab",
        "matplotlib",
        "Pillow",
        "python-dotenv",
        "requests",
    )
    .add_local_dir(
        Path(__file__).parent,
        remote_path="/yt-src",
        copy=True,
        ignore=lambda p: any(
            seg in str(p) for seg in {".tmp", ".env", "__pycache__", ".git", "pyenv"}
        ),
    )
)

output_vol = modal.Volume.from_name("yt-analysis-outputs", create_if_missing=True)


@app.function(
    image=image,
    volumes={"/yt-outputs": output_vol},
    secrets=[modal.Secret.from_name("yt-analysis-secrets")],
    schedule=modal.Cron("30 2 * * 1"),  # Mon 02:30 UTC = Mon 08:00 IST
    timeout=1200,
)
def run_analysis():
    with tempfile.TemporaryDirectory() as tmp_root:
        # Copy source to a writable staging area (image layers are read-only)
        work = Path(tmp_root) / "yt-work"
        shutil.copytree("/yt-src", work)

        # Pre-create output dirs — not all scripts do this themselves
        (work / ".tmp" / "charts").mkdir(parents=True, exist_ok=True)

        # MPLBACKEND=Agg prevents matplotlib from opening a GUI window in the container
        env = {**os.environ, "MPLBACKEND": "Agg"}

        steps = [
            "fetch_channels.py",
            "fetch_videos.py",
            "analyze_trends.py",
            "generate_charts.py",
            "generate_pdf.py",
        ]

        for script in steps:
            print(f"\n--- {script} ---")
            result = subprocess.run(
                ["python", str(work / "tools" / script)],
                cwd=work,
                env=env,
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            if result.returncode != 0:
                print(result.stderr)
                raise RuntimeError(f"{script} failed")

        # Persist PDF to Modal Volume so it survives after the container exits
        date_str = datetime.date.today().isoformat()
        pdf_name = f"youtube_analysis_{date_str}.pdf"
        pdf_src = work / ".tmp" / pdf_name

        if not pdf_src.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_src}")

        shutil.copy(pdf_src, f"/yt-outputs/{pdf_name}")
        output_vol.commit()
        print(f"\n[OK] Saved -> /yt-outputs/{pdf_name}")
        print(f"     Download: python -m modal volume get yt-analysis-outputs {pdf_name}")


@app.local_entrypoint()
def main():
    """Manual trigger: python -m modal run modal_app.py"""
    run_analysis.remote()
