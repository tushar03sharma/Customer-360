# Customer 360 Analytics Warehouse

Customer 360 Analytics Warehouse is a resume-ready data engineering project that ingests customer, order, payment, and support data into DuckDB, transforms it through staged SQL models, and publishes analytics marts for lifecycle value, churn risk, and repeat purchase behavior.

## What this project shows

- End-to-end ETL from raw CSV sources into a warehouse
- SQL-based staging, core modeling, and mart creation
- Airflow-style orchestration with DAG-shaped task boundaries
- Customer-level analytics for CLV, churn, and retention patterns
- Data quality checks and exportable analytics outputs

## Architecture

1. Synthetic source data is generated for `customers`, `orders`, `payments`, and `support_tickets`.
2. Python loads those sources into DuckDB under the `raw` schema.
3. SQL models transform data through `staging`, `core`, and `marts`.
4. An Airflow-style DAG orchestrates extract, warehouse init, raw load, modeling, quality checks, and export tasks.
5. Quality checks validate joins, uniqueness, and revenue sanity.
6. Final marts are exported to `data/exports/` as analyst-friendly CSVs.

## Project structure

```text
.
├── data/
│   ├── raw/
│   └── exports/
├── dags/
├── models/
│   ├── staging/
│   ├── core/
│   └── marts/
├── orchestration/
├── scripts/
├── tests/
└── warehouse/
```

## Key marts

- `marts.customer_360`: unified customer profile with order, revenue, support, and recency metrics
- `marts.customer_clv`: historical and projected customer lifetime value with ranking
- `marts.customer_churn_risk`: risk scoring with recommended action bands
- `marts.repeat_purchase_behavior`: customer repeat segment and cohort repeat rate

## Run locally

```bash
python3 scripts/run_pipeline.py --regenerate-data
python3 scripts/run_orchestrated_pipeline.py --regenerate-data
python3 -m unittest tests/test_pipeline.py
python3 -m unittest tests/test_orchestration.py
```

## Airflow-style orchestration

- `dags/customer_360_warehouse_dag.py` defines the DAG layout and task dependencies in an Airflow-friendly format.
- `orchestration/tasks.py` holds task-level Python callables for extract, load, transform, quality, and export stages.
- `orchestration/dag_runner.py` provides a local DAG executor so the pipeline can be demonstrated without installing Airflow.

Task flow:

1. `extract_source_data`
2. `initialize_warehouse`
3. `load_raw_sources`
4. `build_staging_models`
5. `build_core_models`
6. `build_marts`
7. `run_data_quality_checks`
8. `export_mart_exports`
9. `summarize_pipeline_run`

## Resume bullets you can use

- Built a Customer 360 analytics warehouse in DuckDB with Python ETL pipelines integrating 250+ customers, 600+ orders, payments, and support events into staged and mart-layer models.
- Designed an Airflow-style DAG with task-based orchestration for extraction, warehouse loading, transformation, validation, and export, making the pipeline production-like and scheduler-ready.
- Modeled business-facing marts for CLV, churn risk, and repeat purchase behavior using SQL transformations, cohort logic, and customer-level feature engineering.
- Added automated data quality checks for uniqueness, referential integrity, and revenue validation, then exported clean marts for downstream analytics use.
