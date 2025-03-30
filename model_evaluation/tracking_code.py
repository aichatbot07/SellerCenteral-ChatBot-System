import mlflow
import os

# Set remote MLflow tracking server
MLFLOW_TRACKING_URI = "http://your-mlflow-server:5000"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Define the experiment
mlflow.set_experiment("amazon-chatbot-experiments")

def log_chat_interaction(user_question, model_response, model_name, temperature):
    """Logs the user query and chatbot response in MLflow."""
    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("model", model_name)
        mlflow.log_param("temperature", temperature)

        # Log user question and chatbot response
        mlflow.log_text(user_question, "user_question.txt")
        mlflow.log_text(model_response, "model_response.txt")

        print(f"Logged chat interaction for model {model_name} at temp {temperature}")


