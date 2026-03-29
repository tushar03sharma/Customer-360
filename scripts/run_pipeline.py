from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from warehouse.builder import WarehouseBuilder


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Customer 360 analytics warehouse.")
    parser.add_argument("--regenerate-data", action="store_true", help="Regenerate synthetic source CSVs before loading.")
    args = parser.parse_args()

    builder = WarehouseBuilder()
    summary = builder.build(regenerate_data=args.regenerate_data)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
