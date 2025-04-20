import os
import pandas as pd
from itertools import combinations
import pickle
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define project directory and file paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'meta_data.pkl')
OUTPUT_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'best_bundled_together.pkl')
PREVIOUS_MODEL_OUTPUT_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'product_metadata_with_ml_performance_2.pkl')
UNPROCESSED_PICKEL_PATH = os.path.join(PROJECT_DIR, 'data', 'unprocessed_pkl', 'bought_together.pkl')


def find_category_based_copurchases_df(df, max_products_per_category=50):
    """Find products that can be bundled together based on category relationships"""
    logging.info(f"Input DataFrame columns: {df.columns.tolist()}")
    
    # Check for required columns
    required_cols = ["parent_asin", "categories", "title"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        # (column handling code remains the same...)
        pass
    
    # Check category distribution before filtering
    if 'main_category' in df.columns:
        category_counts = df['main_category'].value_counts()
        logging.info(f"Category distribution before filtering: {category_counts.head(10).to_dict()}")
    
    # Remove rows missing required data
    df = df.dropna(subset=["categories", "parent_asin", "title"])
    
    # Check category distribution after filtering
    if 'main_category' in df.columns:
        category_counts = df['main_category'].value_counts()
        logging.info(f"Category distribution after filtering: {category_counts.head(10).to_dict()}")
    
    # Log the shape after filtering
    logging.info(f"DataFrame shape after filtering: {df.shape}")
    logging.info(f"Sample data after filtering:\n{df.head()}")
    
    # Create a mapping for ASIN to title
    asin_to_title = dict(zip(df["parent_asin"], df["title"]))
    
    # Group ASINs by category
    # Ensure we process each main category separately
    groupby_col = "main_category" if "main_category" in df.columns else "categories"
    category_groups = df.groupby(groupby_col)["parent_asin"].apply(list)
    logging.info(f"Number of category groups: {len(category_groups)}")
    
    # Dictionary to collect bundling info for each parent_asin
    bundling_dict = {}
    
    # Process each category with logging
    for category, products in category_groups.items():
        # Limit the number of products per category
        if len(products) > max_products_per_category:
            logging.info(f"Category {category} has {len(products)} products, limiting to {max_products_per_category}")
            products = products[:max_products_per_category]
        
        if len(products) > 1:
            # Generate all unique pairs
            logging.info(f"Generating pairs for category: {category} with {len(products)} products")
            pairs_generated = 0
            
            for asin1, asin2 in combinations(products, 2):
                # For asin1
                if asin1 not in bundling_dict:
                    bundling_dict[asin1] = []
                bundling_dict[asin1].append(f"{asin2}: {asin_to_title.get(asin2, 'Unknown')}")
                
                # For asin2
                if asin2 not in bundling_dict:
                    bundling_dict[asin2] = []
                bundling_dict[asin2].append(f"{asin1}: {asin_to_title.get(asin1, 'Unknown')}")
                
                pairs_generated += 1
            
            logging.info(f"Generated {pairs_generated} pairs for category: {category}")
    
    # Convert dictionary to DataFrame
    data = []
    for asin, bundled_with in bundling_dict.items():
        # Take top 5 bundled products for each
        top_bundled = bundled_with[:5]
        bundled_str = " | ".join(top_bundled)
        data.append({
            "parent_asin": asin,
            "bought_together": bundled_str
        })
    
    result_df = pd.DataFrame(data)
    logging.info(f"Final co-purchase DataFrame shape: {result_df.shape}")
    
    # Check if products from all categories are represented
    if 'main_category' in df.columns:
        merged_temp = pd.merge(result_df, df[['parent_asin', 'main_category']], on='parent_asin', how='left')
        category_counts = merged_temp['main_category'].value_counts()
        logging.info(f"Categories in final result: {category_counts.head(10).to_dict()}")
    
    return result_df

def generate_copurchase_data():
    """Generate co-purchase recommendations with parent_asin and bought_together columns"""
    logging.info("Starting co-purchase recommendation generation")
    
    # Check if the output file already exists
    if os.path.exists(UNPROCESSED_PICKEL_PATH):
        logging.info(f"Output file {UNPROCESSED_PICKEL_PATH} already exists. Checking format...")
        
        try:
            with open(UNPROCESSED_PICKEL_PATH, "rb") as file:
                existing_df = pickle.load(file)
                logging.info(f"Existing file columns: {existing_df.columns.tolist()}")
                return existing_df
            
            
            if "parent_asin" not in existing_df.columns or "bought_together" not in existing_df.columns:
                logging.warning("Existing file doesn't have the right format. Regenerating.")

                

        except Exception as e:
            logging.warning(f"Cannot load existing file ({str(e)}). Will regenerate.")
    else:   
        try:
            # Read the input data
            logging.info(f"Reading input data from {INPUT_FILE_PATH}")
            df = None
            
            try:
                # Try to load as pickle first
                with open(INPUT_FILE_PATH, "rb") as file:
                    df = pickle.load(file)
                    logging.info(f"Successfully loaded pickle with columns: {df.columns.tolist() if hasattr(df, 'columns') else 'Not a DataFrame'}")
            except Exception as e:
                logging.warning(f"Error loading pickle: {e}")
                # If that fails, try CSV
                try:
                    csv_path = INPUT_FILE_PATH.replace('.pkl', '.csv')
                    logging.info(f"Attempting to load from CSV: {csv_path}")
                    df = pd.read_csv(csv_path, encoding="utf-8", delimiter=",", low_memory=False)
                except Exception as csv_e:
                    logging.error(f"Error loading CSV: {csv_e}")
                    raise ValueError(f"Could not load data from either pickle or CSV. Original error: {e}")
                
            if df is None or len(df) == 0:
                raise ValueError("Loaded DataFrame is empty or None")
                
            logging.info(f"Loaded input DataFrame with shape: {df.shape}")
            
            # Get co-purchase pairs as a DataFrame with parent_asin and bought_together columns
            copurchase_df = find_category_based_copurchases_df(df, max_products_per_category=50)
            
            if len(copurchase_df) == 0:
                logging.warning("No co-purchase recommendations generated. Creating dummy data.")
                copurchase_df = pd.DataFrame({
                    "parent_asin": ["A1", "A2", "A3"],
                    "bought_together": ["A2: Product 2 | A3: Product 3", 
                                        "A1: Product 1 | A3: Product 3",
                                        "A1: Product 1 | A2: Product 2"]
                })
            
            logging.info(f"Generated co-purchase DataFrame with shape: {copurchase_df.shape}")
            logging.info(f"Sample data:\n{copurchase_df.head()}")
            
            # # Save co-purchase data in the new format
            # with open(OUTPUT_PICKLE_PATH, "wb") as file:
            #     pickle.dump(copurchase_df, file, protocol=4)
            # logging.info(f"Saved co-purchase data to {OUTPUT_PICKLE_PATH}")
            
            return copurchase_df
        
        except Exception as e:
            logging.error(f"Error in generate_copurchase_data: {e}")
            raise

def merge_with_previous_model_output_bundle():
    """Merge product performance data into the co-purchase recommendations file"""
    logging.info("Starting merge with previous model output")
    copurchase_df = pd.DataFrame()
    # Generate co-purchase data first
    try:
        copurchase_df = generate_copurchase_data()
    except Exception as e:
        logging.error(f"Error generating co-purchase data: {e}")
        raise
    
    # Check if the previous model output file exists
    if not os.path.exists(PREVIOUS_MODEL_OUTPUT_PATH):
        logging.error(f"Previous model output file not found at {PREVIOUS_MODEL_OUTPUT_PATH}")
        raise FileNotFoundError(f"Previous model output file not found: {PREVIOUS_MODEL_OUTPUT_PATH}")
    
    try:
        # Load co-purchase data
        # with open(UNPROCESSED_PICKEL_PATH, "rb") as file:
        #     copurchase_df = pickle.load(file)
        # logging.info(f"Loaded co-purchase data with shape: {copurchase_df.shape}")
        
        # Load previous model output (product performance data)
        with open(PREVIOUS_MODEL_OUTPUT_PATH, "rb") as file:
            previous_df = pickle.load(file)
        logging.info(f"Loaded previous model output with shape: {previous_df.shape}")
        logging.info(f"Previous model columns: {previous_df.columns.tolist()}")
        
        # Convert parent_asin to string in both dataframes
        copurchase_df['parent_asin'] = copurchase_df['parent_asin'].astype(str)
        previous_df['parent_asin'] = previous_df['parent_asin'].astype(str)
        
        # Merge the data from previous_df into copurchase_df
        # Use a left merge to keep all co-purchase data
        result_df = pd.merge(
            copurchase_df,
            previous_df,
            on='parent_asin',
            how='outer'
        )
        
        logging.info(f"Final merged shape: {result_df.shape}")
        logging.info(f"Final columns: {result_df.columns.tolist()}")
        
        # Save the result to the best_bundled_together.pkl file
        with open(OUTPUT_PICKLE_PATH, "wb") as file:
            pickle.dump(result_df, file, protocol=4)
        logging.info(f"Saved merged data to {OUTPUT_PICKLE_PATH}")
        
        return OUTPUT_PICKLE_PATH
        
    except Exception as e:
        logging.error(f"Error in merge_with_previous_model_output: {e}")
        raise
    
