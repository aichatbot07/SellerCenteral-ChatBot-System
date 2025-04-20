import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main')))

from bias_detection import BiasDetection  # Import the BiasDetection class from Code 3


def main():
    bias = BiasDetection()  # Create an instance of the TestSetEvaluator class

    # Load the test set from the JSON file generated earlier
    bias.detect()
    


if __name__ == "__main__":
    main()