import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier
import numpy as np
import pickle


import os

# Get the base directory (folder where this script is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build absolute path to the dataset
DATA_PATH = os.path.join(BASE_DIR, "./Irrigation_Recommendation_Dataset.csv")  # adjust filename if needed
DATA_PATH = os.path.abspath(DATA_PATH)  # resolve to full path

print("Loading dataset from:", DATA_PATH)

# Read CSV
df = pd.read_csv(DATA_PATH)



label_encoders = {}
for col in df.select_dtypes(include=['object']).columns:
    if col != 'irrigation_method':
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le

target_encoder = LabelEncoder()
df['irrigation_method'] = target_encoder.fit_transform(df['irrigation_method'])

X = df.drop(columns=['irrigation_method'])
y = df['irrigation_method']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

class_counts = y_train.value_counts().to_dict()
total = sum(class_counts.values())
num_classes = len(class_counts)
class_weights = {cls: total / (num_classes * count) for cls, count in class_counts.items()}
weights = y_train.map(class_weights)

param_dist = {
    "n_estimators": [200, 300, 400],
    "max_depth": [4, 6, 8, 10],
    "learning_rate": [0.01, 0.05, 0.1, 0.2],
    "subsample": [0.6, 0.8, 1.0],
    "colsample_bytree": [0.6, 0.8, 1.0],
    "min_child_weight": [1, 3, 5],
    "gamma": [0, 0.1, 0.2]
}

xgb = XGBClassifier(
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1
)

random_search = RandomizedSearchCV(
    estimator=xgb,
    param_distributions=param_dist,
    n_iter=20,  
    scoring="f1_macro",  
    cv=3,
    verbose=2,
    random_state=42,
    n_jobs=-1
)

random_search.fit(X_train, y_train, sample_weight=weights)

print("Best Parameters:", random_search.best_params_)
print("Best Macro F1 Score (CV):", random_search.best_score_)

best_model = random_search.best_estimator_
best_model.fit(X_train, y_train, sample_weight=weights)

y_pred = best_model.predict(X_test)
print("\n Test Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # folder where script is
MODEL_PATH = os.path.join(BASE_DIR, "irrigation_model.pkl")  # save in same folder
MODEL_PATH = os.path.abspath(MODEL_PATH)

with open(MODEL_PATH, "wb") as f:
    pickle.dump((best_model, label_encoders, target_encoder), f)

print("Saved as irrigation_model.pkl")
