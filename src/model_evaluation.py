import os
import pandas as pd
import numpy as np
import joblib
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from fairlearn.metrics import MetricFrame
from fairlearn.postprocessing import ThresholdOptimizer
import shap
import lime
import lime.lime_tabular

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# ---------- Load Processed Data ----------
def load_data(file_path="data/processed_data.csv"):
    """Load preprocessed data for model validation."""
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded dataset with shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return None

# ---------- Split Data ----------
def split_data(df, target_column="sentiment_label"):
    """Splits dataset into training and validation sets."""
    X = df.drop(columns=[target_column])  # Features
    y = df[target_column]  # Target variable

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    logger.info(f"Data split complete. Training size: {X_train.shape}, Test size: {X_test.shape}")
    
    return X_train, X_test, y_train, y_test

# ---------- Load Trained Model ----------
def load_model(model_path="models/best_model.pkl"):
    """Load trained ML model."""
    try:
        model = joblib.load(model_path)
        logger.info("Model loaded successfully.")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

# ---------- Model Evaluation Metrics ----------
def evaluate_model(model, X_test, y_test):
    """Evaluates the trained model on test data."""
    y_pred = model.predict(X_test)
    
    metrics = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred, average="weighted"),
        "Recall": recall_score(y_test, y_pred, average="weighted"),
        "F1 Score": f1_score(y_test, y_pred, average="weighted"),
        "AUC": roc_auc_score(y_test, model.predict_proba(X_test), multi_class="ovr")
    }

    logger.info("Model Evaluation Metrics:")
    for metric, value in metrics.items():
        logger.info(f"{metric}: {value:.4f}")

    # Generate classification report
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # Confusion Matrix
    plot_confusion_matrix(y_test, y_pred)

    return metrics

# ---------- Confusion Matrix Visualization ----------
def plot_confusion_matrix(y_test, y_pred):
    """Plots confusion matrix for model evaluation."""
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=np.unique(y_test), yticklabels=np.unique(y_test))
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    plt.show()

# ---------- Feature Importance Analysis (SHAP & LIME) ----------
def feature_importance_analysis(model, X_test):
    """Performs feature importance analysis using SHAP and LIME."""
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)

        # SHAP Summary Plot
        shap.summary_plot(shap_values, X_test)

        # LIME Explanation
        lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=X_test.values,
            feature_names=X_test.columns.tolist(),
            class_names=["Negative", "Neutral", "Positive"],
            mode="classification"
        )
        exp = lime_explainer.explain_instance(X_test.iloc[0].values, model.predict_proba)
        exp.show_in_notebook()
        
        logger.info("Feature importance analysis completed.")
    except Exception as e:
        logger.error(f"Error in feature importance analysis: {e}")

# ---------- Bias Detection Using Fairlearn ----------
def detect_bias(model, X_test, y_test, sensitive_column="Category"):
    """
    Detects bias in the model across different slices of the dataset.
    """
    if sensitive_column not in X_test.columns:
        logger.warning(f"Sensitive column '{sensitive_column}' not found in dataset.")
        return

    y_pred = model.predict(X_test)

    # Fairlearn metric frame
    metric_frame = MetricFrame(
        metrics={"Accuracy": accuracy_score, "F1 Score": f1_score},
        y_true=y_test,
        y_pred=y_pred,
        sensitive_features=X_test[sensitive_column]
    )

    # Display metrics across slices
    print("Bias Detection Across Slices:\n", metric_frame.by_group)

    # Visualizing Bias
    metric_frame.by_group.plot(kind="bar", title="Bias Detection Across Slices")
    plt.show()

    logger.info("Bias detection analysis completed.")

# ---------- Threshold Adjustment for Fairness ----------
def mitigate_bias(model, X_test, y_test, sensitive_column="Category"):
    """Applies Fairlearn's Threshold Optimizer to adjust decision boundaries."""
    if sensitive_column not in X_test.columns:
        logger.warning(f"Sensitive column '{sensitive_column}' not found in dataset.")
        return

    threshold_optimizer = ThresholdOptimizer(
        estimator=model,
        constraints="demographic_parity",
        predict_method="predict_proba"
    )

    threshold_optimizer.fit(X_test, y_test, sensitive_features=X_test[sensitive_column])
    y_pred_adjusted = threshold_optimizer.predict(X_test, sensitive_features=X_test[sensitive_column])

    # Evaluate fairness-adjusted model
    adjusted_metrics = {
        "Accuracy": accuracy_score(y_test, y_pred_adjusted),
        "F1 Score": f1_score(y_test, y_pred_adjusted, average="weighted"),
    }

    logger.info("Bias mitigation applied. Updated Metrics:")
    for metric, value in adjusted_metrics.items():
        logger.info(f"{metric}: {value:.4f}")

# ---------- Main Execution ----------
if __name__ == "__main__":
    # Load Data
    df = load_data()
    if df is None:
        exit()

    # Split Data
    X_train, X_test, y_train, y_test = split_data(df)

    # Load Model
    model = load_model()
    if model is None:
        exit()

    # Evaluate Model
    metrics = evaluate_model(model, X_test, y_test)

    # Feature Importance Analysis
    feature_importance_analysis(model, X_test)

    # Bias Detection
    detect_bias(model, X_test, y_test)

    # Bias Mitigation (Optional)
    mitigate_bias(model, X_test, y_test)
