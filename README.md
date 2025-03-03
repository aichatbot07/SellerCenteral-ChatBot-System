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
    ```pip install -r requirements.txt
