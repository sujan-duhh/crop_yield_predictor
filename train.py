import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from models import model
from data import data,preproc

# Load dataset
X,y = data.load_dataset()

# Get preprocessors and models
linear_preprocessor, tree_preprocessor = preproc.get_preprocessors(X)
models, linear_models = model.get_models()

results = {}

for name, model in models.items():
    preprocessor = linear_preprocessor if name in linear_models else tree_preprocessor
    pipeline = Pipeline([('preprocessor', preprocessor), ('model', model)])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=47)
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    results[name] = {
        'MSE': mean_squared_error(y_test, y_pred),
        'R2': r2_score(y_test, y_pred)
    }

    # Save trained pipeline for later use
    joblib.dump(pipeline, f"{name.replace(' ', '_')}_pipeline.pkl")

print(pd.DataFrame(results).T)
