import pickle
import pandas as pd

# Load model and encoders
with open("irrigation_model.pkl", "rb") as f:
    model, label_encoders, target_encoder = pickle.load(f)


def predict_irrigation(crop_name, growth_stage, soil_type, soil_ph,
                       water_holding_capacity, temperature, humidity,
                       rainfall_last_7_days, rainfall_forecast_next_7_days,
                       water_availability, source_of_water, field_slope, area_acres):
    
    # Prepare input as DataFrame
    input_data = pd.DataFrame([{
        "crop_name": crop_name,
        "growth_stage": growth_stage,
        "soil_type": soil_type,
        "soil_ph": soil_ph,
        "water_holding_capacity": water_holding_capacity,
        "temperature": temperature,
        "humidity": humidity,
        "rainfall_last_7_days": rainfall_last_7_days,
        "rainfall_forecast_next_7_days": rainfall_forecast_next_7_days,
        "water_availability": water_availability,
        "source_of_water": source_of_water,
        "field_slope": field_slope,
        "area_acres": area_acres
    }])

    # Apply label encoding to categorical columns
    for col, le in label_encoders.items():
        if col in input_data.columns:
            input_data[col] = le.transform(input_data[col])

    # Predict irrigation method
    prediction = model.predict(input_data)[0]
    predicted_irrigation = target_encoder.inverse_transform([prediction])[0]

    return predicted_irrigation


if __name__ == "__main__":
    irrigation_method = predict_irrigation(
        crop_name="rice",
        growth_stage="flowering",
        soil_type="clay",
        soil_ph=6.5,
        water_holding_capacity="high",
        temperature=28.0,
        humidity=70.0,
        rainfall_last_7_days=120.0,
        rainfall_forecast_next_7_days=200.0,
        water_availability="abundant",
        source_of_water="rain-fed",
        field_slope="gentle",
        area_acres=1.5
    )

    print("Recommended Irrigation Method:", irrigation_method)
