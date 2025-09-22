from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# 🔹 Path to trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../Random_Forest_pipeline.pkl")

# Load trained pipeline
model = joblib.load(MODEL_PATH)

# 🔹 Extract features directly from preprocessor
preprocessor = model.named_steps["preprocessor"]
FEATURES = []
for name, transformer, cols in preprocessor.transformers:
    if cols is not None:
        FEATURES.extend(cols)

@app.route("/")
def home():
    return {"message": "🌾 Crop Yield Predictor API is running!"}

@app.route("/features", methods=["GET"])
def features():
    return jsonify({"features": FEATURES})

@app.route("/predict", methods=["POST"])
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        df_input = pd.DataFrame([data])

        # Convert numeric fields safely
        for col in df_input.columns:
            df_input[col] = pd.to_numeric(df_input[col], errors="ignore")

        print("Received input:", df_input.to_dict(orient="records"))  # Debug

        prediction = model.predict(df_input)[0]
        return jsonify({"prediction": round(float(prediction), 2)})
    except Exception as e:
        print("Error:", str(e))  # Debug
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
