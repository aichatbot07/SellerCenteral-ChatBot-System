import os
import sys
import warnings
import pytest
from airflow.models import DagBag

# Suppress deprecation and user warnings for cleaner test output.
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def test_dag_loading():
    """
    Integration test for Airflow DAG loading.
    Verifies that:
      - The DAGs in Data_pipeline/dags are loaded without import errors.
      - The DAG with ID 'mlops_csv_pipeline' is present.
      - The DAG contains the expected tasks.
    """
    # Build the absolute path to the DAGs folder.
    dags_folder = os.path.abspath(os.path.join(os.getcwd(), "Data_pipeline", "dags"))
    print("DEBUG: Using DAGs folder:", dags_folder)
    
    # Load DAGs using DagBag.
    dag_bag = DagBag(dag_folder=dags_folder, include_examples=False)
    print("DEBUG: Loaded DAG count:", len(dag_bag.dags))
    
    # Fail the test if there are import errors.
    if dag_bag.import_errors:
        pytest.fail(f"DAG import errors: {dag_bag.import_errors}")
    
    # Ensure that at least one DAG was loaded.
    assert dag_bag.dags, "No DAGs were loaded from the DAGs folder."
    
    # Check that the specific DAG 'mlops_csv_pipeline' is loaded.
    dag_id = "mlops_csv_pipeline"
    assert dag_id in dag_bag.dags, f"DAG '{dag_id}' not found in the loaded DAGs."
    print(f"DEBUG: DAG '{dag_id}' is loaded.")
    
    # Retrieve the DAG directly from the dictionary.
    dag = dag_bag.dags[dag_id]
    
    # Define the expected tasks for the DAG.
    expected_tasks = {"fetch_data", "data_processing", "read_csv", "create_dataset", "upload_bigquery"}
    actual_tasks = {task.task_id for task in dag.tasks}
    missing_tasks = expected_tasks - actual_tasks
    assert not missing_tasks, f"Missing tasks in DAG: {missing_tasks}"
    
    print("DEBUG: Loaded tasks in DAG:", actual_tasks)
