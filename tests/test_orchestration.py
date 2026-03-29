from __future__ import annotations

import unittest

from orchestration.dag_runner import DAGRunner, build_local_dag


class OrchestrationTest(unittest.TestCase):
    def test_dag_dependency_chain(self) -> None:
        dag = build_local_dag()
        expected_order = [
            "extract_source_data",
            "initialize_warehouse",
            "load_raw_sources",
            "build_staging_models",
            "build_core_models",
            "build_marts",
            "run_data_quality_checks",
            "export_mart_exports",
            "summarize_pipeline_run",
        ]
        self.assertEqual([task.task_id for task in dag.tasks], expected_order)
        self.assertEqual(dag.tasks[-1].upstream_task_ids, ("export_mart_exports",))

    def test_local_runner_executes_full_dag(self) -> None:
        summary = DAGRunner().run(regenerate_data=True)
        self.assertEqual(summary["tasks_run"][0], "extract_source_data")
        self.assertEqual(summary["tasks_run"][-1], "summarize_pipeline_run")
        self.assertTrue(all(item["passed"] for item in summary["final_summary"]["quality_results"]))


if __name__ == "__main__":
    unittest.main()

