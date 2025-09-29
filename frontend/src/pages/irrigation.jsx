import { useState } from "react";
import BackButton from "../components/BackButton";

function Irrigation() {
  const [formData, setFormData] = useState({
    crop_name: "",
    growth_stage: "",
    water_availability: "",
    source_of_water: "",
    field_slope: "",
    area_acres: "",
    state: "",
    district: "",
    soil_type: "",
  });

  const [recommendation, setRecommendation] = useState(null);

  // ---------- Dropdown options ----------
  const cropOptions = [
    "maize", "Maize", "rice", "Rice", "Sugarcane", "chickpea", "cotton", "Wheat",
    "Potato", "Tomato", "grapes", "orange", "mothbeans", "kidneybeans", "apple",
    "muskmelon", "jute", "coconut", "banana", "mungbean", "coffee", "pomegranate",
    "blackgram", "papaya", "watermelon", "pigeonpeas", "mango", "lentil"
  ];
  const growthStageOptions = ["maturity", "flowering", "seedling", "vegetative"];
  const soilTypeOptions = ["loamy", "peaty", "clay", "silt", "saline", "sandy"];
  const waterHoldingOptions = ["medium", "high", "low"];
  const waterAvailabilityOptions = ["abundant", "moderate", "scarce"];
  const waterSourceOptions = ["borewell", "rain-fed", "tank", "canal"];
  const slopeOptions = ["flat", "gentle", "steep"];

  // ---------- Styles ----------
  const styles = {
    container: {
      minHeight: "100vh",
      background: "#eff6ff",
      padding: "2rem",
    },
    title: {
      fontSize: "2rem",
      fontWeight: "bold",
      textAlign: "center",
      marginBottom: "2rem",
    },
    form: {
      maxWidth: "700px",
      margin: "0 auto",
      background: "white",
      padding: "1.5rem",
      borderRadius: "1rem",
      boxShadow: "0 6px 15px rgba(0,0,0,0.1)",
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: "1rem",
    },
    input: {
      padding: "0.3rem",
      border: "1px solid #d1d5db",
      borderRadius: "0.5rem",
      fontSize: "1rem",
      width: "100%",
    },
    button: {
      gridColumn: "span 2",
      marginTop: "1rem",
      padding: "0.75rem",
      background: "#2563eb",
      color: "white",
      border: "none",
      borderRadius: "0.5rem",
      cursor: "pointer",
      fontWeight: "bold",
    },
    card: {
      marginTop: "2rem",
      maxWidth: "700px",
      marginLeft: "auto",
      marginRight: "auto",
      background: "white",
      padding: "1.5rem",
      borderRadius: "1rem",
      boxShadow: "0 6px 15px rgba(0,0,0,0.1)",
    },
    heading: {
      fontSize: "1.25rem",
      fontWeight: "600",
      marginBottom: "0.5rem",
    },
    probaRow: {
      display: "flex",
      alignItems: "center",
      gap: "0.5rem",
      marginBottom: "0.5rem",
    },
    probaBar: {
      flex: 1,
      background: "#e5e7eb",
      borderRadius: "0.25rem",
      height: "1rem",
      overflow: "hidden",
    },
    probaFill: {
      height: "100%",
    },
    suggestionBox: {
      background: "#ecfdf5",
      borderLeft: "4px solid #16a34a",
      padding: "1rem",
      borderRadius: "0.5rem",
    },
  };

  // ---------- Helpers ----------
  const handleChange = (e) => {
    let { name, value } = e.target;
    if (["area_acres"].includes(name)) {
      value = value.trim() === "" ? "" : Number(value);
    }
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://127.0.0.1:5000/irrigation/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();
      if (res.ok) {
        setRecommendation(data);
      } else {
        alert("Error: " + (data.error || "Something went wrong"));
      }
    } catch (err) {
      alert("Error contacting backend API");
      console.error(err);
    }
  };

  const getProbaColor = (method) => {
    const m = method.toLowerCase();
    if (m.includes("drip")) return { background: "#bfdbfe", color: "#1e3a8a" };
    if (m.includes("sprinkler")) return { background: "#bbf7d0", color: "#166534" };
    if (m.includes("furrow")) return { background: "#fef08a", color: "#854d0e" };
    if (m.includes("rain")) return { background: "#e0e7ff", color: "#3730a3" };
    return { background: "#e5e7eb", color: "#374151" };
  };

  // ---------- JSX ----------
  return (
    <div style={styles.container}>
      <BackButton />
      <h1 style={styles.title}>💧 Irrigation Recommendation</h1>

      {/* FORM */}
      <form onSubmit={handleSubmit} style={styles.form}>
        {/* crop_name */}
        <select
          name="crop_name"
          value={formData.crop_name}
          onChange={handleChange}
          style={styles.input}
          required
        >
          <option value="">Select Crop</option>
          {cropOptions.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        {/* growth_stage */}
        <select
          name="growth_stage"
          value={formData.growth_stage}
          onChange={handleChange}
          style={styles.input}
          required
        >
          <option value="">Select Growth Stage</option>
          {growthStageOptions.map((g) => (
            <option key={g} value={g}>
              {g}
            </option>
          ))}
        </select>

        {/* water_availability */}
        <select
          name="water_availability"
          value={formData.water_availability}
          onChange={handleChange}
          style={styles.input}
          required
        >
          <option value="">Select Water Availability</option>
          {waterAvailabilityOptions.map((w) => (
            <option key={w} value={w}>
              {w}
            </option>
          ))}
        </select>

        {/* source_of_water */}
        <select
          name="source_of_water"
          value={formData.source_of_water}
          onChange={handleChange}
          style={styles.input}
          required
        >
          <option value="">Select Source of Water</option>
          {waterSourceOptions.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>

        {/* field_slope */}
        <select
          name="field_slope"
          value={formData.field_slope}
          onChange={handleChange}
          style={styles.input}
          required
        >
          <option value="">Select Field Slope</option>
          {slopeOptions.map((f) => (
            <option key={f} value={f}>
              {f}
            </option>
          ))}
        </select>
        
        {/* soil_type */}
        <select
          name="soil_type"
          value={formData.soil_type}
          onChange={handleChange}
          style={styles.input}
          required
        >
          <option value="">Select soil type</option>
          {soilTypeOptions.map((f) => (
            <option key={f} value={f}>
              {f}
            </option>
          ))}
        </select>

        {/* area_acres */}
        <input
          type="number"
          name="area_acres"
          placeholder="AREA (acres)"
          value={formData.area_acres}
          onChange={handleChange}
          style={styles.input}
          required
        />

        {/* state */}
        <input
          type="text"
          name="state"
          placeholder="STATE"
          value={formData.state}
          onChange={handleChange}
          style={styles.input}
          required
        />

        {/* district */}
        <input
          type="text"
          name="district"
          placeholder="DISTRICT"
          value={formData.district}
          onChange={handleChange}
          style={styles.input}
          required
        />

        <button type="submit" style={styles.button}>
          Get Recommendation
        </button>
      </form>

      {/* RECOMMENDATION */}
      {recommendation && (
        <div style={styles.card}>
          <h2 style={styles.heading}>🌱 Irrigation Result</h2>

          <p>
            <strong>Method:</strong>{" "}
            <span style={{ color: "#2563eb", fontWeight: "600" }}>
              {recommendation.irrigation_method}
            </span>
          </p>

          {recommendation.prediction_proba && (
            <div>
              <h3 style={styles.heading}>📊 Prediction Probabilities</h3>
              {Object.entries(recommendation.prediction_proba).map(
                ([method, prob]) => (
                  <div key={method} style={styles.probaRow}>
                    <span
                      style={{
                        padding: "0.25rem 0.5rem",
                        borderRadius: "0.25rem",
                        fontSize: "0.9rem",
                        fontWeight: "500",
                        minWidth: "70px",
                        textAlign: "center",
                        ...getProbaColor(method),
                      }}
                    >
                      {method}
                    </span>
                    <div style={styles.probaBar}>
                      <div
                        style={{
                          ...styles.probaFill,
                          ...getProbaColor(method),
                          width: `${prob * 100}%`,
                        }}
                      ></div>
                    </div>
                    <span style={{ fontSize: "0.9rem", fontWeight: "600" }}>
                      {(prob * 100).toFixed(1)}%
                    </span>
                  </div>
                )
              )}
            </div>
          )}

          {recommendation.suggestion && (
            <div style={styles.suggestionBox}>
              <h3 style={styles.heading}>💡 Suggestion</h3>
              <p>{recommendation.suggestion}</p>
            </div>
          )}

          <div style={{ marginTop: "1rem" }}>
            <h3 style={styles.heading}>🌍 Environmental Stats</h3>
            <p><strong>🌡 Temperature:</strong> {recommendation.temperature} °C</p>
            <p><strong>💧 Humidity:</strong> {recommendation.humidity} %</p>
            <p><strong>🌧 Rainfall (last 7 days):</strong> {recommendation.rainfall_last_7_days} mm</p>
            <p><strong>🌧 Rainfall (forecast next 7 days):</strong> {recommendation.rainfall_forecast_next_7_days} mm</p>
            <p><strong>⚗️ Soil pH:</strong> {recommendation.soil_ph}</p>
            <p><strong>🪨 Soil Type:</strong> {recommendation.soil_type}</p>
            <p><strong>💧 Water Holding Capacity:</strong> {recommendation.water_holding_capacity}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default Irrigation;
