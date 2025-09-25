import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from ml_models import get_models
from preproc import get_preprocessors
from data import load_dataset

# Load dataset
X,y = load_dataset()

# Get preprocessors and models
linear_preprocessor, tree_preprocessor = get_preprocessors(X)
models, linear_models = get_models()

results = {}

for name, ml_models in models.items():
    preprocessor = linear_preprocessor if name in linear_models else tree_preprocessor
    pipeline = Pipeline([('preprocessor', preprocessor), ('model', ml_models)])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=47)
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    results[name] = {
        'MSE': mean_squared_error(y_test, y_pred),
        'R2': r2_score(y_test, y_pred)
    }

    # Save trained pipeline for later use
    joblib.dump(pipeline, f"{name.replace(' ', '_')}_pipeline.pkl")

# Convert results dict → DataFrame
results_df = pd.DataFrame(results).T

# Find model with lowest MSE
best_model_name = results_df['MSE'].idxmin()
print(f"✅ Best model: {best_model_name}")
print(results_df.loc[best_model_name])

# Load the corresponding trained pipeline
import joblib
best_model = joblib.load(f"{best_model_name.replace(' ', '_')}_pipeline.pkl")

# Now you can use it for predictions
sample_input = X_test.iloc[:5]   # example input
print(best_model.predict(sample_input))
print(pd.DataFrame(results).T)
pd.DataFrame(results).T.to_csv("results.csv")