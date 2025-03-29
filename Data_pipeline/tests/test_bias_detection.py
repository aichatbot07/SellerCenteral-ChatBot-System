import os
import sys
import warnings
import pytest
import pandas as pd

# Suppress runtime warnings for empty slices, etc.
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Add the repository root to PYTHONPATH so that Data_pipeline is discoverable.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, repo_root)

# Import and monkey-patch the config module before any dependent modules are imported.
import Data_pipeline.dags.config as config
if not hasattr(config, "GCP_CREDENTIALS_PATH"):
    config.GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH", "/opt/airflow/dags/gcp-credentials.json")
if not hasattr(config, "BUCKET_NAME"):
    config.BUCKET_NAME = os.getenv("BUCKET_NAME", "ai_chatbot_seller_central")
if not hasattr(config, "FILE_NAME"):
    config.FILE_NAME = os.getenv("FILE_NAME", "new_data_sentiment.csv")

# Reload config to ensure changes are visible.
import importlib
importlib.reload(config)

# Remove fetch_data from sys.modules (if it was imported) to force re-import.
if "Data_pipeline.dags.fetch_data" in sys.modules:
    del sys.modules["Data_pipeline.dags.fetch_data"]

# Now import the module under test.
from Data_pipeline.dags.bias_detection import (
    check_bias,
    plot_bias,
    handle_bias,
    output_folder,
)

def test_check_bias():
    """
    Test that check_bias returns correct accuracy for subgroups.
    We simulate a small test scenario with a 'verified_purchase' column.
    """
    # Create a sample DataFrame with a 'verified_purchase' column.
    df = pd.DataFrame({
        "verified_purchase": [True, True, False, False],
    })
    # Create y_test and y_pred Series with matching indices.
    # For subgroup True (first two rows): predictions match, so accuracy 1.0.
    # For subgroup False (last two rows): predictions are incorrect, so accuracy 0.0.
    y_test = pd.Series([1, 0, 1, 1], index=df.index)
    y_pred = pd.Series([1, 0, 0, 0], index=df.index)
    
    result = check_bias(df, y_pred, y_test, "verified_purchase")
    
    # Check that both subgroups appear in the result.
    assert True in result, "Result should contain key True."
    assert False in result, "Result should contain key False."
    
    # Check expected accuracies.
    assert result[True] == 1.0, f"Expected accuracy for True is 1.0 but got {result[True]}"
    assert result[False] == 0.0, f"Expected accuracy for False is 0.0 but got {result[False]}"

def test_plot_bias(tmp_path):
    """
    Test that plot_bias correctly saves a plot image.
    We temporarily override the output folder to a temporary directory.
    """
    # Create a temporary folder to act as the output folder.
    temp_dir = tmp_path / "bias_detection_images"
    temp_dir.mkdir()

    # Save the original output_folder value.
    original_output_folder = output_folder

    # Override the module-level output_folder with the temporary directory.
    from Data_pipeline.dags.bias_detection import __dict__ as bias_dict
    bias_dict["output_folder"] = str(temp_dir)
    
    # Prepare dummy results and title.
    results = {"True": 0.8, "False": 0.5}
    title = "Test Plot"
    plot_bias(results, title)
    
    # Construct the expected file name.
    plot_file = os.path.join(str(temp_dir), f"{title.replace(' ', '_')}.png")
    assert os.path.exists(plot_file), "Plot file should be created."
    
    # Restore the original output_folder.
    bias_dict["output_folder"] = original_output_folder

def test_handle_bias():
    """
    Test the handle_bias function using a dummy dataset.
    We provide a sufficiently large dummy dataset for basic training and bias detection.
    """
    df = pd.DataFrame({
        "sentiment_label": [
            "positive", "negative", "positive", "positive", "negative",
            "positive", "negative", "positive", "negative", "positive"
        ],
        "rating": [5, 3, 4, 5, 2, 4, 3, 5, 2, 4],
        "verified_purchase": [True, True, False, True, False, False, True, True, False, False],
        "Category": ["A", "A", "B", "A", "B", "B", "A", "A", "B", "B"],
        "helpful_vote": [10, 5, 2, 8, 1, 4, 3, 6, 2, 5]
    })
    results = handle_bias(df)
    
    # Verify that the returned results is a dictionary.
    assert isinstance(results, dict), "handle_bias should return a dictionary of results."
    
    # Check for expected keys.
    expected_keys = ["verified_purchase_results", "sentiment_results", "category_results", "fair_results"]
    for key in expected_keys:
        assert key in results, f"Expected key '{key}' in results."