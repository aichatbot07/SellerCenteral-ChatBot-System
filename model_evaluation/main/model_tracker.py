import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config')))
from config.config import logger, HF_TOKEN, OPENAI_API_KEY,DEEPSEEK_API_KEY,GROQ_API_KEY,LANGFUSE_PUBLIC_KEY,LANGFUSE_SECRET_KEY,LANGFUSE_HOST,GOOGLE_APPLICATION_CREDENTIALS
import mlflow
import logger
import json
import subprocess
import time

mlflow.set_experiment('bias_detection_experiment')

class ModelTracker():

    def log_bias_and_sentiment_metrics(self, bias_results, metrics):
        mlflow.set_experiment('evaluation_metrics_experiment')
        with mlflow.start_run():
            # Extract the metrics from the JSON data
            average_word_match = metrics.get("Average Word Match")
            average_semantic_similarity = metrics.get("Average Semantic Similarity")
            
            # Log metrics if they exist in the JSON data
            if average_word_match is not None:
                mlflow.log_metric("Average Word Match", average_word_match)
            
            if average_semantic_similarity is not None:
                mlflow.log_metric("Average Semantic Similarity", average_semantic_similarity)
        
        # Print logged metrics
        print(f"Logged metrics to MLflow: Average Word Match = {average_word_match}, Average Semantic Similarity = {average_semantic_similarity}")
        mlflow.set_experiment('bias_detection_experiment')
        with mlflow.start_run():
            for asin, result in bias_results.items():
                # Log Bias Detection Metrics
                mlflow.log_metric(f"{asin}_bias_detected_count", result['bias_detected_count'])
                mlflow.log_metric(f"{asin}_num_reviews", result['num_reviews'])
                
                # Log each bias type detected, if any
                for i, bias_type in enumerate(result['bias_types']):
                    mlflow.log_param(f"{asin}_bias_type_{i+1}", bias_type)
                
                # Log Sentiment Metrics
                sentiments = result['review_sentiments']
                mlflow.log_metric(f"{asin}_positive_sentiment", sentiments['positive'])
                mlflow.log_metric(f"{asin}_neutral_sentiment", sentiments['neutral'])
                mlflow.log_metric(f"{asin}_negative_sentiment", sentiments['negative'])

                # Optionally log any other relevant metrics
                mlflow.log_metric(f"{asin}_total_sentiments", sentiments['positive'] + sentiments['neutral'] + sentiments['negative'])

    def load_json_file(self, file_path):
    
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    
    def start_mlflow_ui(self, port=5000):
        """
        Starts the MLflow UI from Python and prints the URL in the terminal.
        
        Args:
        - port (int): The port to run the MLflow UI on (default is 5000).
        """
        # Command to start the MLflow UI
        command = f"mlflow ui --port {port}"

        # Start the MLflow UI in a subprocess
        process = subprocess.Popen(command, shell=True)

        # Wait a moment to ensure the UI starts
        time.sleep(2)

        # Print the URL in the terminal
        print(f"MLflow UI started at: http://localhost:{port}")

        # You can use process.communicate() or other methods to handle the process output if necessary
        return process



