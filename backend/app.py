from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os
from Api_data import get_weather_data,get_lat_lon,get_last7days_weather,get_soil_ph_and_type
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Load results (from training step)
results_df = pd.read_csv(os.path.join(os.path.dirname(__file__), "../results.csv"), index_col=0)

# Find best model (lowest MSE)
best_model_name = results_df['MSE'].idxmin()
print(f"✅ Best model: {best_model_name}")

# Construct path of the best model .pkl file
MODEL_PATH = os.path.join(os.path.dirname(__file__), f"../{best_model_name.replace(' ', '_')}_pipeline.pkl")

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
    return jsonify({"features": ["crop","state_name","dist_name","area_in_acres"]})

@app.route("/predict", methods=["POST"])
def predict():
    try:
        userinput = request.get_json()
        userinput_df=pd.DataFrame([userinput],columns=["crop","state_name","dist_name","area_in_acres"])
        
        # Wrap into DataFrame
        
        lat_lon=get_lat_lon(userinput_df.loc[0,"state_name"],userinput_df.loc[0,"dist_name"])
        print(lat_lon)
        lat=lat_lon["lat"]
        lon=lat_lon["lon"]
        print(lat,lon)

        weather_data=get_weather_data(lat,lon)
        print(weather_data)

        last7days_weather = get_last7days_weather(lat,lon)

        soil_data = get_soil_ph_and_type(lat,lon)
        print(soil_data)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATA_PATH = os.path.join(BASE_DIR, "data", "sensor_Crop_Dataset.csv")

        dataset = pd.read_csv(DATA_PATH)

        npk_data = dataset[(dataset["Soil_Type"]==soil_data["soil_type"]) & (dataset["Crop"]==userinput_df.loc[0,"crop"].title())][["Nitrogen","Phosphorus","Potassium"]].mean()
        print(type(npk_data))

        df_input =pd.DataFrame(columns=FEATURES)
        df_input.loc[0,"year"]=int(datetime.now().year)
        df_input.loc[0,"temperature_c"]=int(last7days_weather["temperature"])
        df_input.loc[0,"humidity_%"]=last7days_weather["humidity"]
        df_input.loc[0,"rainfall_mm"]=last7days_weather["rainfall"]
        df_input.loc[0,"wind_speed_m_s"]=last7days_weather["windspeed"]
        df_input.loc[0,"solar_radiation_mj_m2_day"]=last7days_weather["solar_radiation"]
        df_input.loc[0,"crop"]=userinput_df.loc[0,"crop"]
        df_input.loc[0,"state_name"]=userinput_df.loc[0,"state_name"]
        df_input.loc[0,"dist_name"]=userinput_df.loc[0,"dist_name"]
        df_input.loc[0,"n_req_kg_per_ha"]=int(npk_data["Nitrogen"])
        df_input.loc[0,"p_req_kg_per_ha"]=int(npk_data["Phosphorus"])   
        df_input.loc[0,"k_req_kg_per_ha"]=int(npk_data["Potassium"])
        df_input.loc[0,"area_ha"]=int((0.404686)*(userinput_df.loc[0,"area_in_acres"]))
        df_input.loc[0,"ph"]=soil_data["ph"]
        

        # Convert numeric fields where possible
        for col in df_input.columns:
            df_input[col] = pd.to_numeric(df_input[col], errors="ignore")

        # Debug: log received data
        print("Received input:", df_input.to_dict(orient="records"))

        # Make prediction
        prediction = model.predict(df_input)[0]
        show_features = ["temperature_c", "humidity_%", "rainfall_mm", "wind_speed_m_s",
                 "solar_radiation_mj_m2_day", "n_req_kg_per_ha", "p_req_kg_per_ha",
                 "k_req_kg_per_ha","ph"]

        inputs_to_show = df_input[show_features].to_dict(orient="records")[0]

        return jsonify({
            "prediction": round(float(prediction), 2),
            "prediction_unit": "kg/acre",
            "total_prediction": round(float(prediction) * (userinput_df.loc[0, "area_in_acres"]), 2),
            "total_prediction_unit": "kg",
            "inputs_used": inputs_to_show   # ✅ send df_input subset
        })
    except Exception as e:
        print("Error:", str(e))  # Debug log
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
