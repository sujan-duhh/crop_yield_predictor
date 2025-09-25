import os, joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from data import load_and_preprocess   # ✅ using data.py

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load dataset + encoders
df, crop_encoder, fertilizer_encoder = load_and_preprocess()

# Features + target
X = df[["N", "P", "K", "temperature", "humidity", "ph", "rainfall", "crop_encoded"]]
y = df["fertilizer_encoded"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Pipeline: scaling + model
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", RandomForestClassifier(n_estimators=200, random_state=42))
])

# Train
pipeline.fit(X_train, y_train)

# Evaluate
y_pred = pipeline.predict(X_test)
acc = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred, target_names=fertilizer_encoder.classes_)

print("✅ Accuracy:", acc)
print(report)

# Save results to CSV
results_path = os.path.join(BASE_DIR, "results.csv")
pd.DataFrame({"accuracy": [acc]}).to_csv(results_path, index=False)

# Save ONE .pkl with everything
SAVE_PATH = os.path.join(BASE_DIR, "Fertilizer_pipeline.pkl")
joblib.dump({
    "pipeline": pipeline,
    "crop_encoder": crop_encoder,
    "fertilizer_encoder": fertilizer_encoder
}, SAVE_PATH)

print(f"📦 Model + encoders saved at {SAVE_PATH}")
