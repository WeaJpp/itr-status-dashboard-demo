from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from itr_pipeline.engine import Pipeline  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the privacy-safe ITR demo pipeline.")
    parser.add_argument(
        "--config",
        default="config.example.json",
        help="Config path relative to the repository root.",
    )
    args = parser.parse_args()
    pipeline = Pipeline(ROOT, ROOT / args.config)
    result = pipeline.run()
    print(
        json.dumps(
            {
                "status": result["summary"]["status"],
                "rows": result["summary"]["source_rows"],
                "scanned": result["summary"]["scanned"],
                "changes": result["summary"]["changes"],
                "unresolved": result["summary"]["unresolved"],
                "report": "public/data/dashboard.json",
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
