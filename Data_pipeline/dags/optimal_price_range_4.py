import os
import pandas as pd
import numpy as np
import re
import warnings
import pickle
import logging
# import sys

# import pandas._libs.internals as internals
# sys.modules['pandas.core.internals.blocks'] = internals

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Suppress FutureWarnings from Pandas
warnings.simplefilter(action='ignore', category=FutureWarning)

# Define project directory and file paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'meta_data.pkl')
OUTPUT_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'optimal_price_range.pkl')
PREVIOUS_MODEL_OUTPUT_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'best_bundled_together.pkl')
UNPROCESSED_PICKEL_PATH = os.path.join(PROJECT_DIR, 'data', 'unprocessed_pkl', 'optimal_price_range.pkl')

def clean_price(value):
    """Convert price to float after removing non-numeric characters."""
    try:
        value = str(value)
        value = re.sub(r"[^\d.]", "", value)  # Keep only digits and period
        return float(value) if value else np.nan  
    except Exception:
        return np.nan

def maximum_profitability_strategy():
    """Calculate optimal price range for maximizing profitability and save to pickle file."""
    logging.info("Starting optimal price range calculation")
    
    # Check if output file already exists
    if os.path.exists(UNPROCESSED_PICKEL_PATH):
        logging.info(f"Output file {UNPROCESSED_PICKEL_PATH} already exists. Skipping processing.")
        price_df = pickle.load(file)
        return price_df
    else :
        logging.info(f"Does not exist")
    
    try:
        # Load meta data
        logging.info(f"Loading meta data from {INPUT_FILE_PATH}")
        try:
            df = pd.read_pickle(INPUT_FILE_PATH)
            logging.info(f"Loaded meta data with shape: {df.shape}")
        except Exception as e:
            logging.error(f"Error loading meta data: {e}")
            raise ValueError("Could not load meta_data using pickle")
        
        # Validate required columns
        required_columns = ['main_category', 'price', 'rating_number', 'parent_asin']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logging.warning(f"Missing required columns: {missing_columns}")
            # Try to find alternative columns
            if 'main_category' in missing_columns and 'categories' in df.columns:
                logging.info("Using 'categories' instead of 'main_category'")
                df['main_category'] = df['categories']
            if 'rating_number' in missing_columns and 'numRatings' in df.columns:
                logging.info("Using 'numRatings' instead of 'rating_number'")
                df['rating_number'] = df['numRatings']
            if 'parent_asin' in missing_columns:
                asin_cols = [col for col in df.columns if "asin" in col.lower()]
                if asin_cols:
                    logging.info(f"Using '{asin_cols[0]}' as parent_asin")
                    df['parent_asin'] = df[asin_cols[0]]
            
            # Check again after replacements
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logging.error(f"Still missing required columns: {missing_columns}")
                optimal_price_range_df = pd.DataFrame(columns=['parent_asin', 'optimal_price_min', 'optimal_price_max'])
                with open(OUTPUT_PICKLE_PATH, "wb") as file:
                    pickle.dump(optimal_price_range_df, file, protocol=4)
                logging.warning(f"Saved empty result to {OUTPUT_PICKLE_PATH} due to missing columns")
                return OUTPUT_PICKLE_PATH
        
        # Clean and convert price
        logging.info("Cleaning and processing data")
        df['price'] = df['price'].apply(clean_price)
        df = df.dropna(subset=['price'])
        df['price'] = df['price'].astype(float)
        
        # Convert data types and estimate sales volume
        df['main_category'] = df['main_category'].astype(str)
        df['parent_asin'] = df['parent_asin'].astype(str)
        df['rating_number'] = pd.to_numeric(df['rating_number'], errors='coerce').fillna(0).astype(int)
        df['sales_volume'] = df['rating_number'].apply(lambda x: max(1, x * np.random.uniform(1.5, 2.5)))
        
        # Competitive price analysis
        logging.info("Performing price analysis by category")
        df['avg_competitor_price'] = df.groupby('main_category')['price'].transform('mean')
        df['avg_competitor_price'] = df['avg_competitor_price'].fillna(df['price'].median())
        
        # Price difference calculation
        df['price_difference'] = df['price'] - df['avg_competitor_price']
        
        # Revenue and profitability calculations
        logging.info("Calculating profitability metrics")
        df['revenue'] = df['price'] * df['sales_volume']
        df['profit_margin'] = df['revenue'] - (df['avg_competitor_price'] * df['sales_volume'])
        df['profitability_score'] = df['profit_margin'] / (df['avg_competitor_price'] + 1)
        
        # Remove extreme outliers in price (top 1% threshold)
        price_threshold = df['price'].quantile(0.99)
        df = df[df['price'] < price_threshold]
        logging.info(f"Removed price outliers above {price_threshold:.2f}")
        
        # Determine profitability threshold using median
        profit_threshold = df['profitability_score'].median()
        logging.info(f"Profitability threshold: {profit_threshold:.4f}")
        
        # Find optimal price range for categories with above-median profitability
        logging.info("Calculating optimal price ranges by category")
        optimal_price_range = (
            df[df['profitability_score'] > profit_threshold]
            .groupby('main_category')['price']
            .agg(['min', 'max'])
            .reset_index()
        )
        logging.info(f"Generated optimal price ranges for {len(optimal_price_range)} categories")
        
        # Map each category to all parent_asins in that category
        category_to_asins = {}
        for main_category in optimal_price_range['main_category']:
            category_mask = df['main_category'] == main_category
            if category_mask.any():
                asins = df.loc[category_mask, 'parent_asin'].unique()
                if len(asins) > 0:
                    category_to_asins[main_category] = asins
        
        # Create rows for each parent_asin with its category's price range
        final_rows = []
        for _, row in optimal_price_range.iterrows():
            main_category = row['main_category']
            if main_category in category_to_asins:
                for asin in category_to_asins[main_category]:
                    final_rows.append({
                        'parent_asin': asin,
                        'optimal_price_min': row['min'],
                        'optimal_price_max': row['max']
                    })
        
        # Create final dataframe with parent_asin for merging
        final_df = pd.DataFrame(final_rows)
        logging.info(f"Final result shape: {final_df.shape}")
        
        # # Save the result as a pickle file
        # with open(OUTPUT_PICKLE_PATH, "wb") as file:
        #     pickle.dump(final_df, file, protocol=4)
        # logging.info(f"Saved optimal price ranges to {OUTPUT_PICKLE_PATH}")
        
        return final_df
        
    except Exception as e:
        logging.error(f"Error in maximum_profitability_strategy: {e}")
        raise

