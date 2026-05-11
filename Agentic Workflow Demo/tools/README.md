# Tools

Each script in this directory is a self-contained, deterministic execution unit.

## Conventions
- Scripts accept arguments via `argparse` or read from `.env`
- All credentials come from `.env` — never hardcoded
- Output goes to stdout or `.tmp/` for intermediate files
- Final deliverables go to cloud services (Google Sheets, etc.)

## Adding a New Tool
1. Create `tools/your_tool_name.py`
2. Add a docstring at the top explaining inputs, outputs, and usage
3. Reference it in the relevant workflow markdown
