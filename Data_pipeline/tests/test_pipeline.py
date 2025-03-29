import os
import sys
import importlib
import pendulum

# --- Monkey-patch pendulum for compatibility with Airflow ---
# In Pendulum v3, pendulum.tz is no longer callable.
if not callable(getattr(pendulum.tz, "timezone", None)):
    pendulum.tz = pendulum

# --- Ensure the repository root is in PYTHONPATH ---
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, repo_root)

# Optionally, you can verify your PYTHONPATH includes the repo_root:
#print("PYTHONPATH:", sys.path)

import pytest
from airflow.models import DagBag

def test_dag_loading():
    """
    Integration test for the Airflow DAG.
    This test loads the DAG from Data_pipeline/dags and verifies that:
      - No import errors occur.
      - The 'mlops_csv_pipeline' DAG is present.
      - It contains the expected tasks.
    """
    # Determine the path to your dags folder.
    dags_folder = os.path.join(os.getcwd(), "Data_pipeline", "dags")
    dagbag = DagBag(dag_folder=dags_folder, include_examples=False)
    
    # Fail the test if there are any import errors.
    if dagbag.import_errors:
        pytest.fail(f"DAG import errors: {dagbag.import_errors}")
    
    # Verify that at least one DAG is loaded.
    assert dagbag.dags, "No DAGs were loaded from the dags folder."
    
    # Check that the specific DAG 'mlops_csv_pipeline' is loaded.
    dag_id = "mlops_csv_pipeline"
    assert dag_id in dagbag.dags, f"DAG '{dag_id}' not found in the loaded DAGs."
    
    # Optionally, verify that the DAG has the expected tasks.
    dag = dagbag.get_dag(dag_id)
    expected_tasks = {"fetch_data", "data_processing", "read_csv", "create_dataset", "upload_bigquery"}
    actual_tasks = {task.task_id for task in dag.tasks}
    missing_tasks = expected_tasks - actual_tasks
    assert not missing_tasks, f"Missing tasks in DAG: {missing_tasks}"
    
    print("Loaded tasks:", actual_tasks)