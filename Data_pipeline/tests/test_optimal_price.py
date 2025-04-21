import os
import pickle
import tempfile
import pandas as pd
import pytest
import numpy as np

from Data_pipeline.dags import optimal_price_range_4 as opr


@pytest.fixture
def sample_meta_data():
    """Creates a sample DataFrame to mock meta_data.pkl."""
    return pd.DataFrame({
        "main_category": ["A", "A", "B", "B"],
        "price": ["$10.99", "$12.49", "$15.00", "$14.75"],
        "rating_number": [10, 20, 5, 8],
        "parent_asin": ["asin1", "asin2", "asin3", "asin4"]
    })


@pytest.fixture
def bundled_output():
    """Creates a dummy bundled output file to simulate previous model."""
    return pd.DataFrame({
        "parent_asin": ["asin1", "asin2", "asin3", "asin4"],
        "some_feature": [1, 2, 3, 4]
    })


def test_maximum_profitability_strategy_valid(tmp_path, sample_meta_data):
    # Create a temp pickle file
    meta_path = tmp_path / "meta_data.pkl"
    with open(meta_path, "wb") as f:
        pickle.dump(sample_meta_data, f)

    opr.INPUT_FILE_PATH = str(meta_path)  # Override path
    opr.UNPROCESSED_PICKEL_PATH = ""  # Disable skipping logic

    df = opr.maximum_profitability_strategy()

    assert not df.empty
    assert "optimal_price_min" in df.columns
    assert "optimal_price_max" in df.columns
    assert "parent_asin" in df.columns


def test_merge_with_previous_model_output(tmp_path, sample_meta_data, bundled_output):
    # Write input and bundled files
    meta_path = tmp_path / "meta_data.pkl"
    bundle_path = tmp_path / "bundled.pkl"
    output_path = tmp_path / "final.pkl"

    with open(meta_path, "wb") as f:
        pickle.dump(sample_meta_data, f)

    with open(bundle_path, "wb") as f:
        pickle.dump(bundled_output, f)

    # Patch paths
    opr.INPUT_FILE_PATH = str(meta_path)
    opr.PREVIOUS_MODEL_OUTPUT_PATH = str(bundle_path)
    opr.OUTPUT_PICKLE_PATH = str(output_path)
    opr.UNPROCESSED_PICKEL_PATH = ""  # Avoid early return

    result_path = opr.merge_with_previous_model_output()

    assert os.path.exists(result_path)
    with open(result_path, "rb") as f:
        result_df = pickle.load(f)

    assert "optimal_price_min" in result_df.columns
    assert result_df["optimal_price_min"].notnull().any()