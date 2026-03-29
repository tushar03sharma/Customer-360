from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from . import tasks


TaskCallable = Callable[..., dict[str, object]]


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    python_callable: TaskCallable
    upstream_task_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DAGSpec:
    dag_id: str
    schedule: str
    default_args: dict[str, object]
    tasks: tuple[TaskSpec, ...]


def build_local_dag() -> DAGSpec:
    return DAGSpec(
        dag_id="customer_360_analytics_warehouse",
        schedule="@daily",
        default_args={
            "owner": "data-eng",
            "depends_on_past": False,
            "retries": 1,
        },
        tasks=(
            TaskSpec("extract_source_data", tasks.extract_source_data),
            TaskSpec("initialize_warehouse", tasks.initialize_warehouse, ("extract_source_data",)),
            TaskSpec("load_raw_sources", tasks.load_raw_sources, ("initialize_warehouse",)),
            TaskSpec("build_staging_models", tasks.build_staging_models, ("load_raw_sources",)),
            TaskSpec("build_core_models", tasks.build_core_models, ("build_staging_models",)),
            TaskSpec("build_marts", tasks.build_marts, ("build_core_models",)),
            TaskSpec("run_data_quality_checks", tasks.run_data_quality_checks, ("build_marts",)),
            TaskSpec("export_mart_exports", tasks.export_mart_exports, ("run_data_quality_checks",)),
            TaskSpec("summarize_pipeline_run", tasks.summarize_pipeline_run, ("export_mart_exports",)),
        ),
    )


class DAGRunner:
    def __init__(self, dag: DAGSpec | None = None) -> None:
        self.dag = dag or build_local_dag()

    def run(self, *, regenerate_data: bool = False, db_path: str | None = None) -> dict[str, object]:
        task_results: dict[str, dict[str, object]] = {}

        for task in self.dag.tasks:
            missing_upstream = [task_id for task_id in task.upstream_task_ids if task_id not in task_results]
            if missing_upstream:
                raise ValueError(f"Task {task.task_id} is missing upstream tasks: {missing_upstream}")
            kwargs = {"db_path": db_path}
            if task.task_id == "extract_source_data":
                kwargs["regenerate_data"] = regenerate_data
            task_results[task.task_id] = task.python_callable(**kwargs)

        return {
            "dag_id": self.dag.dag_id,
            "schedule": self.dag.schedule,
            "tasks_run": [task.task_id for task in self.dag.tasks],
            "task_results": task_results,
            "final_summary": task_results["summarize_pipeline_run"],
        }
