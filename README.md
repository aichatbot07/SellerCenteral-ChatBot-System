# SellerCenteral-ChatBot-System
Here’s the complete content for your `README.md` file, formatted for easy readability and ready to be copy-pasted:

---

# **Seller Central AI Chatbot**

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
