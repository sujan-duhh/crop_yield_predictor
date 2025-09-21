from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, BaggingRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

def get_models():
    """
    Returns models dict and linear models list
    """
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=200, random_state=47, n_jobs=-1),
        "XGBoost": XGBRegressor(n_estimators=500, learning_rate=0.05, max_depth=8, random_state=47, n_jobs=-1),
        "Bagging (Linear Regression)": BaggingRegressor(estimator=LinearRegression(), n_estimators=100, random_state=47, n_jobs=-1),
        "Bagging (Decision Tree)": BaggingRegressor(estimator=DecisionTreeRegressor(max_depth=None, random_state=47), n_estimators=100, random_state=47, n_jobs=-1)
    }

    linear_models = ["Linear Regression", "Bagging (Linear Regression)"]

    return models, linear_models
