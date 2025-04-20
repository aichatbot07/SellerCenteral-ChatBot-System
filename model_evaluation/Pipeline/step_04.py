import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main')))


from model_tracker import ModelTracker

def main():
    tracker = ModelTracker()  # Create an instance of the TestSetEvaluator class

    # Load the test set from the JSON file generated earlier
    bias_scores = tracker.load_json_file("bias-scores.json")
    
    metrics_scores = tracker.load_json_file("eval_metrics.json")
    tracker.log_bias_and_sentiment_metrics(bias_scores, metrics_scores)
    print("done")
    tracker.start_mlflow_ui(5000)


    
if __name__ == "__main__":
    main()