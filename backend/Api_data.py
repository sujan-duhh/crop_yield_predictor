import pandas as pd
import numpy as np
import os
import requests
import json
import logging
import time
from datetime import datetime,timedelta,UTC

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import requests
import pandas as pd

# --- Load local dataset once ---
DATASET_PATH = "sensor_Crop_Dataset.csv"
try:
    local_data = pd.read_csv(DATASET_PATH)
except Exception:
    local_data = pd.DataFrame()

# --- Mapping WRB → Dataset Soil Types ---
SOIL_MAPPING = {
    "Vertisols": "Clay",
    "Luvisols": "Clay",
    "Cambisols": "Clay",
    "Fluvisols": "Silt",
    "Arenosols": "Sandy",
    "Leptosols": "Sandy",
    "Solonchaks": "Saline",
    "Histosols": "Peaty",
    "Phaeozems": "Loamy",
    "Chernozems": "Loamy",
    "Kastanozems": "Loamy"
}

def map_soil_type(wrb_class_name):
    return SOIL_MAPPING.get(wrb_class_name, "Unknown")

def get_soil_from_dataset(soil_type=None, crop=None):
    """Fallback: fetch avg soil pH using soil_type + crop"""
    if local_data.empty:
        return {"ph": 7.0, "soil_type": soil_type or "Unknown", "wrb_class": None}
    
    df = local_data.copy()
    if soil_type:
        df = df[df["soil_type"].str.lower() == soil_type.lower()]
    if crop and not df.empty:
        df = df[df["crop"].str.lower() == crop.lower()]

    if df.empty:
        ph_val = local_data["ph"].mean() if "ph" in local_data else 7.0
        soil_type_val = soil_type or "Unknown"
    else:
        ph_val = df["ph"].mean() if "ph" in df else 7.0
        soil_type_val = df["soil_type"].mode()[0] if "soil_type" in df else (soil_type or "Unknown")

    return {"ph": round(ph_val, 2), "soil_type": soil_type_val, "wrb_class": None}

def get_soil_ph_and_type(lat, lon, crop=None):
    """Main API function: fetch soil pH + type from ISRIC → fallback to dataset"""
    try:
        # --- Fetch soil pH ---
        ph_url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lat={lat}&lon={lon}&property=phh2o"
        ph_resp = requests.get(ph_url, timeout=10).json()

        ph = None
        try:
            layers = ph_resp.get("properties", {}).get("layers", [])
            if layers:
                ph_layer = layers[0]["depths"][0]
                ph_val = ph_layer["values"].get("mean", None)
                ph = ph_val / 10.0 if ph_val else None
        except Exception:
            ph = None

        # --- Fetch soil type ---
        type_url = f"https://rest.isric.org/soilgrids/v2.0/classification/query?lat={lat}&lon={lon}"
        type_data = requests.get(type_url, timeout=10).json()

        wrb_class = type_data.get("wrb_class_name", None)
        soil_type = map_soil_type(wrb_class) if wrb_class else None

        # --- If API failed → fallback to dataset ---
        if ph is None or soil_type is None:
            return get_soil_from_dataset(soil_type=soil_type, crop=crop)

        return {"ph": round(ph, 2), "soil_type": soil_type, "wrb_class": wrb_class}

    except Exception:
        # Full fallback if API fails
        return get_soil_from_dataset(soil_type=None, crop=crop)


def get_last7days_weather(lat, lon):
    """
    Fetch last 7 days weather & solar radiation (MJ/m²/day) from NASA POWER API.
    Returns aggregated weekly features with all values as means.
    """
    today = datetime.now()
    end = (datetime.now(UTC) - timedelta(days=2)).strftime("%Y%m%d")
    start = (datetime.now(UTC) - timedelta(days=9)).strftime("%Y%m%d")
    print(start,end)

    url = (
    f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,RH2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN,WS2M&community=AG&latitude={lat}&longitude={lon}&start={start}&end={end}&format=JSON"
    )

    print(url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()["properties"]["parameter"]

        # Convert to DataFrame
        df = pd.DataFrame({k: v for k, v in data.items()})
        df.index = pd.to_datetime(list(data["T2M"].keys()))  # dates
        df = df.astype(float)
        df = df.replace(-999.0, np.nan)

        # Aggregate (7-day mean for everything)
        agg = {
            "temperature": df["T2M"].mean(skipna=True),                   # °C
            "humidity": df["RH2M"].mean(skipna=True),                     # %
            "rainfall": df["PRECTOTCORR"].mean(skipna=True),              # mm/day
            "solar_radiation": df["ALLSKY_SFC_SW_DWN"].mean(skipna=True), # MJ/m²/day
            "windspeed": df["WS2M"].mean(skipna=True),                    # m/s
        }
        return agg

    except Exception as e:
        logging.error(f"Error fetching NASA POWER data: {e}")
        return None

def get_lat_lon(state: str, district: str, country: str = "India"):
    query = f"{district}, {state}, {country}"
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }

    try:
        headers = {"User-Agent": "geo-tester"}  # Required by Nominatim
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if len(data) > 0:
            result = data[0]
            return {
                "lat": float(result["lat"]),
                "lon": float(result["lon"])
            }
        else:
            return None
    except Exception as e:
        print("Error:", e)
        return None


