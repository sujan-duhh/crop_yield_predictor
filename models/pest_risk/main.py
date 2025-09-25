import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder

def get_preprocessors(X):
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()

    linear_preprocessor = ColumnTransformer(transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

    tree_preprocessor = ColumnTransformer(transformers=[
        ('num', 'passthrough', numeric_features),
        ('cat', OrdinalEncoder(handle_unknown="error"), categorical_features)
    ])

    return linear_preprocessor, tree_preprocessor

def load_and_preprocess_data(
    file_path=None, test_size=0.2, random_state=47
):
    # ✅ Resolve absolute path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if file_path is None:
        file_path = os.path.join(BASE_DIR, "./pest_risk_dataset.csv")

    # Load dataset
    df = pd.read_csv(file_path)

    # Features (X) and target (y)
    X = df.drop(columns=["Pest_Risk"])
    y = df["Pest_Risk"]

    # Preprocessors
    linear_preprocessor, tree_preprocessor = get_preprocessors(X)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    return X_train, X_test, y_train, y_test, linear_preprocessor, tree_preprocessor
