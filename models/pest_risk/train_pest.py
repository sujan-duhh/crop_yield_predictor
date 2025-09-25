import os
import joblib
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pandas as pd

from main import load_and_preprocess_data

# ✅ Base directory (this script’s location)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR)
RESULTS_DIR = os.path.join(MODEL_DIR)

# Create dirs if not exist


# Load data & preprocessors
X_train, X_test, y_train, y_test, linear_preprocessor, tree_preprocessor = load_and_preprocess_data()

# Define RandomForest model
rf_model = RandomForestClassifier(
    n_estimators=200,
    random_state=47,
    class_weight="balanced"
)

# Create pipeline with tree_preprocessor
pipeline = Pipeline([
    ("preprocessor", tree_preprocessor),
    ("model", rf_model)
])

# Train model
pipeline.fit(X_train, y_train)

# Predictions
y_pred = pipeline.predict(X_test)

# Evaluation
accuracy = accuracy_score(y_test, y_pred)
class_report = classification_report(y_test, y_pred, output_dict=True)
conf_matrix = confusion_matrix(y_test, y_pred)

print("✅ Random Forest Classifier Results")
print("Accuracy:", accuracy)
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", conf_matrix)

# ✅ Save trained pipeline (absolute path)
MODEL_PATH = os.path.join(MODEL_DIR, "PestRisk_RFClassifier_pipeline.pkl")
joblib.dump(pipeline, MODEL_PATH)
print(f"📂 Model saved at: {MODEL_PATH}")

# Example predictions
sample_input = X_test.iloc[:5]
print(sample_input)
print("\n🔍 Sample Predictions:")
print(pipeline.predict(sample_input))

# ✅ Save results to CSV (absolute path)
RESULTS_PATH = os.path.join(RESULTS_DIR, "results.csv")
results_df = pd.DataFrame(class_report).T
results_df.loc["overall_accuracy"] = [accuracy, None, None, None]  # add accuracy row
results_df.to_csv(RESULTS_PATH, index=True)
print(f"📂 Results saved at: {RESULTS_PATH}")
