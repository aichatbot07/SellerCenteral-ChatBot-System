# SellerCenteral-ChatBot-System

## **Overview**
The **Seller Central AI Chatbot** is an intelligent assistant designed to help Amazon sellers analyze product reviews and metadata, retrieve relevant information, and answer seller-related queries. It leverages **LangChain**, **FAISS**, and **BigQuery** to provide accurate and insightful responses.

---

## **Features**
- Fetch product reviews and metadata from **Google BigQuery**.
- Create retrievers using **FAISS** for efficient document retrieval.
- Generate intelligent responses using a conversational retrieval QA chain.
- Evaluate chatbot performance using retrieval and response quality metrics.
- Modular design for maintainability and scalability.

---

## **Folder Structure**

```plaintext
Seller_central_AIChatbot/
│
├── .github/
│   └── workflows/
│       └── ci.yml                               # GitHub Actions workflow for CI/CD pipeline.
├── config/
│   └── config.py                                # Environment variable configuration file (.env loader). 
├── Data
│   ├── fetch_reviews.py                         # Functions to fetch user reviews from BigQuery.
│   └── meta_data.py                             # Functions to fetch meta data from BigQuery.
├── Data_pipeline                                # Complete data pipline structure (dive into it to explore in details)
├── model_evaluation                             # Contains scripts for evaluating the chatbot's performance.
│   ├── bias_detection.py                        # Script to detect and mitigate bias in the dataset or model responses.          
│   ├── evaluate_responses.py                    # Evaluates response quality using metrics like BLEU and ROUGE.
│   ├── evaluate_retrieval.py                    # Evaluates retrieval performance using metrics like Precision@k and Recall@k.
│   ├── run.py                                   # Orchestrates the evaluation process by running retrieval and response.
│   ├── tracking_code.py                         # Tracks evaluation metrics and logs them for analysis.
│   └── utils.py                                 # Utility functions for loading datasets, preprocessing, or other shared tasks.
├── src
│   ├── app.py                                   # Main Streamlit application file.
│   ├── chain.py                                 # Functions to creat QA chain from retrievers.
│   └── create_retriever.py                      # Functions to create retrievers from DataFrames.                   
├── tests/
│   └── test_pipeline.py                         # Unit tests for pipeline components.
├── requirements.txt                             # Python dependencies file.
└── Dockerfile                                   # Containerization setup file.

```

---

## **Setup Instructions**

### **Prerequisites**
1. Install Python 3.9 or later.
2. Set up a Google Cloud Platform (GCP) project with:
   - BigQuery enabled.
   - A service account key JSON file downloaded for authentication.
