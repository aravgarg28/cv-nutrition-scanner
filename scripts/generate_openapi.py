"""Dump the FastAPI OpenAPI schema to a stable JSON file.

The output is committed and drift-checked in CI (T-005): regenerating must produce a
byte-identical file, so the TypeScript client can never silently diverge from the API.
Determinism: sorted keys + fixed indent + trailing newline.

Usage:
    uv run python scripts/generate_openapi.py
"""

from __future__ import annotations

import json
from pathlib import Path

from snap_api.main import app

OUTPUT = Path(__file__).resolve().parent.parent / "packages" / "api-client" / "openapi.json"


def main() -> None:
    schema = app.openapi()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
