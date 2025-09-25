from flask import Blueprint, request, jsonify
import joblib
import pandas as pd
import os, sys

# ✅ Make sure api/ is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.Api_data import get_lat_lon, get_last7days_weather, get_soil_ph_and_type

# Create blueprint
fertilizer_bp = Blueprint("fertilizer", __name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
MODEL_PATH = os.path.join(BASE_DIR, "../models/fertilizer_recommendation/Fertilizer_pipeline.pkl")
MODEL_PATH = os.path.abspath(MODEL_PATH)

print("Loading fertilizer model from:", MODEL_PATH)

# Load model + encoders
bundle = joblib.load(MODEL_PATH)
pipeline = bundle["pipeline"]
crop_encoder = bundle["crop_encoder"]
fertilizer_encoder = bundle["fertilizer_encoder"]

# ---------------- Fertilizer Expansions ----------------
fertilizer_map = {
    "Urea": "Urea (Nitrogen-rich fertilizer)",
    "DAP": "Diammonium Phosphate (Phosphorus-based fertilizer)",
    "MOP": "Muriate of Potash (Potassium-based fertilizer)",
    "SSP": "Single Super Phosphate (Sulphur & Phosphorus)",
    "Ammonium Sulphate": "Ammonium Sulphate (Nitrogen & Sulphur)",
    "Compost": "Organic Compost (Improves soil health)",
}

# ---------------- Advisory Function ----------------
def fertilizer_advisory(n, p, k, predicted_fertilizer, crop):
    fert_full = fertilizer_map.get(predicted_fertilizer, predicted_fertilizer)
    suggestion = f"For your {crop} crop, the recommended fertilizer is {fert_full}. Using this will help balance your soil nutrients and improve your yield. "

    # Nitrogen logic
    if n < 50:
        suggestion += "Your Nitrogen level is low, so this fertilizer will help improve leaf growth. "
    elif n > 100:
        suggestion += "Nitrogen is already high, so apply cautiously to avoid over-fertilization. "

    # Phosphorus logic
    if p < 50:
        suggestion += "Phosphorus is low, which can affect root development. This recommendation helps balance it. "
    elif p > 100:
        suggestion += "Phosphorus is on the higher side, so avoid extra P-based fertilizers. "

    # Potassium logic
    if k < 50:
        suggestion += "Potassium is low, which may reduce crop quality. This fertilizer supports fruit/seed formation. "
    elif k > 100:
        suggestion += "Potassium is already sufficient, so apply in moderation. "

    return suggestion.strip()

# ---------------- Route ----------------
@fertilizer_bp.route("/predict", methods=["POST"])
def predict_fertilizer():
    try:
        # Get JSON request data
        data = request.get_json()

        # Get location
        lat_lon = get_lat_lon(data.get("state"), data.get("district"))
        lat, lon = lat_lon["lat"], lat_lon["lon"]

        # Fetch weather + soil data
        last7days_weather = get_last7days_weather(lat, lon)
        soil_data = get_soil_ph_and_type(lat, lon)

        # ✅ Extract only N, P, K, crop
        sample = {
            "N": data.get("N"),
            "P": data.get("P"),
            "K": data.get("K"),
            "crop": data.get("crop"),
            "temperature": int(last7days_weather["temperature"]),
            "humidity": int(last7days_weather["humidity"]),
            "ph": int(soil_data["ph"]),
            "rainfall": int(last7days_weather["rainfall"]),
        }

        # Encode crop
        sample["crop_encoded"] = crop_encoder.transform([sample["crop"]])[0]

        # Convert to DataFrame
        X_new = pd.DataFrame([[
            sample["N"], sample["P"], sample["K"],
            sample["temperature"], sample["humidity"],
            sample["ph"], sample["rainfall"], sample["crop_encoded"]
        ]], columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall", "crop_encoded"])

        # Prediction
        pred = pipeline.predict(X_new)[0]
        fertilizer = fertilizer_encoder.inverse_transform([pred])[0]
        fertilizer_full = fertilizer_map.get(fertilizer, fertilizer)

        # Probabilities
        prediction_proba_raw = pipeline.predict_proba(X_new)[0]
        prediction_proba = {
            fert: round(prob, 3)
            for fert, prob in zip(fertilizer_encoder.classes_, prediction_proba_raw)
        }

        # Advisory suggestion
        suggestion = fertilizer_advisory(sample["N"], sample["P"], sample["K"], fertilizer, sample["crop"])

        return jsonify({
            "fertilizer": fertilizer,
            "fertilizer_full": fertilizer_full,
            "prediction_proba": prediction_proba,
            "suggestion": suggestion,
            "temperature": sample["temperature"],
            "humidity": sample["humidity"],
            "ph": sample["ph"],
            "rainfall": sample["rainfall"],
            "crop": sample["crop"],
            "state": data.get("state"),
            "district": data.get("district")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400