3. Obtain API keys:
   - HuggingFace API token (`HF_TOKEN`).
   - DeepSeek API key (`DEEPSEEK_API_KEY`).
   - LangFuse public and secret keys (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`).

---

### **Installation**
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Seller_central_AIChatbot.git
   cd Seller_central_AIChatbot/
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your environment variables in a `.env` file:
   ```plaintext
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account.json
   HF_TOKEN=
   DEEPSEEK_API_KEY=
   LANGFUSE_PUBLIC_KEY=
   LANGFUSE_SECRET_KEY=
   LANGFUSE_HOST=
   BUCKET_NAME=
   ```

---

### **Running Locally**
1. Start the Streamlit application:
    ```bash
   cd src
   ```
   ```bash
   streamlit run app.py
   ```

2. Open your browser at `http://localhost:8501` to interact with the chatbot.

---

### **Testing the Pipeline**
Run unit tests using `pytest`:
```bash
pytest tests/
```

---

### **Deployment (Optional)**

#### Using Docker:
1. Build the Docker image:
   ```bash
   docker build -t seller_central_chatbot .
   ```

2. Run the container:
   ```bash
   docker run -p 8501:8501 seller_central_chatbot
   ```

#### Using GitHub Actions (CI/CD):
- The GitHub Actions workflow (`.github/workflows/ci.yml`) automates testing and deployment.

---

## **How It Works**

### **1. Fetching Data**
- The chatbot fetches product reviews and metadata from BigQuery using `fetch_reviews.py` and `fetch_metadata()` functions.

### **2. Creating a Retriever**
- Reviews are converted into vector embeddings using HuggingFace models, stored in a FAISS index, and used as a retriever (`create_retriever.py`).

### **3. Generating Responses**
- The retriever is combined with a conversational QA chain (`qa_chain.py`) to generate intelligent responses based on user queries.

### **4. Evaluation**
- The chatbot's performance is evaluated using retrieval metrics (Precision@k, Recall@k) and response quality metrics (BLEU, ROUGE-L).

---

## **Technologies Used**
- [Streamlit](https://streamlit.io/) for the user interface.
- [Google BigQuery](https://cloud.google.com/bigquery) for data storage and querying.
- [LangChain](https://langchain.com/) for building conversational AI pipelines.
- [FAISS](https://faiss.ai/) for vector-based document retrieval.
- [HuggingFace Transformers](https://huggingface.co/) for embedding generation.

---

## **Contributing**
Contributions are welcome! If you'd like to contribute to this project:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

---
=======

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

1. *Clone the repository:*
   bash
   git clone https://github.com/your-repo-name/seller-central-chatbot.git
   cd seller-central-chatbot
2. **Create and activate a virtual environment:**

- For Python 3.x:
    bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    
3. *Install the required dependencies:*
    bash
    pip install -r requirements.txt


4. **Set up Google Cloud credentials:**
- Ensure you have a Google Cloud project and the necessary permissions to access GCS.
- Download your credentials.json from the Google Cloud Console and set the environment variable:
  
  export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
  

5. **DVC Setup (for data versioning):**
- Install DVC if not already installed:
  
  pip install dvc
  
- Initialize DVC in the repository:
  
  dvc init
  
- Pull the data files if they are tracked in DVC:
  
  dvc pull
  

## Pipeline Execution

To run the pipeline and process the data, follow these steps:

### **1. Ensure all dependencies are installed**  
If dependencies are missing, install them using:
bash
pip install -r requirements.txt


### **2. Activate the virtual environment**  
bash
source venv/bin/activate  # On Windows: venv\Scripts\activate


### **3. Run the pipeline script**  

#### **Run the Data Pipeline manually:**  
bash
python Data_pipeline/dags/fetch_data.py        # Fetch raw data
python Data_pipeline/dags/data_process.py      # Process raw data
python Data_pipeline/dags/bias_detection.py    # Detect bias in data
python Data_pipeline/dags/dataflow_processing.py # Perform dataflow processing
python Data_pipeline/dags/sellerId_check.py    # Validate seller ID information
python Data_pipeline/dags/mlops_airflow.py     # Run MLOps integration


#### **Run the pipeline using Apache Airflow:**  
bash
airflow db init                      # Initialize Airflow database
airflow scheduler &                   # Start Airflow scheduler
airflow webserver --port 8080         # Start Airflow webserver (http://localhost:8080)

**Enable and trigger DAGs inside Airflow UI:**.

### **4. Monitor the output**  
- The processed output files will be stored in the **data/** folder.  
- Bias detection logs will be stored in **Data_pipeline/dags/bias_detection.log**.  
- Execution logs will be printed to the terminal and stored in **logs/pipeline.log**.  
- If using **Google Cloud Storage (GCS)**, processed files will be stored in **processed/** on GCS.  

## Code Structure

Here's a breakdown of the project's folder and file structure:

```
 SellerCentral-Chatbot-System/
 │
 ├── Data_pipeline/              # Main data pipeline directory
 │   ├── .dvc/                   # Data Version Control (DVC) metadata
 │   │   ├── .gitignore
 │   │   ├── config
 │   │
 │   ├── dags/                    # Apache Airflow DAGs (Directed Acyclic Graphs)
 │   │   ├── __pycache__/         # Cached compiled Python files
 │   │   ├── bias_detection.py    # Bias detection logic
 │   │   ├── config.py            # Configuration settings
 │   │   ├── data_process.py      # Data processing logic
 │   │   ├── dataflow_processing.py  # Main dataflow script
 │   │   ├── fetch_data.py        # Fetches raw data from GCS
 │   │   ├── logging_setup.py     # Logging configurations
 │   │   ├── mlops_airflow.py     # MLOps integration with Airflow
 │   │   ├── sellerId_check.py    # Data validation script
 │   │   ├── .gitignore           # Ignore unnecessary files
 │   │   ├── bias_detection.log   # Bias detection logs
 │   │
 │   ├── data/                    # Data directory (tracked via DVC)
 │   │   ├── .gitignore
 │   │   ├── new_data_sentiment.csv.dvc  # Tracked dataset
 │   │
 │   ├── logs/                    # Logs for debugging and monitoring
 │   │   ├── .gitignore
 │   │   ├── pipeline.log         # Execution logs
 │   │
 │   ├── tests/                   # Tests for pipeline validation
 │   │   ├── __init__.py          # Makes tests a package
 │   │   ├── test_fetch_data.py     # Test for fetch_data.py (GCS Extraction)
 │   │   ├── test_data_process.py   # Test for data_process.py (Transformation)
 │   │   ├── test_bias_detection.py # Test for bias_detection.py
 │   │   ├── test_pipeline.py       # Integration test for full ETL pipeline
 │   │   ├── test_schema.py         # Test for data schema validation (BigQuery)
 │   │   ├── test_dvc.py            # Test for DVC data versioning
 │   │   ├── test_airflow.py        # Test for Airflow DAG execution
 │
 ├── .github/workflows/             # CI/CD automation for testing
 │   ├── ci.yml                     # GitHub Actions workflow for local testing
 │   ├── ci-gcp.yml                  # GitHub Actions workflow for GCP testing
 │
 ├── docker-compose.yml           # Docker Compose file for container orchestration
 ├── Dockerfile                   # Docker setup for the project
 ├── requirements.txt              # Python dependencies
 ├── .gitignore                    # Ignore unnecessary files
 └── README.md                     # Documentation
```

## Reproducibility & Data Versioning

- ensure reproducibility, follow these steps:

1. Clone the repository and install dependencies: As described in the Environment Setup section.

2. Use DVC to version the data: The data files are versioned with DVC. Use DVC to pull the latest data when setting up the project:

    bash
    dvc pull

3. Re-run the pipeline: Once the environment is set up and dependencies installed, you can re-run the pipeline with:

    ```bash
    python scripts/sellerId_check.py


This will ensure that the data, code, and environment are consistent across different machines.

## Code Style & Guidelines

The code in this repository follows Python's PEP 8 guidelines for readability and consistency.

- *Modular Programming:* The code is divided into smaller, reusable functions for clarity and maintainability.
- *Naming Conventions:* Variables, functions, and classes use descriptive and consistent naming conventions as per PEP 8.
- *Documentation:* All functions and classes are documented with docstrings to explain their purpose and usage.

## Error Handling & Logging

The project includes error handling to ensure smooth execution and provide detailed logs for troubleshooting.

- *File Processing Errors:* If the JSONL data files are malformed or missing, the script will print warnings and skip those files.
- *Data Unavailability:* The pipeline checks if required columns like parent_asin are missing, and logs appropriate error messages.
- *Logging:* The project uses print statements to log progress, errors, and warnings. You can customize this to use a more advanced logging framework like logging for better control.

## Contributing

Contributions are welcome! If you want to improve the project, follow these steps:

1. Fork the repository.
2. Create a new branch for your changes.
3. Commit your changes.
4. Push your branch and create a pull request.
