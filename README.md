# SellerCentral-ChatBot-System

## Project Overview

SellerCentral-ChatBot-System is a cloud-based conversational chatbot designed to assist e-commerce sellers with common queries and tasks. It provides an interactive question-answering service through a web API endpoint, allowing sellers to get instant support. The chatbot is deployed on **Google Cloud Platform (GCP)** using **Cloud Run**, which means it runs as a serverless containerized application. This design allows the chatbot to scale automatically based on demand without requiring manual server management ([Cloud Run | xMatters](https://www.xmatters.com/integration/google-cloud-run#:~:text=Google%20Cloud%20Run%20is%20a,almost%20instantaneously%20depending%20on%20traffic)). The project emphasizes *model deployment and monitoring* rather than model training – in fact, no model training or retraining is performed as part of this system. Instead, a pre-built or pre-trained model is integrated into the application and served to users. 


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


Key features of the SellerCentral-ChatBot-System include:

- **Stateless Chatbot API**: The chatbot logic (e.g., a machine learning model or rule-based system) is encapsulated in a container that responds to HTTP requests. This makes it easy to query the chatbot from any client (web, mobile, etc.) via simple HTTP calls.
- **Data-Driven Answers:** Fetches product **reviews and metadata** from a Google BigQuery database to ground its answers in real customer feedback.
- **Vector Similarity Search:** Converts reviews into embeddings using HuggingFace transformers ([GitHub - aichatbot07/SellerCenteral-ChatBot-System](https://github.com/aichatbot07/SellerCenteral-ChatBot-System#:~:text=,HuggingFace%20Transformers%20for%20embedding%20generation)) and indexes them with **FAISS** for efficient similarity search. This allows the bot to retrieve relevant snippets when a question is asked.
- **Conversational QA Chain:** Uses **LangChain** ([GitHub - aichatbot07/SellerCenteral-ChatBot-System](https://github.com/aichatbot07/SellerCenteral-ChatBot-System#:~:text=,HuggingFace%20Transformers%20for%20embedding%20generation)) to build a conversational Question-Answering chain. The bot combines the retrieved review data with a language model to generate an answer. It can handle follow-up questions by maintaining context (conversation history) in memory.
- **Evaluation and MLOps:** Includes scripts for evaluating retrieval quality (e.g. Precision@k, Recall@k) and answer quality (e.g. BLEU, ROUGE-L) to monitor performance. An offline data pipeline (using Apache Airflow and DVC for data versioning) is provided to ingest and preprocess data into BigQuery, ensuring the chatbot's knowledge base stays up-to-date.
- **Cloud Deployment**: By leveraging GCP Cloud Run, the chatbot benefits from high availability and automatic scaling. Cloud Run manages the underlying infrastructure, scaling the container instances up or down (even to zero) based on incoming traffic, which optimizes cost and performance ([Cloud Run | xMatters](https://www.xmatters.com/integration/google-cloud-run#:~:text=Google%20Cloud%20Run%20is%20a,almost%20instantaneously%20depending%20on%20traffic)).
- **Continuous Deployment**: The project uses a CI/CD pipeline with GitHub Actions to automatically build and deploy new versions of the chatbot. Every code update can be seamlessly rolled out to Cloud Run, ensuring that the live service is always up-to-date.
- **Monitoring & Logging**: The system implements basic model monitoring through logging. Each time the chatbot is started or handles a conversation, and whenever an error occurs, the event is logged. These logs are exported to **BigQuery** for analysis. By querying the logs, one can track metrics such as *how often the chatbot is invoked* and *how many errors occur over time*. This provides insights into usage patterns and system reliability.

In summary, SellerCentral-ChatBot-System is a **serverless chatbot application** with an emphasis on reliable deployment and monitoring. It is suitable for scenarios where an AI chatbot assists users (in this case, sellers) without the overhead of managing infrastructure or continuously retraining models.




## Deployment Architecture

The deployment architecture of the SellerCentral-ChatBot-System comprises several GCP services and integration points, as shown below:

- **Google Cloud Run (Service)** – Cloud Run hosts the chatbot application in a Docker container. It is a fully managed, serverless platform for running stateless containers triggered by web requests ([Cloud Run | xMatters](https://www.xmatters.com/integration/google-cloud-run#:~:text=Google%20Cloud%20Run%20is%20a,almost%20instantaneously%20depending%20on%20traffic)). The chatbot container is deployed to Cloud Run, allowing it to automatically scale with incoming traffic and scale down when idle. Cloud Run abstracts away server management, so we don't worry about VMs or Kubernetes clusters. The service is typically configured to allow public (unauthenticated) access, so that users can directly send requests to the chatbot’s HTTP endpoint. There is no separate model training component in the architecture; the model is loaded and served within this runtime container.

- **GitHub Actions (CI/CD Pipeline)** – The code repository (for example, on GitHub) is linked to an automated pipeline using GitHub Actions. Whenever new code is pushed to the repository (e.g., merged into the main branch), the CI/CD workflow triggers. The pipeline builds the Docker image for the chatbot, runs tests (if any), pushes the image to a container registry, and then deploys the new image to Cloud Run ([From Code to Cloud: GitHub Actions for Cloud Run Deployment | by Azeez | Medium](https://azeezz.medium.com/from-code-to-cloud-github-actions-for-cloud-run-deployment-dc1304573642#:~:text=Github%20Actions%20is%20a%20continuous,with%20a%20Service%20Account%20Key)) ([From Code to Cloud: GitHub Actions for Cloud Run Deployment | by Azeez | Medium](https://azeezz.medium.com/from-code-to-cloud-github-actions-for-cloud-run-deployment-dc1304573642#:~:text=machine%20,on%20the%20cloud%20run%20service)). This ensures continuous integration and deployment: any update to the chatbot’s code can be quickly rolled out to production without manual intervention. The GitHub Actions workflow uses Google Cloud’s official or community-provided actions to authenticate with GCP and execute the deployment commands.

- **Container Registry/Artifact Registry** – As part of deployment, the Docker image for the chatbot is stored in a registry. This could be Google Container Registry (GCR) or Artifact Registry. The CI pipeline builds the image and tags it (for example, with the Git commit or version), then pushes it to the registry. Cloud Run then pulls this image from the registry during deployment. The registry is Google-managed and requires proper authentication (handled by the CI workflow using GCP credentials).

- **Cloud Logging and BigQuery (Monitoring)** – Cloud Run services automatically send logs to Google Cloud Logging by default ([Logging and viewing logs in Cloud Run  |  Cloud Run Documentation  |  Google Cloud](https://cloud.google.com/run/docs/logging#:~:text=Cloud%20Run%20has%20two%20types,automatically%20sent%20to%20Cloud%20Logging)). In this architecture, a Cloud Logging **sink** is configured to export relevant logs to **BigQuery** in near real-time. Two custom metrics are tracked via log entries:
  - *Chatbot Started Count*: incremented/logged each time the chatbot application starts handling a new session or request (this could be for each new chat session or each invocation, depending on how it's instrumented).
  - *Chatbot Error Count*: incremented/logged whenever an error or exception occurs in the chatbot (for example, failure to process a message).
  
  The log sink filters the Cloud Run logs to capture these events and stores them in a BigQuery table for analysis. By exporting logs to BigQuery, we can run SQL queries to count occurrences of these events over time ([View logs routed to BigQuery  |  Cloud Logging  |  Google Cloud](https://cloud.google.com/logging/docs/export/bigquery#:~:text=This%20document%20explains%20how%20you,also%20describes%20the%20%20213)). This serves as a lightweight monitoring solution for usage (how many chats were started) and reliability (how many errors happened). Optionally, these logs could also be used to set up alerts or dashboards (for instance, using Data Studio or Cloud Monitoring by linking BigQuery data), but the core idea is that the metrics are **logged** and **queried** rather than using a complex monitoring system. All other application logs (like debug info or general audit logs) also reside in Cloud Logging and can be viewed via the Logs Explorer in GCP, but only the key metrics are routed to BigQuery for custom analysis.

**Note:** The architecture does not include a training or data pipeline because *no model training/retraining is involved*. The focus is on deploying the inference service (the chatbot) and monitoring its runtime behavior. All components (Cloud Run, Logging, BigQuery, etc.) are in the cloud, making the system highly available and maintainable with minimal on-premise requirements.




## Deployment setup
1. **Prerequisites and Environment Setup**:  
   - **Google Cloud Project**: Ensure you have access to a GCP project with billing enabled. Note the **Project ID** as it will be needed for deployment configuration. If you don't have a project, create one via the GCP Console. Also, enable the **Cloud Run API** and **BigQuery API** for this project (you can do this through the console or with `gcloud services enable run.googleapis.com bigquery.googleapis.com`).  
   - **Google Cloud SDK (gcloud CLI)**: Install the Google Cloud SDK to get the `gcloud` command-line tool ([Google Cloud CLI documentation](https://cloud.google.com/sdk/docs#:~:text=Google%20Cloud%20CLI%20documentation%20Quickstart%3A,CLI%20%C2%B7%20Managing%20gcloud)). This tool will be used for local testing or manual deployment. You can install it from Google’s documentation (for example, on Ubuntu or Mac, download the installer or use a package manager). After installation, run `gcloud init` and `gcloud auth login` to authenticate and set the default project.  
   - **Docker**: Install Docker on your local system if you plan to build or run the container image locally. Docker is required to build the container image that Cloud Run will execute. Verify that running `docker --version` works.  
   - **Source Code**: Clone the repository for SellerCentral-ChatBot-System to your local machine:  
     ```bash
     git clone https://github.com/your-username/SellerCentral-ChatBot-System.git
     cd SellerCentral-ChatBot-System
     ```  
     (Use the actual repository URL or path as appropriate). The repository should contain the application code, a Dockerfile, and configuration files including the GitHub Actions workflow.  
   - **Configuration**: Review any configuration files or environment variable templates (for example, a `.env.example` file) in the repository. Prepare a `.env` file or set environment variables as needed (for instance, API keys or other secrets the chatbot might require to function). Common variables might include `PORT` (Cloud Run sets this automatically, usually 8080), or any model-specific settings. These should be documented in the repo. 

2. **Authentication and Permissions Setup**:  
   Deploying to Cloud Run via GitHub Actions requires granting the pipeline access to your GCP project:
   - **Service Account**: Create a GCP Service Account that will be used by GitHub Actions. For example, in the GCP Console or using the gcloud CLI, create a service account (e.g., name it `github-deployer`). Grant this service account the necessary IAM roles:
     - *Cloud Run Admin* – allows deploying new revisions to Cloud Run.
     - *Cloud Run Service Agent* – (if not included in admin) allows managing Cloud Run services.
     - *Artifact Registry Writer* (or *Storage Object Admin* if using Container Registry) – allows pushing Docker images to your project's registry.
     - *BigQuery Data Editor* (optional, only if your deployment process or monitoring needs to create tables or write to BigQuery; reading logs doesn't require this, as logging will handle BigQuery writes).
     - *Service Account User* – if the GitHub Actions workflow will impersonate this service account, it might need this role on itself.
   - **Generate Key**: For the service account, create a JSON key (in the IAM & Admin > Service Accounts section, select your service account, and add a key). This will download a JSON credentials file. **Keep it secure** and do not commit it to your repo.
   - **GitHub Secrets**: In your GitHub repository settings, add the necessary secrets so the Actions workflow can authenticate:
     - `GCP_PROJECT_ID`: your Google Cloud project ID.
     - `GCP_SA_KEY`: the content of the service account JSON key (you can copy-paste the JSON or encode it as base64 as required by your workflow).
     - (Alternatively, you might use OpenID Connect Workload Identity Federation instead of a JSON key. In that case you'd configure `google-github-actions/auth@v2` with a workload identity provider. But using the JSON key is simpler to start with.)
   - **Permissions Confirmation**: Locally, you can also authenticate with GCP to test permissions. Run: `gcloud auth activate-service-account --key-file path/to/key.json --project YOUR_PROJECT_ID` to impersonate the service account, then try a dry-run deployment command (see next step) to ensure permissions are correct.

**3. Set Up GitHub Actions for CI/CD (Optional)**  
Instead of manual builds and deploys, you can rely on the included GitHub Actions workflow to automate this process on every code push. The repo’s workflow file is located at [`.github/workflows/ci.yml`](.github/workflows/ci.yml), and it already contains the steps to authenticate to Google Cloud, build the Docker image, push it, and deploy to Cloud Run (mirroring the manual steps above). To use this:

   - Go to your GitHub repository Settings -> Secrets (or Settings -> Actions -> Secrets and variables -> Repository secrets) and add a secret named `GOOGLE_APPLICATION_CREDENTIALS`. The value should be the **JSON content** of the Google Cloud service account key (that has permissions to deploy to Cloud Run). This is used by the workflow to authenticate (`google-github-actions/auth@v1`).
   - Open the `ci.yml` file and update the environment variables under `env:` if needed:
     - `PROJECT_ID` should be your GCP project ID.
     - `SERVICE` should be your desired Cloud Run service name (e.g., "sellerchatbot-api").
     - `REGION` should match where you want to deploy (e.g., "us-central1").
   - Ensure the Secret Manager on GCP has all the runtime secrets as discussed. The workflow uses `gcloud run deploy --set-secrets` just like the manual step, so it expects those secrets to exist in GCP. (If you prefer not to use Secret Manager, you'd have to modify the deploy command to use `--update-env-vars` with values stored in GitHub Secrets — not covered here for brevity and security considerations.)
   - Commit and push your changes. The GitHub Actions pipeline will trigger on push to the **main** branch by default (as specified by `on: push` to main in the workflow). You can monitor the progress in the Actions tab of your GitHub repo. If configured correctly, you should see steps for checkout, Google Cloud auth, Docker build/push, and Cloud Run deploy. A successful run means your new code is live on Cloud Run.

Using the CI/CD pipeline ensures that any update to your code repository will automatically roll out to the Cloud Run service, providing a robust continuous deployment mechanism.

**4. Test the Deployed Service (API)**  
After deployment, you should verify that the chatbot API is working. You can use `curl` from the command line to send a test request to the `/chat/` endpoint. The endpoint expects a POST request with a JSON body containing an `asin` (Amazon product ID) and a `question`. For example:

```bash
# Replace <CLOUD_RUN_URL> with your service URL from the deploy step
curl -X POST "<CLOUD_RUN_URL>/chat/" \
  -H "Content-Type: application/json" \
  -d '{
        "asin": "B0EXAMPLEASIN", 
        "question": "What do customers say about the battery life?"
      }'
```

If everything is set up correctly, the service will fetch the reviews for the product `B0EXAMPLEASIN` from BigQuery, run the QA chain, and return a JSON response with an answer. A typical successful response looks like:

```json
{
  "asin": "B0EXAMPLEASIN",
  "question": "What do customers say about the battery life?",
  "answer": "Many customers mention that the battery life lasts around 10 hours on a single charge, which they find satisfactory for daily use."
}
```

(The exact answer will depend on the content of your BigQuery reviews for that ASIN and the behavior of the language model. If the ASIN is not found in the database, you should get an appropriate message like "No review data found for the provided ASIN." as defined in the code.)

> **Tip:** You can also test the service from the GCP Console. In Cloud Run, click on your service and use the "Testing" tab to send a JSON request. Alternatively, tools like Postman or HTTPie can be used for testing the REST endpoint.


By following these steps, you will have the SellerCentral-ChatBot-System deployed on Cloud Run and confirmed that it's functional. Future updates can be deployed simply by pushing changes to the repository (triggering the CI/CD workflow again), making the process of maintaining the chatbot very convenient.



## Deployment Instructions
**1. Build the Docker Container Image**  
The repository includes a `Dockerfile` that defines the container environment. It is based on **Python 3.9 slim**, installs the Python dependencies from `requirements.txt`, and sets the entrypoint to Uvicorn serving the FastAPI app on port 8080 (see the `CMD ["uvicorn", "src.main:app", ...]` in the Dockerfile). You can build the image locally and push to Google Container Registry (GCR) or Artifact Registry:

- *Option A: Use Google Cloud Build (gcloud)* – This is the simplest method if you have the gcloud CLI:
  ```bash
  # from the root of the repository:
  gcloud config set project YOUR_GCP_PROJECT_ID
  gcloud builds submit --tag gcr.io/YOUR_GCP_PROJECT_ID/sellerchatbot:latest .
  ```
  This command will upload your code to Google Cloud and build it on GCP's infrastructure, then store the image in the GCR registry (`sellerchatbot` is an example image name; you can choose another name).

- *Option B: Build and push with Docker manually* – Ensure Docker is running locally, then:
  ```bash
  docker build -t gcr.io/YOUR_GCP_PROJECT_ID/sellerchatbot:latest .
  docker push gcr.io/YOUR_GCP_PROJECT_ID/sellerchatbot:latest
  ```
  This will build the image locally and push it to your GCP project's container registry. (You might need to run `gcloud auth configure-docker` once to allow Docker to push to gcr.io.)

**2. Deploy to Cloud Run (Manual via gcloud)**  
Once the container image is available in the registry, deploy it to Cloud Run:
```bash
gcloud run deploy sellerchatbot-api \
  --image gcr.io/YOUR_GCP_PROJECT_ID/sellerchatbot:latest \
  --platform managed --region us-central1 \
  --allow-unauthenticated \
  --service-account YOUR_SERVICE_ACCOUNT_EMAIL \
  --memory 4Gi --timeout 300s \
  --update-secrets "HF_TOKEN=HF_TOKEN:latest,DEEPSEEK_API_KEY=DEEPSEEK_API_KEY:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,GOOGLE_APPLICATION_CREDENTIALS=GOOGLE_APPLICATION_CREDENTIALS:latest"
```
In the above command:
  - `sellerchatbot-api` is the name of the Cloud Run service (you can name it differently).
  - `--platform managed --region us-central1` deploys to the specified region on the fully managed Cloud Run.
  - `--allow-unauthenticated` makes the service publicly accessible (no auth token needed to invoke).
  - `--service-account` sets the service to run as the service account we configured (replace `YOUR_SERVICE_ACCOUNT_EMAIL` with the email of the SA). This account's permissions will be used to access BigQuery and secrets.
  - `--update-secrets` attaches the secrets from Secret Manager as environment variables in the container. For example, `HF_TOKEN=HF_TOKEN:latest` means it will fetch the latest version of the Secret Manager secret named "HF_TOKEN" and set an env var `HF_TOKEN` with that value inside the container. Similarly for the other secrets including `GOOGLE_APPLICATION_CREDENTIALS` (which would provide the JSON credentials if needed). If you are using the service account identity for BigQuery, the `GOOGLE_APPLICATION_CREDENTIALS` secret may not be strictly required – Google’s ADC (Application Default Credentials) will use the service account's identity automatically. However, if your code explicitly expects a JSON key, providing it via secret ensures compatibility.

   *Note:* The memory (4Gi) and timeout (300s) settings can be adjusted based on the needs of the model (e.g., if embedding or QA chain is heavy). Ensure your Cloud Run service account has access to the specified secrets (Secret Manager will enforce IAM).

After running the deploy, Cloud Run will output the service URL (something like `https://sellerchatbot-api-<randomhash>-uc.a.run.app`). You can also retrieve the URL with:
```bash
gcloud run services describe sellerchatbot-api --region us-central1 --format "value(status.url)"
```


## CI/CD Pipeline

The continuous integration/continuous delivery pipeline is implemented with **GitHub Actions**, enabling automated builds, tests, and deployment on every code change. Here’s an overview of the CI/CD setup and how it works:

- **Workflow Configuration**: The repository contains a workflow file (e.g., `.github/workflows/deploy.yml`) that defines the CI/CD process. This YAML file specifies triggers and a series of jobs/steps. For this project, the workflow is triggered on updates to the main branch (for example, on every push to `main` or when a pull request is merged). It may also allow manual triggers for deployment via the GitHub Actions interface if configured with `workflow_dispatch`. The trigger configuration ensures that the latest code is automatically deployed, achieving true continuous delivery.

- **Build and Test Stages**: Once triggered, the workflow runs on a GitHub-provided runner (Ubuntu VM by default). Typical stages in the job include:
  - *Checkout Code*: Uses `actions/checkout@v4` to pull the repository code onto the runner.
  - *Set up Cloud SDK*: Uses the Google Cloud action `google-github-actions/setup-gcloud` to install the gcloud CLI and authenticate. The service account credentials (from the `GCP_SA_KEY` secret) are used here to log in to GCP within the runner environment. After this, `gcloud` commands and other Google Cloud tools can be used.
  - *Build Docker Image*: The workflow builds the Docker image for the chatbot. It might do this with a Docker action or simply by running `docker build` in a script step. This compiles the application and packages it into a container image. If there are tests, this stage could also run unit tests (e.g., if using a Python app, maybe running `pytest` before building or as part of the build).
  - *Push to Registry*: After building, it logs in to Google’s container registry (using stored credentials or the gcloud auth) and pushes the image. The image tag might be `latest` or based on the commit SHA or a version number.
  - *Deploy to Cloud Run*: Finally, the workflow calls `gcloud run deploy` (or uses the `google-github-actions/deploy-cloudrun` action) to update the Cloud Run service with the new image. This step will replace the existing service revision with a new one carrying the updated code. By the end of this step, Cloud Run will serve the new version of the chatbot. The output of this action is often the service URL and confirmation of a successful deployment.

- **Continuous Deployment Behavior**: Thanks to this pipeline, developers do not need to manually intervene for deploying changes. For example, if a developer fixes a bug or adds a new feature to the chatbot and pushes a commit, within a few minutes the GitHub Actions workflow will build and release that change to Cloud Run. This reduces deployment friction and errors since the process is scripted and consistent. It also encourages frequent, incremental updates. If a build or deploy fails (due to a code issue or infrastructure problem), the GitHub Actions UI will show a failure, and the team can address it before it affects the production service.

- **Security and Credentials**: The CI/CD setup keeps sensitive information (like GCP credentials) in GitHub Secrets, not in the code. Only the GitHub Actions runner can access these secrets during a run. This protects the GCP account from unauthorized access. Additionally, using least-privilege principles for the service account (only giving it deploy permissions) ensures the CI/CD pipeline cannot perform unintended operations.

- **Rollback Strategy**: Although not explicitly part of the question, it’s worth noting: Cloud Run retains previous revisions of the service. In case a deployment has issues, one can quickly roll back to the last known good revision via the Cloud Run console or CLI. The CI pipeline could also be configured to only deploy on passing tests or incorporate manual approval for production, depending on how critical the application is. However, for this chatbot, we assume fully automated deployments for speed.

In summary, the CI/CD pipeline uses GitHub Actions to seamlessly integrate code changes with deployment. This follows industry best practices for DevOps, where code commits trigger builds and deployments in a reproducible manner ([From Code to Cloud: GitHub Actions for Cloud Run Deployment | by Azeez | Medium](https://azeezz.medium.com/from-code-to-cloud-github-actions-for-cloud-run-deployment-dc1304573642#:~:text=Github%20Actions%20is%20a%20continuous,with%20a%20Service%20Account%20Key)). The result is that maintaining and updating the SellerCentral-ChatBot-System is efficient and reliable, with minimal downtime and human error.


## Monitoring and Logging

Monitoring the chatbot’s performance and usage is crucial for ensuring reliability. In this project, we implement monitoring primarily through logging. The approach is to log key events from the application and then use those logs to derive metrics. Here's how it works and how you can utilize it:

- **Cloud Run Logging**: Out of the box, Cloud Run streams all logs from the application to **Google Cloud Logging** (formerly Stackdriver Logging). This includes two types of logs: **request logs** (each HTTP request has an entry with response code, latency, etc.) and **application logs** (any `stdout` or `stderr` output from the app) ([Logging and viewing logs in Cloud Run  |  Cloud Run Documentation  |  Google Cloud](https://cloud.google.com/run/docs/logging#:~:text=Cloud%20Run%20has%20two%20types,automatically%20sent%20to%20Cloud%20Logging)). Our chatbot application is instrumented to log specific events:
  - When the chatbot starts handling a new chat session or question, it logs a message like “Chatbot session started” (with perhaps a timestamp or session ID).
  - If an error or exception occurs (for example, if the model fails to generate a response or an internal error happens), the code logs an error message like “Chatbot error: <error details>”.
  - (Optionally, we could log other info such as the user’s question or the response time, but the key metrics of interest are start counts and error counts.)

- **Log-based Metrics in BigQuery**: Instead of using Cloud Monitoring’s custom metrics, we opted to export logs to **BigQuery** for analysis. A logging **sink** is configured in Cloud Logging that matches our chatbot’s logs and routes them to a BigQuery dataset. This means that every time a log entry is written (e.g., "Chatbot session started"), it is also appended as a row in a BigQuery table. Google’s logging service streams the data in small batches efficiently ([View logs routed to BigQuery  |  Cloud Logging  |  Google Cloud](https://cloud.google.com/logging/docs/export/bigquery#:~:text=This%20document%20explains%20how%20you,also%20describes%20the%20%20213)). In BigQuery, the logs can be queried using SQL, which provides a flexible way to calculate metrics over any time period:
  - **Chatbot Started Count**: You can count the number of "start" logs to see how many times the chatbot was invoked. For example, a simple BigQuery SQL query might be:  
    ```sql
    SELECT DATE(timestamp) as date, COUNT(*) as sessions
    FROM `your_project.logging_dataset.chatbot_logs`
    WHERE textPayload CONTAINS "Chatbot session started"
    GROUP BY date
    ORDER BY date;
    ```  
    This would give you daily counts of chatbot sessions started. (The exact field names like `textPayload` or schema depends on how the logs are structured in BigQuery, but generally the message appears in one of the payload fields).
  - **Chatbot Error Count**: Similarly, you can count error logs. For example:  
    ```sql
    SELECT DATE(timestamp) as date, COUNT(*) as errors
    FROM `your_project.logging_dataset.chatbot_logs`
    WHERE textPayload CONTAINS "Chatbot error"
    GROUP BY date
    ORDER BY date;
    ```  
    This yields the number of errors logged each day. If you join or compare the two metrics, you can calculate an error rate (errors per session) as well.

- **Viewing Logs and Metrics**: To inspect logs directly, you have a few options:
  - Use the **Cloud Run Logs** tab in the Google Cloud Console (navigate to Cloud Run service, then Logs). This is handy for recent logs or debugging specific issues.
  - Use **Cloud Logging Logs Explorer** for advanced filtering (you can filter by severity, or search for the text "Chatbot error" etc., across all logs).
  - Use **BigQuery**: go to the BigQuery console, find the dataset (for example, it might be named `chatbot_logs` or part of a logging dataset with your project ID), and you can query it or even just preview the table. BigQuery is particularly useful for aggregating metrics over time as shown in the examples above. Since the logs are stored in BigQuery, you could also connect a dashboard tool (e.g., Google Data Studio/Looker Studio) to visualize these metrics over time, if desired.

- **Alerting (Optional)**: While not explicitly set up in this project, you could create alerts in Cloud Monitoring based on these metrics. For instance, a **logs-based metric** could be defined in Cloud Monitoring to count "Chatbot error" occurrences and trigger an alert if the count exceeds a threshold in a given period. Alternatively, since data is in BigQuery, one could schedule a query or use an external script to monitor and send notifications. Given the scope of this project, we focus on manual monitoring via queries rather than automated alerts.

- **BigQuery Cost Consideration**: Exporting logs to BigQuery has cost implications (storage and query costs). However, for a moderate volume of logs (e.g., a chatbot with light usage), the cost is minimal. Logs in BigQuery allow long-term retention and complex analysis which Cloud Logging alone might limit (Cloud Logging also has retention limits depending on settings). It's a trade-off for the educational scenario to demonstrate custom monitoring. In a real production scenario, one might use Cloud Monitoring dashboards or export logs to a more purpose-built monitoring system if needed.

By reviewing the BigQuery logs, one can determine how frequently the chatbot is used and how stable it is (via error counts). For instance, if the "chatbot started" count suddenly drops to zero on a given day, it might indicate an outage or deployment issue. If the "error count" spikes, it signals something is wrong in responses or system performance. This logging-based monitoring provides a feedback loop to improve the chatbot system over time.


## Local Development and Testing

For development and testing purposes, you may want to run the chatbot system locally. This allows you to debug issues and run the pipeline without deploying to the cloud each time. Below are instructions for setting up a local dev environment and running tests:

**1. Setting up the environment:**  
Clone the repository to your local machine:
```bash
git clone https://github.com/aichatbot07/SellerCenteral-ChatBot-System.git
cd SellerCenteral-ChatBot-System
```
Ensure you have **Python 3.9+** installed. It's recommended to use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # (On Windows: venv\Scripts\activate)
```
Install the required Python packages:
```bash
pip install -r requirements.txt
```
This will install FastAPI, Uvicorn, google-cloud-bigquery, langchain, faiss-cpu, and other dependencies.

**2. Configuration:**  
For local testing, you'll need access to BigQuery and the various API keys just like in production. The simplest approach is to set environment variables on your machine for all the keys (HF_TOKEN, OPENAI_API_KEY, etc.). You can do this by creating a `.env` file or exporting variables in your shell. Also, you need to authenticate to Google Cloud for BigQuery access:
- Obtain your Google Cloud service account JSON key (the same one used in deployment, or any account with BigQuery read access).
- Set the environment variable to point to it:
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account.json"
  ```
  This will allow the BigQuery client to find the credentials. Alternatively, use `gcloud auth application-default login` to use your own account for BigQuery access in dev (not recommended for production, but fine for a quick test).

**3. Running the API server locally:**  
You can start the FastAPI server (Uvicorn) locally to test the chatbot:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
```
The `--reload` flag makes the server auto-restart on code changes (useful during development). Once it’s running, open a browser or use curl to test:
```
curl -X POST "http://localhost:8080/chat/" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B0TESTASIN", "question": "Sample question?"}'
```
If you have the BigQuery access configured properly and the ASIN exists in your data, you should get a JSON response from the local server. You can add print statements or use a debugger to step through the code in `src/chatbot_model.py` or other modules to inspect behavior.

**4. Running the Data Pipeline (optional):**  
The repository contains a `Data_pipeline/` directory with scripts (and Airflow DAGs) that presumably take raw data (like JSONL files of reviews) and load them into BigQuery, perform preprocessing, bias detection, etc. If you want to regenerate or update the BigQuery data, you can run these scripts. For example:
```bash
python Data_pipeline/dags/fetch_data.py       # Fetch raw data (perhaps from an API or file)
python Data_pipeline/dags/data_process.py     # Process/clean the raw data
python Data_pipeline/dags/bias_detection.py   # (Optional) detect biases in data
python Data_pipeline/dags/dataflow_processing.py  # Additional processing, maybe using Dataflow
python Data_pipeline/dags/sellerId_check.py   # Validate or augment data with seller IDs
python Data_pipeline/dags/mlops_airflow.py    # Integrate with Airflow (if using Airflow scheduler)
```
These are just the names of scripts; refer to the code/comments in those files for details on usage. If you have **Apache Airflow** installed, you can instead use the Airflow UI to run the pipeline as a DAG (there is an Airflow YAML in `.github/workflows/airflow_pipeline.yml` which might relate to running Airflow in CI). For local simplicity, direct Python execution or using DVC is sufficient:
   - The project supports **DVC (Data Version Control)** for data tracking. If DVC is set up, you might pull sample data using `dvc pull` (if a remote is configured; check for `.dvc` files).
   - Ensure any paths or project IDs inside these scripts match your setup (for example, the BigQuery dataset name).

**5. Running Tests:**  
Under the `tests/` directory, there may be unit tests for certain components (for instance, `tests/test_pipeline.py`). You can run the test suite with:
```bash
pytest tests/
```
Make sure you have any necessary test fixtures or environment variables set so that tests can run (the test code may be expecting a certain environment or sample data). The tests will help verify that individual pieces like the data pipeline or retrieval functions are working as expected.

**6. Iterating locally:**  
You can freely modify the code (for example, tweak the prompt for the LangChain QA chain, or try a different embedding model) and test it locally. Once satisfied, you can push changes to GitHub to trigger the CI/CD and deploy them.


---

## **Technologies Used**
- [Streamlit](https://streamlit.io/) for the user interface.
- [Google BigQuery](https://cloud.google.com/bigquery) for data storage and querying.
- [LangChain](https://langchain.com/) for building conversational AI pipelines.
- [FAISS](https://faiss.ai/) for vector-based document retrieval.
- [HuggingFace Transformers](https://huggingface.co/) for embedding generation.

---


## Code Style & Guidelines

The code in this repository follows Python's PEP 8 guidelines for readability and consistency.

- *Modular Programming:* The code is divided into smaller, reusable functions for clarity and maintainability.
- *Naming Conventions:* Variables, functions, and classes use descriptive and consistent naming conventions as per PEP 8.
- *Documentation:* All functions and classes are documented with docstrings to explain their purpose and usage.


## **Contributing**
Contributions are welcome! If you'd like to contribute to this project:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

---
