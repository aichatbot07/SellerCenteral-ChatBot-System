import os
import pytest
import warnings
from airflow.models import DagBag

# Suppress deprecation and user warnings for cleaner output.
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def test_airflow_dag_loading():
    """
    Test that Airflow successfully loads DAGs from the project.
    Verifies that no import errors occur and that at least one DAG is loaded.
    """
    # Construct an absolute path to the DAGs folder.
    dags_folder = os.path.abspath(os.path.join(os.getcwd(), "Data_pipeline", "dags"))
    print("DAGs folder:", dags_folder)
    
    # Load the DAGs using DagBag.
    dag_bag = DagBag(dag_folder=dags_folder, include_examples=False)
    
    # Fail the test if there are any import errors.
    if dag_bag.import_errors:
        pytest.fail(f"DAG import errors: {dag_bag.import_errors}")
    
    # Debug: Print loaded DAG IDs.
    loaded_dags = list(dag_bag.dags.keys())
    print("Loaded DAGs:", loaded_dags)
    
    # Ensure that at least one DAG was loaded.
    assert dag_bag.dags, "No DAGs were loaded. Please check your DAG files."