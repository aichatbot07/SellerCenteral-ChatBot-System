import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main')))

from evaluation import TestSetEvaluator  # Import the TestSetEvaluator class from Code 2

def main():
    evaluator = TestSetEvaluator()  # Create an instance of the TestSetEvaluator class

    # Load the test set from the JSON file generated earlier
    test_set = evaluator.load_test_set("rag_test_set.json")

    # Evaluate the test set to calculate metrics
    metrics = evaluator.evaluate_test_set(test_set)
    evaluator.save_results(metrics, "eval_metrics.json")

    # Print the evaluation metrics
    print("Evaluation Results:")  
    print(metrics)

if __name__ == "__main__":
    main()
