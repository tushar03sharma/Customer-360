from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from orchestration.dag_runner import DAGRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Customer 360 Airflow-style orchestration pipeline.")
    parser.add_argument("--regenerate-data", action="store_true", help="Regenerate synthetic source CSVs before the DAG runs.")
    args = parser.parse_args()

    summary = DAGRunner().run(regenerate_data=args.regenerate_data)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

