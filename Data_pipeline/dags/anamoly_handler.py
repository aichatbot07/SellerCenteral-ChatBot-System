import pandas as pd
import os
import pandas as pd
import pickle

# Load your dataset
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data',
                                 'processed','raw_data.pkl')
OUTPUT_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data',
                                  'processed', 'after_anomaly_process.pkl')

def remove_anomalies(input_pickle_path=INPUT_PICKLE_PATH,
                           output_pickle_path=OUTPUT_PICKLE_PATH):
    # Load DataFrame from input pickle
    if os.path.exists(input_pickle_path):
        with open(input_pickle_path, "rb") as file:
            df = pickle.load(file)
    else:
        raise FileNotFoundError(f"No data found at the specified path: {input_pickle_path}")
    print(f"Original dataset shape: {df.shape}")
    # 1. **Remove Missing Values**
    # df = df.dropna()
    
    # 2. **Remove Outliers (for 'rating' column)**
    Q1 = df['rating'].quantile(0.25)
    Q3 = df['rating'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df = df[(df['rating'] >= lower_bound) & (df['rating'] <= upper_bound)]
    
    # 3. **Remove Invalid Ratings (Keep only ratings between 1 and 5)**
    df = df[df['rating'].between(1, 5)]
    
    # # 4. **Remove Invalid Timestamp Format**
    # df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    # df = df.dropna(subset=['timestamp'])

    print(f"Anamoly removed dataset shape: {df.shape}")

    with open(output_pickle_path, "wb") as file:
        pickle.dump(df, file)
    print(f"Data saved to {output_pickle_path}.")

    print(f"Anomalies removed. Cleaned dataset saved to 'Subscription_Boxes_Cleaned.csv'.")

    return output_pickle_path
