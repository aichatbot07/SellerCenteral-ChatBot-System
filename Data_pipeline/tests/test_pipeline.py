# File: Data_pipeline/tests/test_pipeline.py

import subprocess
import pytest

def test_pipeline_execution():
    """
    Integration test for the full ETL pipeline.
    This test runs the pipeline script (mlops_airflow.py) using subprocess
    and asserts that it returns an exit code of 0.
    """
    try:
        result = subprocess.run(
            ["python", "Data_pipeline/dags/mlops_airflow.py"],
            capture_output=True,
            text=True,
            timeout=300  # adjust the timeout as needed
        )
    except subprocess.TimeoutExpired as e:
        pytest.fail(f"Pipeline execution timed out: {e}")

    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    assert result.returncode == 0, f"Pipeline execution failed with exit code {result.returncode}.\nError: {result.stderr}"