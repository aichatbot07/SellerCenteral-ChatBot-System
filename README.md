# SellerCenteral-ChatBot-System

## Overview
This project implements a chatbot for the Seller Central platform that helps users manage seller data efficiently. The pipeline processes JSONL data files, assigns seller IDs to products, and generates a merged CSV file. This repository also integrates with Google Cloud Storage (GCS) to handle the data.

---

## Table of Contents

- [Environment Setup](#environment-setup)
- [Pipeline Execution](#pipeline-execution)
- [Code Structure](#code-structure)
- [Reproducibility & Data Versioning](#reproducibility--data-versioning)
- [Code Style & Guidelines](#code-style--guidelines)
- [Error Handling & Logging](#error-handling--logging)
- [Contributing](#contributing)

---

## Environment Setup

Follow these steps to set up the environment on your local machine:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo-name/seller-central-chatbot.git
   cd seller-central-chatbot
2. **Create and activate a virtual environment:**

- For Python 3.x:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    
3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt


4. **Set up Google Cloud credentials:**
- Ensure you have a Google Cloud project and the necessary permissions to access GCS.
- Download your credentials.json from the Google Cloud Console and set the environment variable:
  ```
  export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
  ```

5. **DVC Setup (for data versioning):**
- Install DVC if not already installed:
  ```
  pip install dvc
  ```
- Initialize DVC in the repository:
  ```
  dvc init
  ```
- Pull the data files if they are tracked in DVC:
  ```
  dvc pull
  ```

## Pipeline Execution

To run the pipeline and process the data, follow these steps:

1. Ensure all dependencies are installed.

2. Activate the virtual environment:
    ```bash
    source venv/bin/activate # On Windows: venv\Scripts\activate

3. Run the pipeline script:
    ```bash
    python scripts/sellerId_check.py


4. Monitor the output:
- The output file `reviews_processed.csv` will be stored in the `processed/` folder on GCS.
- Logs will be printed to the terminal during the process.

## Code Structure

Here's a breakdown of the project's folder and file structure:

```bash
seller-central-chatbot/
│
├── scripts/
│   ├── sellerId_check.py          # Main pipeline script for processing data
│   └── helper_functions.py        # Helper functions for data processing and error handling
│
├── requirements.txt              # Python dependencies for the project
├── Dvc.yaml                      # DVC pipeline file
├── .gitignore                    # Git ignore file
├── README.md                     # Project documentation (this file)
└── data/
    ├── raw/                      # Raw data stored in GCS bucket
    ├── processed/                # Processed data output (CSV)
    └── reviews/                  # JSONL files containing reviews