# Example usage
print(get_lat_lon("Maharashtra", "Nagpur"))
print(get_lat_lon("Telangana", "Hyderabad"))


def get_weather_data(lat, lon):
    """
    Fetches weather data from OpenWeatherMap API for a given location.
    
    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        
    Returns:
        dict: A dictionary containing temperature, humidity, and rainfall data,
              or None if an error occurs.
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        logging.error("OpenWeatherMap API key not found in environment variables.")
        return None

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        
        # Rainfall data might not always be available
        rainfall = data.get("rain", {}).get("1h", 0)
        windspeed = data.get("wind",{}).get("speed",None)
        return {
            "temperature": temp,
            "humidity": humidity,
            "rainfall": rainfall,
            "windspeed": windspeed
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        return None
    except KeyError as e:
        logging.error(f"Missing key in weather data response: {e}")
        return None


def get_agromonitoring_data(lat, lon):
    """
    Fetches weather history (last 7 days) and soil data from AgroMonitoring API.
    """
    api_key = os.getenv("AGROMONITORING_API_KEY")
    if not api_key:
        logging.error("AgroMonitoring API key not found in environment variables.")
        return None

    # Use current time and go 7 days back
    end = int(time.time())
    start = end - 7 * 24 * 60 * 60  # 7 days ago

    weather_url = (
        f"https://api.agromonitoring.com/agro/1.0/weather/history"
        f"?lat={lat}&lon={lon}&start={start}&end={end}&appid={api_key}"
    )
    soil_url = (
        f"https://api.agromonitoring.com/agro/1.0/soil?lat={lat}&lon={lon}&appid={api_key}"
    )

    try:
        weather_res = requests.get(weather_url, timeout=10)
        weather_res.raise_for_status()
        weather_data = weather_res.json()

        soil_res = requests.get(soil_url, timeout=10)
        soil_res.raise_for_status()
        soil_data = soil_res.json()

        # Extract relevant info (use latest weather record if available)
        if weather_data:
            last_weather = weather_data[-1]
            temp = last_weather.get("main", {}).get("temp")
            humidity = last_weather.get("main", {}).get("humidity")
        else:
            temp, humidity = None, None

        soil_moisture = soil_data.get("main", {}).get("soil_moisture")
        soil_temp = soil_data.get("main", {}).get("soil_temp")

        return {
            "temperature": temp,
            "humidity": humidity,
            "soil_moisture": soil_moisture,
            "soil_temp": soil_temp,
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching AgroMonitoring data: {e}")
        return None
    except (IndexError, KeyError) as e:
        logging.error(f"Missing key in AgroMonitoring response: {e}")
        return None


def get_satellite_data(lat, lon):
    """
    Placeholder for a function to get satellite data.
    
    This is a more complex task that would typically involve:
    1. Using the AgroMonitoring API to create a polygon for the farmer's field.
    2. Requesting a vegetation index (like NDVI) for that polygon.
    3. The data would need to be processed to extract a meaningful value for your model.
    Alternatively, you could use Google Earth Engine (GEE), but this is a very complex
    service that requires its own API and is more suitable for server-side tasks.
    """
    logging.info("Satellite data fetching from GEE or AgroMonitoring is a more complex task.")
    logging.info("This would typically involve getting an NDVI value.")
    return None

def get_translation_data(text, target_language="hi"):
    """
    Placeholder for a function to translate text using LibreTranslate.
    """
    logging.info("Translation is a separate concern for the UI, but here is a placeholder.")
    url = "https://libretranslate.com/translate"
    payload = {
        "q": text,
        "source": "en",
        "target": target_language
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        translated_text = response.json()["translatedText"]
        return translated_text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error translating text: {e}")
        return None

if __name__ == '__main__':
    # This block is for testing the functions directly
    print("Testing API functions...")
    lat_lon=get_lat_lon("Chhattisgarh","Durg")
    test_lat = lat_lon["lat"]  # Mumbai, India
    test_lon = lat_lon["lon"]
    print(test_lat,test_lon)
    weather_data = get_weather_data(test_lat, test_lon)
    features = get_last7days_weather(test_lat, test_lon)
    print("7-day mean features:", features)
    soil_data = get_soil_ph_and_type(float(f"{test_lat:.2f}"),float(f"{test_lon:.2f}"),"rice")

    if weather_data:
        print("\nWeather Data:")
        print(json.dumps(weather_data, indent=2))
        
    agromonitoring_data = get_agromonitoring_data(test_lat, test_lon)
    if agromonitoring_data:
        print("\nAgroMonitoring Data:")
        print(json.dumps(agromonitoring_data, indent=2))
    if features:
        print("7-day mean features:", features)
        print(json.dumps(features, indent=2))
    if soil_data:
        print("soil data:", soil_data)
        print(json.dumps(soil_data, indent=2))
