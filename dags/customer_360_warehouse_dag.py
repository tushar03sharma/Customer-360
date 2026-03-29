from __future__ import annotations

from orchestration.dag_runner import build_local_dag
from orchestration.tasks import (
    build_core_models,
    build_marts,
    build_staging_models,
    export_mart_exports,
    extract_source_data,
    initialize_warehouse,
    load_raw_sources,
    run_data_quality_checks,
    summarize_pipeline_run,
)

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
except ImportError:  # pragma: no cover
    DAG = None
    PythonOperator = None


dag_spec = build_local_dag()


def _build_airflow_dag() -> DAG | None:
    if DAG is None or PythonOperator is None:
        return None

    with DAG(
        dag_id=dag_spec.dag_id,
        schedule=dag_spec.schedule,
        default_args=dag_spec.default_args,
        catchup=False,
        tags=["data-engineering", "customer-360", "duckdb"],
    ) as dag:
        extract = PythonOperator(task_id="extract_source_data", python_callable=extract_source_data)
        initialize = PythonOperator(task_id="initialize_warehouse", python_callable=initialize_warehouse)
        load = PythonOperator(task_id="load_raw_sources", python_callable=load_raw_sources)
        staging = PythonOperator(task_id="build_staging_models", python_callable=build_staging_models)
        core = PythonOperator(task_id="build_core_models", python_callable=build_core_models)
        marts = PythonOperator(task_id="build_marts", python_callable=build_marts)
        quality = PythonOperator(task_id="run_data_quality_checks", python_callable=run_data_quality_checks)
        exports = PythonOperator(task_id="export_mart_exports", python_callable=export_mart_exports)
        summary = PythonOperator(task_id="summarize_pipeline_run", python_callable=summarize_pipeline_run)

        extract >> initialize >> load >> staging >> core >> marts >> quality >> exports >> summary

    return dag


dag = _build_airflow_dag()

