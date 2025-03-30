import os
import sys
import warnings
import pandas as pd
import importlib

# Suppress runtime warnings for empty slices and other deprecations.
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Ensure the repository root is in sys.path.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Reload config to ensure any changes are applied.
import Data_pipeline.dags.config as config
importlib.reload(config)

# Force re-import of fetch_data if it was already imported.
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
    Verify that check_bias returns correct accuracy for subgroups.
    """
    # Create a sample DataFrame.
    df = pd.DataFrame({"verified_purchase": [True, True, False, False]})
    y_test = pd.Series([1, 0, 1, 1], index=df.index)
    y_pred = pd.Series([1, 0, 0, 0], index=df.index)
    
    result = check_bias(df, y_pred, y_test, "verified_purchase")
    
    # Verify that both subgroups are present and have the expected accuracy.
    assert True in result, "Result should contain key True."
    assert False in result, "Result should contain key False."
    assert result[True] == 1.0, f"Expected accuracy for True is 1.0 but got {result[True]}"
    assert result[False] == 0.0, f"Expected accuracy for False is 0.0 but got {result[False]}"

def test_plot_bias(tmp_path):
    """
    Verify that plot_bias correctly saves a plot image.
    """
    temp_dir = tmp_path / "bias_detection_images"
    temp_dir.mkdir()

    # Override output_folder temporarily.
    from Data_pipeline.dags.bias_detection import __dict__ as bias_dict
    original_output_folder = bias_dict.get("output_folder")
    bias_dict["output_folder"] = str(temp_dir)
    
    # Call plot_bias with dummy results.
    results = {"True": 0.8, "False": 0.5}
    title = "Test Plot"
    plot_bias(results, title)
    
    # Construct expected file name and check its existence.
    plot_file = os.path.join(str(temp_dir), f"{title.replace(' ', '_')}.png")
    assert os.path.exists(plot_file), "Plot file should be created."
    
    # Restore original output_folder.
    bias_dict["output_folder"] = original_output_folder

def test_handle_bias():
    """
    Verify that handle_bias returns a dictionary with the expected keys.
    """
    df = pd.DataFrame({
        "sentiment_label": ["positive", "negative", "positive", "positive", "negative", 
                            "positive", "negative", "positive", "negative", "positive"],
        "rating": [5, 3, 4, 5, 2, 4, 3, 5, 2, 4],
        "verified_purchase": [True, True, False, True, False, False, True, True, False, False],
        "Category": ["A", "A", "B", "A", "B", "B", "A", "A", "B", "B"],
        "helpful_vote": [10, 5, 2, 8, 1, 4, 3, 6, 2, 5]
    })
    results = handle_bias(df)
    
    # Verify that the result is a dictionary and contains the expected keys.
    assert isinstance(results, dict), "handle_bias should return a dictionary."
    for key in ["verified_purchase_results", "sentiment_results", "category_results", "fair_results"]:
        assert key in results, f"Expected key '{key}' in results."

if __name__ == "__main__":
    test_check_bias()
    test_plot_bias(tmp_path=".")
    test_handle_bias()
    print("All bias detection tests passed.")