import os
import pytest
import pandas as pd
import pickle
from Data_pipeline.dags.best_bundled_together_3 import (
    find_category_based_copurchases_df,
    generate_copurchase_data,
    merge_with_previous_model_output_bundle,
)

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "parent_asin": ["A1", "A2", "A3", "A4"],
        "categories": [["Cat1"], ["Cat1"], ["Cat1"], ["Cat2"]],
        "title": ["Product 1", "Product 2", "Product 3", "Product 4"],
        "main_category": ["Main1", "Main1", "Main1", "Main2"]
    })

def test_find_category_based_copurchases_df_output_structure(sample_df):
    result = find_category_based_copurchases_df(sample_df)
    assert isinstance(result, pd.DataFrame), "Output should be a DataFrame"
    assert "parent_asin" in result.columns, "'parent_asin' should be a column in result"
    assert "bought_together" in result.columns, "'bought_together' should be a column in result"
    assert not result.empty, "Resulting DataFrame should not be empty"

def test_find_category_based_copurchases_df_pairing_logic():
    df = pd.DataFrame({
        "parent_asin": ["A1", "A2"],
        "categories": [["Cat1"], ["Cat1"]],
        "title": ["Product 1", "Product 2"],
        "main_category": ["Main1", "Main1"]
    })
    result = find_category_based_copurchases_df(df)
    assert "A1" in result["parent_asin"].values
    assert "A2: PRODUCT 2" in result[result["parent_asin"] == "A1"]["bought_together"].values[0].upper()

def test_generate_copurchase_data_with_dummy_fallback(tmp_path):
    dummy_path = tmp_path / "meta_data.pkl"
    df = pd.DataFrame({
        "parent_asin": ["A1", "A2"],
        "categories": [["X"], ["X"]],
        "title": ["Prod1", "Prod2"],
        "main_category": ["Main", "Main"]
    })
    with open(dummy_path, "wb") as f:
        pickle.dump(df, f)

    # Temporarily patch the input path
    from Data_pipeline.dags import best_bundled_together_3
    original_path = best_bundled_together_3.INPUT_FILE_PATH
    best_bundled_together_3.INPUT_FILE_PATH = str(dummy_path)

    result_df = generate_copurchase_data()
    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty

    best_bundled_together_3.INPUT_FILE_PATH = original_path

def test_merge_with_previous_model_output_bundle(tmp_path):
    # Mock copurchase and performance data
    copurchase_df = pd.DataFrame({
        "parent_asin": ["A1"],
        "bought_together": ["A2: Test Product"]
    })
    performance_df = pd.DataFrame({
        "parent_asin": ["A1"],
        "score": [4.5]
    })

    # Save them to temporary paths
    copurchase_path = tmp_path / "bought_together.pkl"
    perf_path = tmp_path / "performance.pkl"
    final_path = tmp_path / "final.pkl"

    with open(copurchase_path, "wb") as f:
        pickle.dump(copurchase_df, f)
    with open(perf_path, "wb") as f:
        pickle.dump(performance_df, f)

    # Patch internal paths
    from Data_pipeline.dags import best_bundled_together_3
    original_cop = best_bundled_together_3.UNPROCESSED_PICKEL_PATH
    original_perf = best_bundled_together_3.PREVIOUS_MODEL_OUTPUT_PATH
    original_out = best_bundled_together_3.OUTPUT_PICKLE_PATH

    best_bundled_together_3.UNPROCESSED_PICKEL_PATH = str(copurchase_path)
    best_bundled_together_3.PREVIOUS_MODEL_OUTPUT_PATH = str(perf_path)
    best_bundled_together_3.OUTPUT_PICKLE_PATH = str(final_path)

    output = merge_with_previous_model_output_bundle()
    assert os.path.exists(output), "Output file should exist after merge"

    # Cleanup: reset paths
    best_bundled_together_3.UNPROCESSED_PICKEL_PATH = original_cop
    best_bundled_together_3.PREVIOUS_MODEL_OUTPUT_PATH = original_perf
    best_bundled_together_3.OUTPUT_PICKLE_PATH = original_out