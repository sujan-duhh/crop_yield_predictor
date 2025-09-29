from flask import Blueprint, request, jsonify
import pickle
import pandas as pd
import os
import sys

# Create blueprint
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.Api_data import get_lat_lon, get_last7days_weather, get_soil_ph_and_type, get_future_rainfall

irrigation_bp = Blueprint("irrigation", __name__)

# ✅ Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../models/irrigation_techniques/irrigation_model.pkl")
MODEL_PATH = os.path.abspath(MODEL_PATH)

print("Loading irrigation model from:", MODEL_PATH)

# Load model + encoders
with open(MODEL_PATH, "rb") as f:
    model, label_encoders, target_encoder = pickle.load(f)

# ✅ Soil → Water holding capacity mapping
soil_water_capacity = {
    "clay": "high",
    "loamy": "medium",
    "peaty": "medium",
    "saline": "medium",
    "sandy": "low",
    "silt": "medium"
}

# 🔹 Suggestion logic for irrigation method
def generate_irrigation_suggestion(method, crop, weather, soil, future_rainfall, area):
    method = method.lower()

    if method == "rain-fed":
        return (
            f"🌧 Predicted method: RAIN-FED. Suitable if rainfall remains consistent. "
            f"Since forecast rainfall is {future_rainfall} mm, monitor closely. "
            f"For {crop}, ensure soil type ({soil['soil_type']}) retains enough water "
            f"(capacity: {soil_water_capacity.get(soil['soil_type'].lower(), 'medium')})."
        )

    elif method == "drip":
        return (
            f"💧 Predicted method: DRIP irrigation. Recommended for efficient water use. "
            f"Good choice for {crop}, especially under current temperature {weather['temperature']}°C "
            f"and humidity {weather['humidity']}%. Helps save water in {area} acres field."
        )

    elif method == "sprinkler":
        return (
            f"🌱 Predicted method: SPRINKLER irrigation. Useful for lighter soils like {soil['soil_type']} "
            f"and crops sensitive to uniform watering. With rainfall forecast {future_rainfall} mm, "
            f"sprinkler ensures even distribution."
        )

    elif method == "furrow":
        return (
            f"🚜 Predicted method: FURROW irrigation. Works well for row crops and moderate slopes. "
            f"Soil water capacity is {soil_water_capacity.get(soil['soil_type'].lower(), 'medium')}. "
            f"Consider runoff if slope is high."
        )

    else:
        return (
            f"ℹ️ Predicted irrigation method is {method.upper()}. "
            f"Ensure compatibility with soil ({soil['soil_type']}) and local water availability."
        )


@irrigation_bp.route("/", methods=["GET"])
def home():
    return {"message": "💧 Irrigation Recommendation API is running!"}


@irrigation_bp.route("/predict", methods=["POST"])
def predict_irrigation():
    try:
        data = request.get_json()
        print("Received data:", data)

        # Step 1: Get location (lat, lon)
        lat_lon = get_lat_lon(data.get("state"), data.get("district"))
        lat, lon = lat_lon["lat"], lat_lon["lon"]

        # Step 2: Get last 7 days weather
        weather = get_last7days_weather(lat, lon)

        # Step 3: Get soil data
        soil_data = get_soil_ph_and_type(lat, lon)
        print("Soil data:", soil_data)

        # Step 4: Future rainfall
        future_rainfall = get_future_rainfall(lat, lon)

        # ✅ Clean soil type before encoding
        raw_soil_type = soil_data.get("soil_type", "").lower()
        if raw_soil_type in ["unknown", "", None]:
            soil_type = "loamy"   # fallback default
        else:
            soil_type = raw_soil_type

        # ✅ Assign water holding capacity
        water_capacity = soil_water_capacity.get(soil_type, "medium")

                # Prepare input dataframe
        input_data = pd.DataFrame([{
            "crop_name": data.get("crop_name"),
            "growth_stage": data.get("growth_stage", "").lower(),
            "soil_type": data.get("soil_type", soil_type).lower(),
            "soil_ph": float(soil_data["ph"]),
            "water_holding_capacity": water_capacity,
            "temperature": float(weather["temperature"]),
            "humidity": float(weather["humidity"]),
            "rainfall_last_7_days": float(weather["rainfall"]),
            "rainfall_forecast_next_7_days": float(future_rainfall),   # ✅ force float
            "water_availability": data.get("water_availability"),
            "source_of_water": data.get("source_of_water"),
            "field_slope": data.get("field_slope"),
            "area_acres": float(data.get("area_acres", 0)),           # ✅ force float
        }])


        print("Cleaned input before encoding:\n", input_data)

        # ✅ Safe label encoding
        for col, le in label_encoders.items():
            if col in input_data.columns:
                input_data[col] = input_data[col].apply(
                    lambda val: val if val in le.classes_ else le.classes_[0]
                )
                input_data[col] = le.transform(input_data[col])

        # 🔮 Predict
        prediction = model.predict(input_data)[0]
        irrigation_method = target_encoder.inverse_transform([prediction])[0]

        # Probabilities
        prediction_proba_raw = model.predict_proba(input_data)[0]
        prediction_proba = {
            method: round(prob, 3)
            for method, prob in zip(target_encoder.classes_, prediction_proba_raw)
        }

        # Generate suggestion
        suggestion = generate_irrigation_suggestion(
            irrigation_method,
            data.get("crop_name"),
            weather,
            soil_data,
            future_rainfall,
            data.get("area_acres")
        )

        return jsonify({
            "irrigation_method": str(irrigation_method),
            "suggestion": str(suggestion),
            "temperature": float(weather["temperature"]),
            "humidity": float(weather["humidity"]),
            "rainfall_last_7_days": float(weather["rainfall"]),
            "rainfall_forecast_next_7_days": float(future_rainfall),
            "soil_type": str(soil_type),
            "soil_ph": float(soil_data["ph"]),
            "water_holding_capacity": str(water_capacity),
            "inputs_used": {
                **data,
                "soil_type": str(soil_type),
                "soil_ph": float(soil_data["ph"]),
                "water_holding_capacity": str(water_capacity)
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

