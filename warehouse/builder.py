from __future__ import annotations

from pathlib import Path

import duckdb

from .config import DB_PATH, EXPORT_DIR, MODEL_FOLDERS, MODELS_DIR, RAW_FILES
from .data_generator import generate_source_data

MODEL_ORDER = {
    "staging": [
        "stg_customers.sql",
        "stg_orders.sql",
        "stg_payments.sql",
        "stg_support_tickets.sql",
    ],
    "core": [
        "dim_customers.sql",
        "fct_orders.sql",
        "fct_support_tickets.sql",
        "customer_order_summary.sql",
        "customer_support_summary.sql",
    ],
    "marts": [
        "customer_360.sql",
        "customer_clv.sql",
        "customer_churn_risk.sql",
        "repeat_purchase_behavior.sql",
    ],
}

MART_TABLES = ["customer_360", "customer_clv", "customer_churn_risk", "repeat_purchase_behavior"]


class WarehouseBuilder:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path else DB_PATH

    def ensure_source_data(self, regenerate_data: bool = False) -> dict[str, int]:
        if regenerate_data or not all(path.exists() for path in RAW_FILES.values()):
            return generate_source_data()
        return {name: self._count_csv_rows(path) for name, path in RAW_FILES.items()}

    def build(self, regenerate_data: bool = False) -> dict[str, object]:
        data_counts = self.ensure_source_data(regenerate_data=regenerate_data)

        EXPORT_DIR.mkdir(parents=True, exist_ok=True)

        with duckdb.connect(str(self.db_path)) as conn:
            self.prepare_schemas(conn)
            self.load_raw_tables(conn)
            self.run_all_models(conn)
            quality_results = self.run_quality_checks(conn)
            self.export_marts(conn)
            mart_counts = self.collect_mart_counts(conn)

        return {
            "database": str(self.db_path),
            "raw_counts": data_counts,
            "mart_counts": mart_counts,
            "quality_results": quality_results,
        }

    def prepare_schemas(self, conn: duckdb.DuckDBPyConnection) -> None:
        for schema in ["raw", "staging", "core", "marts", "qa"]:
            conn.execute(f"create schema if not exists {schema}")

    def load_raw_tables(self, conn: duckdb.DuckDBPyConnection) -> None:
        for table_name, path in RAW_FILES.items():
            normalized_path = path.as_posix()
            conn.execute(
                f"""
                create or replace table raw.{table_name} as
                select *
                from read_csv_auto('{normalized_path}', header=true)
                """
            )

    def run_model_folder(self, conn: duckdb.DuckDBPyConnection, folder: str) -> list[str]:
        model_files = MODEL_ORDER.get(folder)
        sql_paths = [(MODELS_DIR / folder / file_name) for file_name in model_files] if model_files else sorted((MODELS_DIR / folder).glob("*.sql"))
        for sql_file in sql_paths:
            conn.execute(sql_file.read_text(encoding="utf-8"))
        return [sql_path.stem for sql_path in sql_paths]

    def run_all_models(self, conn: duckdb.DuckDBPyConnection) -> dict[str, list[str]]:
        return {folder: self.run_model_folder(conn, folder) for folder in MODEL_FOLDERS}

    def run_quality_checks(self, conn: duckdb.DuckDBPyConnection) -> list[dict[str, object]]:
        checks = [
            (
                "unique_customers",
                """
                select count(*) = count(distinct customer_id)
                from raw.customers
                """,
            ),
            (
                "orders_have_customers",
                """
                select count(*) = 0
                from raw.orders o
                left join raw.customers c on o.customer_id = c.customer_id
                where c.customer_id is null
                """,
            ),
            (
                "payments_have_orders",
                """
                select count(*) = 0
                from raw.payments p
                left join raw.orders o on p.order_id = o.order_id
                where o.order_id is null
                """,
            ),
            (
                "customer_360_row_count",
                """
                select (select count(*) from marts.customer_360) = (select count(*) from raw.customers)
                """,
            ),
            (
                "non_negative_revenue",
                """
                select count(*) = 0
                from marts.customer_360
                where lifetime_revenue < 0
                """,
            ),
        ]

        results: list[dict[str, object]] = []
        for check_name, sql in checks:
            passed = conn.execute(sql).fetchone()[0]
            results.append({"check_name": check_name, "passed": bool(passed)})

        conn.execute("drop table if exists qa.data_quality_results")
        conn.execute("create table qa.data_quality_results (check_name varchar, passed boolean)")
        conn.executemany(
            "insert into qa.data_quality_results values (?, ?)",
            [(result["check_name"], result["passed"]) for result in results],
        )
        return results

    def export_marts(self, conn: duckdb.DuckDBPyConnection) -> list[str]:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        exported_files = []
        for mart_name in MART_TABLES:
            export_path = (EXPORT_DIR / f"{mart_name}.csv").as_posix()
            conn.execute(
                f"""
                copy marts.{mart_name}
                to '{export_path}'
                (header, delimiter ',')
                """
            )
            exported_files.append(export_path)
        return exported_files

    def collect_mart_counts(self, conn: duckdb.DuckDBPyConnection) -> dict[str, int]:
        counts = {}
        for mart_name in MART_TABLES:
            counts[mart_name] = conn.execute(f"select count(*) from marts.{mart_name}").fetchone()[0]
        return counts

    @staticmethod
    def _count_csv_rows(path: Path) -> int:
        with path.open("r", encoding="utf-8") as handle:
            return max(sum(1 for _ in handle) - 1, 0)
