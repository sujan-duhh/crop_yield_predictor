from flask import Blueprint, request, jsonify
import joblib
import pandas as pd
import os, sys
from datetime import datetime

# Make sure api/ is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.Api_data import get_lat_lon, get_last7days_weather, get_soil_ph_and_type

# Create Blueprint
pest_bp = Blueprint("pest_control", __name__)

# ✅ Absolute model path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../models/pest_risk/PestRisk_RFClassifier_pipeline.pkl")
MODEL_PATH = os.path.abspath(MODEL_PATH)

print("🔍 Loading Pest Risk model from:", MODEL_PATH)

# Load trained pipeline
pipeline = joblib.load(MODEL_PATH)


# 🔹 Suggestion logic based on pest risk prediction
def generate_pest_suggestion(prediction, crop, growth_stage, weather, soil):
    risk = prediction.lower()

    if risk == "low":
        return (
            f"✅ Pest risk is LOW for {crop} at {growth_stage} stage. "
            f"Continue regular field monitoring. Favorable weather (T={weather['temperature']}°C, "
            f"H={weather['humidity']}%) may still attract minor pests, but no major action needed."
        )

    elif risk == "medium":
        return (
            f"⚠️ Pest risk is MODERATE for {crop} at {growth_stage} stage. "
            f"Keep a close watch on leaves and stems. Consider using organic pest repellents or neem spray "
            f"as preventive measures, especially since soil pH is {soil['ph']} and rainfall is {weather['rainfall']} mm."
        )

    elif risk == "high":
        return (
            f"❌ Pest risk is HIGH for {crop} at {growth_stage} stage. "
            f"Immediate monitoring is required. Recommended to consult a local agri expert and consider "
            f"appropriate pesticide application. Weather conditions (high humidity {weather['humidity']}% "
            f"and {weather['rainfall']} mm rainfall) increase the chance of pest outbreak."
        )

    else:
        return (
            f"ℹ️ Pest risk level could not be determined clearly. "
            f"Please cross-check inputs or consult your local agricultural officer."
        )


@pest_bp.route("/predict", methods=["POST"])
def predict_pest_risk():
    try:
        # Get JSON request data
        user_data = request.get_json()
        print("🔍 User Input received:", user_data)

        # Required inputs
        crop = user_data.get("Crop")
        variety = user_data.get("Variety")
        growth_stage = user_data.get("Growth_Stage")
        print(growth_stage)
        state = user_data.get("State")
        district = user_data.get("District")

        # Step 1: Get location (lat, lon)
        lat_lon = get_lat_lon(state, district)
        lat, lon = lat_lon["lat"], lat_lon["lon"]

        # Step 2: Get last 7 days weather
        weather = get_last7days_weather(lat, lon)

        # Step 3: Get soil data
        soil_data = get_soil_ph_and_type(lat, lon)
        print(soil_data)
        # Step 4: Build final model input
        soil_type = soil_data.get("soil_type", "Loamy")  # fallback
        soil_type = soil_data.get("soil_type", "Loamy")  # fallback
        if soil_type.lower() == "unknown" or soil_type is None:
                soil_type = "Loamy"  # or whichever is most common in your training data

        X_new = pd.DataFrame([{
                "Crop": crop.title(),
                "Variety": variety.title(),
                "Growth_Stage": growth_stage,
                "Soil_Type": soil_type,
                "pH_Value": soil_data["ph"],
                "Temperature": weather["temperature"],
                "Humidity": weather["humidity"],
                "Rainfall": weather["rainfall"]
            }])



        print("✅ Final Model Input:", X_new)

        # Step 5: Predict
        prediction = pipeline.predict(X_new)[0]

        # Probabilities mapped to class labels
        prediction_proba_raw = pipeline.predict_proba(X_new)[0]
        prediction_proba = {
            label: round(prob, 3)
            for label, prob in zip(pipeline.classes_, prediction_proba_raw)
        }

        # Step 6: Generate suggestion
        suggestion = generate_pest_suggestion(prediction, crop, growth_stage, weather, soil_data)

        # Step 7: Return JSON
        return jsonify({
            "prediction": str(prediction),
            "prediction_proba": prediction_proba,
            "suggestion": suggestion,
            "temperature": weather["temperature"],
            "humidity": weather["humidity"],
            "rainfall": weather["rainfall"],
            "ph": soil_data["ph"],
            "soil_type": soil_data["soil_type"],
            "inputs_used": X_new.to_dict(orient="records")[0],
            "state": state,
            "district": district
        })

    except Exception as e:
        print("❌ Error in pest prediction:", str(e))
        return jsonify({"error": str(e)}), 400
