import os
import sys
import pytest
from airflow.models import DagBag
from unittest import mock

# Mock all external modules used in mlops_airflow.py
sys.modules["read_csv_from_gcp_code"] = mock.Mock()
sys.modules["create_bigquery_dataset_code"] = mock.Mock()
sys.modules["upload_to_bigquery_code"] = mock.Mock()
sys.modules["fetch_data"] = mock.Mock()
sys.modules["anamoly_handler"] = mock.Mock()
sys.modules["product_features"] = mock.Mock()
sys.modules["best_bundled_together_3"] = mock.Mock()
sys.modules["product_performance_predictor_2"] = mock.Mock()
sys.modules["optimal_price_range_4"] = mock.Mock()
sys.modules["verified_nonverified_6"] = mock.Mock()
DAG_ID = "mlops_csv_pipeline"

@pytest.fixture(scope="module")
def dagbag():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dags_folder = os.path.join(repo_root, "Data_pipeline", "dags")
    return DagBag(dag_folder=dags_folder, include_examples=False)

def test_dag_imports_without_errors(dagbag):
    assert not dagbag.import_errors, f"DAG import errors: {dagbag.import_errors}"

def test_dag_is_loaded(dagbag):
    assert DAG_ID in dagbag.dags, f"DAG '{DAG_ID}' not found in dagbag"

@pytest.fixture(scope="module")
def dag(dagbag):
    return dagbag.get_dag(DAG_ID)

def test_dag_has_expected_tasks(dag):
    expected_tasks = {
        "fetch_data",
        "read_csv",
        "removing_anamolies",
        "extracting_features",
        "product_performance_predictor",
        "best_bundled_together",
        "optimal_price_range",
        "verified_vs_nonverified",
        "create_dataset",
        "upload_bigquery"
    }
    actual_tasks = {task.task_id for task in dag.tasks}
    assert expected_tasks == actual_tasks

def test_dag_task_dependencies(dag):
    expected_dependencies = [
        ("fetch_data", "read_csv"),
        ("read_csv", "removing_anamolies"),
        ("removing_anamolies", "extracting_features"),
        ("extracting_features", "product_performance_predictor"),
        ("product_performance_predictor", "best_bundled_together"),
        ("best_bundled_together", "optimal_price_range"),
        ("optimal_price_range", "verified_vs_nonverified"),
        ("verified_vs_nonverified", "create_dataset"),
        ("create_dataset", "upload_bigquery")
    ]
    for upstream, downstream in expected_dependencies:
        downstreams = {t.task_id for t in dag.task_dict[upstream].get_direct_relatives(upstream=False)}
        assert downstream in downstreams, f"{downstream} not downstream of {upstream}"
def test_dag_default_args(dag):
    assert dag.default_args["owner"] == "airflow"
    assert dag.default_args["retries"] == 3

def test_dag_schedule_and_catchup(dag):
    assert dag.schedule_interval == "@daily"
    assert dag.catchup is False

def test_all_tasks_are_python_operators(dag):
    from airflow.operators.python_operator import PythonOperator
    for task in dag.tasks:
        assert isinstance(task, PythonOperator)