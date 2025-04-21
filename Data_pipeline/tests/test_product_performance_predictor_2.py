# import os
# import pickle
# import pytest
# import pandas as pd

# from types import ModuleType

# # Load the file as a dummy module to avoid circular import issues
# def load_functions_from_file(path):
#     with open(path, "r") as f:
#         code = f.read()
#     module = ModuleType("product_performance_predictor_2")
#     exec(code, module.__dict__)
#     return module

# # Path to the DAG Python file
# DAG_FILE = os.path.abspath(os.path.join(
#     os.path.dirname(__file__), "Data_pipeline", "dags", "product_performance_predictor_2.py"
# ))

# product_module = load_functions_from_file(DAG_FILE)

# @pytest.fixture
# def dummy_metadata_pickle(tmp_path):
#     df = pd.DataFrame({
#         'parent_asin': ['A1', 'A2', 'A3'],
#         'main_category': ['Electronics', 'Books', 'Toys'],
#         'title': ['P1', 'P2', 'P3'],
#         'average_rating': [4.5, 4.0, 3.5],
#         'rating_number': [10, 20, 30],
#         'price': [100, 200, 150]
#     })
#     p = tmp_path / "meta_data.pkl"
#     df.to_pickle(p)
#     return p

# @pytest.fixture
# def dummy_features_pickle(tmp_path):
#     df = pd.DataFrame({
#         'parent_asin': ['A1', 'A2', 'A3'],
#         'most_liked_features': ['Quality(90%)', 'Design(80%)', 'Battery(70%)']
#     })
#     p = tmp_path / "with_feature1.pkl"
#     with open(p, "wb") as f:
#         pickle.dump(df, f)
#     return p

# def test_safe_pickle_load_success(tmp_path):
#     df = pd.DataFrame({'x': [1, 2, 3]})
#     pkl_path = tmp_path / "test.pkl"
#     df.to_pickle(pkl_path)

#     result = product_module.safe_pickle_load(str(pkl_path))
#     assert isinstance(result, pd.DataFrame)
#     assert "x" in result.columns

# def test_merge_performance_and_features(tmp_path, dummy_metadata_pickle, dummy_features_pickle, monkeypatch):
#     monkeypatch.setattr(product_module, "INPUT_FILE_PATH", str(dummy_metadata_pickle))
#     monkeypatch.setattr(product_module, "PREVIOUS_MODEL_OUTPUT_PATH", str(dummy_features_pickle))
#     monkeypatch.setattr(product_module, "OUTPUT_PICKLE_PATH", str(tmp_path / "output.pkl"))
#     monkeypatch.setattr(product_module, "UNPROCESSED_PICKEL_PATH", str(tmp_path / "unprocessed.pkl"))

#     output_path = product_module.merge_performance_and_features()
#     assert os.path.exists(output_path)

#     with open(output_path, "rb") as f:
#         result = pickle.load(f)

#     assert "parent_asin" in result.columns
#     assert "predicted_performance_score" in result.columns
#     assert "most_liked_features" in result.columns