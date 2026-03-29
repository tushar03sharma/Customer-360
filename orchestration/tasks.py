from __future__ import annotations

from pathlib import Path

import duckdb

from warehouse.builder import WarehouseBuilder


def _builder(db_path: str | None = None) -> WarehouseBuilder:
    return WarehouseBuilder(Path(db_path) if db_path else None)


def extract_source_data(*, regenerate_data: bool = False, db_path: str | None = None) -> dict[str, object]:
    counts = _builder(db_path).ensure_source_data(regenerate_data=regenerate_data)
    return {"task": "extract_source_data", "raw_counts": counts}


def initialize_warehouse(*, db_path: str | None = None) -> dict[str, object]:
    builder = _builder(db_path)
    with duckdb.connect(str(builder.db_path)) as conn:
        builder.prepare_schemas(conn)
    return {"task": "initialize_warehouse", "database": str(builder.db_path)}


def load_raw_sources(*, db_path: str | None = None) -> dict[str, object]:
    builder = _builder(db_path)
    with duckdb.connect(str(builder.db_path)) as conn:
        builder.prepare_schemas(conn)
        builder.load_raw_tables(conn)
    return {"task": "load_raw_sources", "tables_loaded": 4}


def build_staging_models(*, db_path: str | None = None) -> dict[str, object]:
    builder = _builder(db_path)
    with duckdb.connect(str(builder.db_path)) as conn:
        models = builder.run_model_folder(conn, "staging")
    return {"task": "build_staging_models", "models_built": models}


def build_core_models(*, db_path: str | None = None) -> dict[str, object]:
    builder = _builder(db_path)
    with duckdb.connect(str(builder.db_path)) as conn:
        models = builder.run_model_folder(conn, "core")
    return {"task": "build_core_models", "models_built": models}


def build_marts(*, db_path: str | None = None) -> dict[str, object]:
    builder = _builder(db_path)
    with duckdb.connect(str(builder.db_path)) as conn:
        models = builder.run_model_folder(conn, "marts")
        mart_counts = builder.collect_mart_counts(conn)
    return {"task": "build_marts", "models_built": models, "mart_counts": mart_counts}


def run_data_quality_checks(*, db_path: str | None = None) -> dict[str, object]:
    builder = _builder(db_path)
    with duckdb.connect(str(builder.db_path)) as conn:
        quality_results = builder.run_quality_checks(conn)
    return {"task": "run_data_quality_checks", "quality_results": quality_results}


def export_mart_exports(*, db_path: str | None = None) -> dict[str, object]:
    builder = _builder(db_path)
    with duckdb.connect(str(builder.db_path)) as conn:
        exported_files = builder.export_marts(conn)
    return {"task": "export_mart_exports", "exported_files": exported_files}


def summarize_pipeline_run(*, db_path: str | None = None) -> dict[str, object]:
    builder = _builder(db_path)
    with duckdb.connect(str(builder.db_path)) as conn:
        mart_counts = builder.collect_mart_counts(conn)
        quality_results = conn.execute(
            """
            select check_name, passed
            from qa.data_quality_results
            order by check_name
            """
        ).fetchall()
    return {
        "task": "summarize_pipeline_run",
        "database": str(builder.db_path),
        "mart_counts": mart_counts,
        "quality_results": [
            {"check_name": check_name, "passed": passed}
            for check_name, passed in quality_results
        ],
    }

