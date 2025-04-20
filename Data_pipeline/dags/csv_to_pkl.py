import os
import pandas as pd
import pickle

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE_PATH = os.path.join(PROJECT_DIR, 'data', 'unprocessed')
OUTPUT_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data', 'unprocessed_pkl')


def convert_all_csv_to_pickle(folder_path = INPUT_FILE_PATH, output_folder_path = OUTPUT_PICKLE_PATH):
    # Check if the output folder exists, if not create it
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file is a CSV
        if filename.endswith(".csv"):
            csv_path = os.path.join(folder_path, filename)
            pickle_path = os.path.join(output_folder_path, f"{os.path.splitext(filename)[0]}.pkl")

            try:
                # Load the CSV file into a pandas DataFrame
                df = pd.read_csv(csv_path)
                
                # Save the DataFrame as a pickle file
                with open(pickle_path, 'wb') as file:
                    pickle.dump(df, file, protocol=4)  # Use protocol 4 for compatibility with Python 3.7
                print(f"Converted {csv_path} to {pickle_path}")
            
            except Exception as e:
                print(f"Error converting {csv_path}: {e}")

