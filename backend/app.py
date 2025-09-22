from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os
import logging
from .api_data import get_weather_data, get_agromonitoring_data

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

# 🔹 Path to trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../Random_Forest_pipeline.pkl")

# Load trained pipeline
try:
    model = joblib.load(MODEL_PATH)
    preprocessor = model.named_steps["preprocessor"]
    FEATURES = preprocessor.get_feature_names_out().tolist()
    logging.info("Model pipeline loaded successfully.")
    logging.info(f"Expected features: {FEATURES}")
except FileNotFoundError:
    logging.error(f"Model file not found at {MODEL_PATH}")
    model = None
    FEATURES = []
except Exception as e:
    logging.error(f"Error loading model pipeline: {e}")
    model = None
    FEATURES = []

@app.route("/")
def home():
    if model:
        return {"message": "🌾 Crop Yield Predictor API is running!"}
    else:
        return {"message": "🌾 Crop Yield Predictor API is running, but model is not loaded."}, 500

@app.route("/features", methods=["GET"])
def features():
    return jsonify({"features": FEATURES})

@app.route("/predict", methods=["POST"])
def predict():
    if not model:
        return jsonify({"error": "Model is not available. Please check server logs."}), 500
    
    try:
        data = request.get_json()
        
        # 🔹 Extract latitude and longitude from the request
        lat = data.get("lat")
        lon = data.get("lon")

        if not lat or not lon:
            return jsonify({"error": "Latitude and longitude are required."}), 400

        # 🔹 Automatically fetch weather and soil data
        agromonitoring_data = get_agromonitoring_data(lat, lon)
        if not agromonitoring_data:
            return jsonify({"error": "Could not fetch necessary data from AgroMonitoring API."}), 500

        # 🔹 Combine fetched data with user input
        # Note: We assume the user's model features include the data fetched from the API.
        combined_data = {**data, **agromonitoring_data}
        
        # Remove lat and lon from the combined data as they are not model features
        combined_data.pop("lat", None)
        combined_data.pop("lon", None)
        
        # Create a DataFrame with the combined data
        df_input = pd.DataFrame([combined_data])

        # Ensure columns are in the correct order as expected by the model
        df_input = df_input.reindex(columns=FEATURES, fill_value=0)

        logging.info(f"Input for prediction: {df_input.to_dict(orient='records')}")

        prediction = model.predict(df_input)[0]
        return jsonify({"prediction": round(float(prediction), 2)})
    
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