def merge_with_previous_model_output():
    """Merge the complete previous output (bundled together file) with the optimal price data.
       Rows with matching parent_asin will have their 'optimal_price_min' and 'optimal_price_max'
       values overridden by the new optimal price data, while all other columns (e.g., most_liked_features)
       are preserved. The merged result is saved to OUTPUT_PICKLE_PATH.
    """
    logging.info("Starting merge of new data sentiment with optimal price range data")
    
    try:
        # First, ensure that the optimal price data is generated.
        price_df = maximum_profitability_strategy()
    except Exception as e:
        logging.error(f"Error generating optimal price data: {e}")
        raise
    
    # Check if the new optimal price data file exists
    # if not os.path.exists(UNPROCESSED_PICKEL_PATH):
    #     logging.error(f"Optimal price data file not found at {UNPROCESSED_PICKEL_PATH}")
    #     raise FileNotFoundError(f"Optimal price data file not found: {UNPROCESSED_PICKEL_PATH}")
    
    # Check that the complete previous output (bundled together file) exists
    if not os.path.exists(PREVIOUS_MODEL_OUTPUT_PATH):
        logging.error(f"Bundled together file not found at {PREVIOUS_MODEL_OUTPUT_PATH}")
        raise FileNotFoundError(f"Bundled together file not found: {PREVIOUS_MODEL_OUTPUT_PATH}")
    
    try:
        # # Load the new optimal price data
        # with open(UNPROCESSED_PICKEL_PATH, "rb") as file:
        #     price_df = pickle.load(file)
        # logging.info(f"Loaded optimal price data with shape: {price_df.shape}")
        
        # Load the complete previous output (bundled together file)
        with open(PREVIOUS_MODEL_OUTPUT_PATH, "rb") as file:
            previous_df = pickle.load(file)
        logging.info(f"Loaded previous output with shape: {previous_df.shape}")
        logging.info(f"Previous output columns: {previous_df.columns.tolist()}")
        
        # Ensure 'parent_asin' is a string in both DataFrames
        previous_df['parent_asin'] = previous_df['parent_asin'].astype(str)
        price_df['parent_asin'] = price_df['parent_asin'].astype(str)
        
        # Set index to 'parent_asin' for both DataFrames
        previous_indexed = previous_df.set_index('parent_asin')
        price_indexed = price_df.set_index('parent_asin')
        
        # Check if the optimal price columns exist in the previous output.
        # If they do not exist, add them (they'll be created).
        if 'optimal_price_min' not in previous_indexed.columns:
            previous_indexed['optimal_price_min'] = np.nan
        if 'optimal_price_max' not in previous_indexed.columns:
            previous_indexed['optimal_price_max'] = np.nan
        
        # Override the optimal price columns in the previous output with the new values.
        # This will update only rows where the parent_asin exists in price_indexed.
        previous_indexed.update(price_indexed[['optimal_price_min', 'optimal_price_max']])
        
        # Reset the index to turn 'parent_asin' back into a column
        final_df = previous_indexed.reset_index()
        
        logging.info(f"Final merged data shape: {final_df.shape}")
        logging.info(f"Final columns: {final_df.columns.tolist()}")
        logging.info(f"Number of rows with optimal price data: {final_df['optimal_price_min'].notna().sum()}")
        
        # Save the merged result to the new data sentiment output pickle path
        with open(OUTPUT_PICKLE_PATH, "wb") as file:
            pickle.dump(final_df, file, protocol=4)
        logging.info(f"Saved merged data to {OUTPUT_PICKLE_PATH}")
        
        return OUTPUT_PICKLE_PATH
        
    except Exception as e:
        logging.error(f"Error in merge_with_previous_model_output: {e}")
        raise


