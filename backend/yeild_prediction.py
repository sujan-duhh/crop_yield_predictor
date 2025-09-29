from flask import Blueprint, request, jsonify
import joblib
import pandas as pd
import sys, os
from datetime import datetime

# ✅ Make sure api/ is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.Api_data import get_lat_lon, get_last7days_weather, get_soil_ph_and_type

# Create blueprint
yield_bp = Blueprint("yield", __name__)

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(BASE_DIR, "../models/yeild_prediction/results.csv")

# Load results
results_df = pd.read_csv(os.path.abspath(RESULTS_PATH), index_col=0)

# Find best model (lowest MSE)
best_model_name = results_df["MSE"].idxmin()
print(f"✅ Best yield model: {best_model_name}")

# Construct model path
MODEL_PATH = os.path.join(BASE_DIR, f"../models/yeild_prediction/{best_model_name.replace(' ', '_')}_pipeline.pkl")
MODEL_PATH = os.path.abspath(MODEL_PATH)

# Load trained pipeline
model = joblib.load(MODEL_PATH)

# Extract features from preprocessor
preprocessor = model.named_steps["preprocessor"]
FEATURES = []
for _, _, cols in preprocessor.transformers:
    if cols is not None:
        FEATURES.extend(cols)


@yield_bp.route("/", methods=["GET"])
def home():
    return {"message": "🌾 Crop Yield Predictor API is running!"}


@yield_bp.route("/features", methods=["GET"])
def features():
    return jsonify({"features": ["crop", "state_name", "dist_name", "area_in_acres"]})


@yield_bp.route("/predict", methods=["POST"])
def predict_yield():
    try:
        userinput = request.get_json()
        userinput_df = pd.DataFrame([userinput], columns=["crop", "state_name", "dist_name", "area_in_acres","soil_type"])
        print(userinput_df)
        # Fetch location
        lat_lon = get_lat_lon(userinput_df.loc[0, "state_name"], userinput_df.loc[0, "dist_name"])
        lat, lon = lat_lon["lat"], lat_lon["lon"]

        # Fetch weather + soil
        last7days_weather = get_last7days_weather(lat, lon)
        print("🔍 Weather data fetched:", last7days_weather)
        soil_data = get_soil_ph_and_type(lat, lon)
        print("🔍 Soil data fetched:", soil_data)

        # Load NPK dataset
        data_path = os.path.join(BASE_DIR, "sensor_Crop_Dataset.csv")
        dataset = pd.read_csv(data_path)

        
        npk_data = dataset[
            (dataset["Soil_Type"] == userinput_df.loc[0,"soil_type"].title()) &
            (dataset["Crop"] == userinput_df.loc[0, "crop"].title())
        ][["Nitrogen", "Phosphorus", "Potassium"]].mean()
        print("🔍 NPK data fetched:", npk_data)
        # Build model input
        df_input = pd.DataFrame(columns=FEATURES)
        df_input.loc[0, "year"] = int(datetime.now().year)
        df_input.loc[0, "temperature_c"] = int(last7days_weather["temperature"])
        df_input.loc[0, "humidity_%"] = last7days_weather["humidity"]
        df_input.loc[0, "rainfall_mm"] = last7days_weather["rainfall"]
        df_input.loc[0, "wind_speed_m_s"] = last7days_weather["windspeed"]
        df_input.loc[0, "solar_radiation_mj_m2_day"] = last7days_weather["solar_radiation"]
        df_input.loc[0, "crop"] = userinput_df.loc[0, "crop"]
        df_input.loc[0, "state_name"] = userinput_df.loc[0, "state_name"]
        df_input.loc[0, "dist_name"] = userinput_df.loc[0, "dist_name"]
        df_input.loc[0, "n_req_kg_per_ha"] = int(npk_data["Nitrogen"])
        df_input.loc[0, "p_req_kg_per_ha"] = int(npk_data["Phosphorus"])
        df_input.loc[0, "k_req_kg_per_ha"] = int(npk_data["Potassium"])
        df_input.loc[0, "area_ha"] = int(0.404686 * userinput_df.loc[0, "area_in_acres"])
        df_input.loc[0, "ph"] = soil_data["ph"]

        # Convert numerics
        for col in df_input.columns:
            df_input[col] = pd.to_numeric(df_input[col], errors="ignore")

        # Prediction
        prediction = model.predict(df_input)[0]

        # Show selected features back
        show_features = [
            "temperature_c", "humidity_%", "rainfall_mm", "wind_speed_m_s",
            "solar_radiation_mj_m2_day", "n_req_kg_per_ha", "p_req_kg_per_ha",
            "k_req_kg_per_ha", "ph"
        ]
        inputs_to_show = df_input[show_features].to_dict(orient="records")[0]

        return jsonify({
            "prediction": round(float(prediction), 2),
            "prediction_unit": "kg/acre",
            "total_prediction": round(float(prediction) * (userinput_df.loc[0, "area_in_acres"]), 2),
            "total_prediction_unit": "kg",
            "inputs_used": inputs_to_show
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400
