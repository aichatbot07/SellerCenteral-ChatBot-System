import os
import pandas as pd
import pickle
import logging
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define project directory and file paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Path to the input metadata pickle file
INPUT_FILE_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'meta_data.pkl')
# Path to the most liked features pickle file
PREVIOUS_MODEL_OUTPUT_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'with_feature1.pkl')
# Output path for the merged pickle file
OUTPUT_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'product_metadata_with_ml_performance_2.pkl')

UNPROCESSED_PICKEL_PATH = os.path.join(PROJECT_DIR, 'data', 'unprocessed_pkl', 'product_metadata_with_ml_performance.pkl')


def safe_pickle_load(pickle_path):
    """Load a pickle file safely, handling version compatibility issues"""
    try:
        # Try direct file read method which might bypass some pandas internals
        with open(pickle_path, 'rb') as f:
            try:
                # First try with highest protocol
                return pickle.load(f)
            except:
                # If that fails, try with compatibility mode
                f.seek(0)
                return pd.DataFrame(pickle.load(f, encoding='latin1'))
    except Exception as e:
        logging.error(f"Error loading pickle file {pickle_path}: {e}")
        raise

def merge_performance_and_features():
    """
    Loads the metadata pickle and the most liked features pickle,
    merges them on 'parent_asin', and saves the merged DataFrame as a new pickle file.
    """
    logging.info("Starting merge of performance and features data")
    df_perf = pd.DataFrame()
    
    
    # Check if output exists
    if os.path.exists(UNPROCESSED_PICKEL_PATH):
        logging.info(f"Output file {UNPROCESSED_PICKEL_PATH} already exists. Skipping processing.")
        with open(UNPROCESSED_PICKEL_PATH, "rb") as file:
            df_perf = pickle.load(file)
        # logging.info(f"Merged pickle file saved to {OUTPUT_PICKLE_PATH}")
    else:
        logging.info("trying to run the model")
        try:
            with open(INPUT_FILE_PATH, "rb") as file:
                df_perf = pickle.load(file)
            logging.info("trying to run the model")
            df_perf = df_perf[['parent_asin', 'main_category', 'title', 'average_rating', 'rating_number', 'price']].dropna()
            logging.info("trying to run the model1")

            # Step 2: Create a synthetic target variable.
            # Here, performance_target is defined as average_rating multiplied by log1p(rating_number)
            # This assumes that both rating quality and review volume contribute to performance.
            df_perf['performance_target'] = df_perf['average_rating'] * np.log1p(df_perf['rating_number'])
            logging.info("trying to run the model2")
            
            # Step 3: Define features and target for the model.
            features = ['average_rating', 'rating_number', 'price', 'main_category']
            target = 'performance_target'
            logging.info("trying to run the model3")
            X = df_perf[features]
            y = df_perf[target]
            logging.info("trying to run the model4")
            # Step 4: Split data into training and testing sets.
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Step 5: Set up preprocessing for numerical and categorical features.
            numeric_features = ['average_rating', 'rating_number', 'price']
            categorical_features = ['main_category']
            
            numeric_transformer = Pipeline(steps=[
                ('scaler', StandardScaler())
            ])
            
            categorical_transformer = Pipeline(steps=[
                ('onehot', OneHotEncoder(handle_unknown='ignore'))
            ])
            
            preprocessor = ColumnTransformer(
                transformers=[
                    ('num', numeric_transformer, numeric_features),
                    ('cat', categorical_transformer, categorical_features)
                ])
            
            # Step 6: Create an ML pipeline with the preprocessor and a RandomForestRegressor.
            model_pipeline = Pipeline(steps=[
                ('preprocessor', preprocessor),
                ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
            ])
            
            # Step 7: Train the model.
            model_pipeline.fit(X_train, y_train)
            
            # Step 8: Evaluate the model on the test set.
            y_pred = model_pipeline.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            print("Test Mean Squared Error:", mse)
            
    # Step 9: Use the trained model to predict performance scores for all products.
            df_perf['predicted_performance_score'] = model_pipeline.predict(X)
        except Exception as e:
            # If we can't load the pickle, create dummy data for testing
            logging.warning(f"Creating dummy performance data due to error: {e}")
            df_perf = pd.DataFrame({
                'parent_asin': ['A1', 'A2', 'A3'],
                'main_category': ['Category1', 'Category2', 'Category3'],
                'title': ['Product 1', 'Product 2', 'Product 3'],
                'average_rating': [4.5, 4.0, 3.5],
                'rating_number': [10, 20, 30],
                'price': [19.99, 29.99, 39.99],
                'performance_target': [0.8, 0.7, 0.6],
                'predicted_performance_score': [0.75, 0.65, 0.55]
            })
    
    # Load features data
    try:
        df_features = safe_pickle_load(PREVIOUS_MODEL_OUTPUT_PATH)
        logging.info(f"Loaded features DataFrame. Shape: {df_features.shape}")
    except Exception as e:
        # If we can't load the pickle, create dummy data for testing
        logging.warning(f"Creating dummy features data due to error: {e}")
        df_features = pd.DataFrame({
            'parent_asin': ['A1', 'A2', 'A4'],
            'most_liked_features': ['FEATURE1(45%), FEATURE2(30%)', 'FEATURE3(50%)', 'FEATURE5(25%)']
        })
    
    # Convert parent_asin to string in both DataFrames for consistent merging
    df_perf['parent_asin'] = df_perf['parent_asin'].astype(str)
    df_features['parent_asin'] = df_features['parent_asin'].astype(str)
    
    # Merge the two DataFrames on 'parent_asin'
    df_merged = pd.merge(df_perf, df_features, on='parent_asin', how='outer')
    logging.info(f"Merged DataFrame shape: {df_merged.shape}")
    logging.info(f"Merged DataFrame columns: {df_merged.columns.tolist()}")
    
    # Save the merged DataFrame to pickle using protocol 2 (more compatible)
    try:
        with open(OUTPUT_PICKLE_PATH, "wb") as file:
            pickle.dump(df_merged, file, protocol=2)
        logging.info(f"Merged pickle file saved to {OUTPUT_PICKLE_PATH}")
    except Exception as e:
        logging.error(f"Error saving merged pickle file: {e}")
        raise
    
    return OUTPUT_PICKLE_PATH



if __name__ == "__main__":
    merge_performance_and_features()