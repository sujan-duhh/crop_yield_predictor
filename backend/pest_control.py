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
    temp = weather.get("temperature")
    hum = weather.get("humidity")
    rain = weather.get("rainfall")
    ph = soil.get("ph")

    if risk == "low":
        return (
            f"✅ Pest risk is LOW for {crop} at {growth_stage} stage. "
            f"Continue regular monitoring. Current conditions (T={temp}°C, H={hum}%, Rain={rain}mm) "
            f"are generally unfavorable for major pest outbreaks."
        )

    elif risk == "moderate" or risk == "medium":  # handle both words
        return (
            f"⚠️ Pest risk is MODERATE for {crop} at {growth_stage} stage. "
            f"Watch leaves and stems closely. You may consider organic repellents (e.g., neem spray). "
            f"Soil pH={ph}, Rainfall={rain}mm, and Humidity={hum}% could support some pest activity."
        )

    elif risk == "high":
        # Build reasons
        reasons = []
        if hum is not None:
            if hum > 70:
                reasons.append(f"high humidity ({hum}%)")
            elif hum < 40:
                reasons.append(f"low humidity ({hum}%)")
        if rain is not None:
            if rain > 50:
                reasons.append(f"heavy rainfall ({rain}mm)")
            elif rain < 10:
                reasons.append(f"low rainfall ({rain}mm)")
        reason_text = " and ".join(reasons) if reasons else "current weather conditions"

        return (
            f"❌ Pest risk is HIGH for {crop} at {growth_stage} stage. "
            f"Immediate monitoring is required. The risk is mainly due to {reason_text}. "
            f"Consult an agri expert and apply recommended pesticides."
        )

    elif risk == "very high":
        return (
            f"🚨 Pest risk is VERY HIGH for {crop} at {growth_stage} stage! "
            f"Urgent action is needed. Weather (T={temp}°C, H={hum}%, Rain={rain}mm) "
            f"and soil pH={ph} create extremely favorable conditions for pest outbreak. "
            f"Consult experts immediately and apply strong preventive/control measures."
        )

    else:
        return (
            f"ℹ️ Pest risk level '{prediction}' could not be interpreted clearly. "
            f"Please verify your inputs or consult your local agricultural officer."
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
        soil_type = user_data.get("soil_type").title()

        # Step 1: Get location (lat, lon)
        lat_lon = get_lat_lon(state, district)
        lat, lon = lat_lon["lat"], lat_lon["lon"]

        # Step 2: Get last 7 days weather
        weather = get_last7days_weather(lat, lon)

        # Step 3: Get soil data
        soil_data = get_soil_ph_and_type(lat, lon)
        print(soil_data)
        # Step 4: Build final model input
        

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
            "soil_type": soil_type,
            "inputs_used": X_new.to_dict(orient="records")[0],
            "state": state,
            "district": district
        })

    except Exception as e:
        print("❌ Error in pest prediction:", str(e))
        return jsonify({"error": str(e)}), 400
