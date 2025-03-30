import os
import pytest
from airflow.models import DagBag

def test_airflow_dag_loading():
    """
    Test that Airflow successfully loads DAGs from the project.
    """
    # Build an absolute path to the dags folder.
    dags_folder = os.path.abspath(os.path.join(os.getcwd(), "Data_pipeline", "dags"))
    dag_bag = DagBag(dag_folder=dags_folder, include_examples=False)
    
    # If there are import errors, print them and fail the test.
    if dag_bag.import_errors:
        pytest.fail(f"DAG import errors: {dag_bag.import_errors}")
    
    # Debug: Print out the IDs of loaded DAGs.
    loaded_dags = list(dag_bag.dags.keys())
    print("Loaded DAGs:", loaded_dags)
    
    # Check that at least one DAG is loaded.
    assert dag_bag.dags, "No DAGs were loaded. Please check your DAG files."