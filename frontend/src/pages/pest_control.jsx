import React, { useState } from "react";
import axios from "axios";
import BackButton from "../components/BackButton";

export default function Pest() {
  const [formData, setFormData] = useState({
    Crop: "",
    Variety: "",
    Growth_Stage: "",
    State: "",
    District: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/pest_control/predict",
        formData
      );
      setResult(response.data);
    } catch (err) {
      const errorMsg = err.response?.data?.error || "Something went wrong!";
      alert(`Error: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  // ---------- Dropdown options ----------
  const cropOptions = ["Wheat", "Tomato", "Sugarcane", "Maize", "Potato", "Rice"];

  const cropVarietyMap = {
    Wheat: ["Durum", "Hard Red", "Soft Red"],
    Tomato: ["Beefsteak", "Cherry", "Roma"],
    Sugarcane: ["Co 0238", "Co 86032", "Co 99004"],
    Maize: ["Dent", "Flint", "Sweet"],
    Potato: ["Red", "Russet", "Yukon Gold"],
    Rice: ["Arborio", "Basmati", "Jasmine"],
  };

  const growthStageOptions = [
    "Flowering",
    "Fruiting/Grain_fill",
    "Seedling",
    "Vegetative",
  ];

  // ---------- Styles ----------
  const styles = {
    container: {
      minHeight: "100vh",
      background: "#f9fafb",
      padding: "2.5rem 1rem",
    },
    card: {
      maxWidth: "700px",
      margin: "0 auto",
      background: "white",
      borderRadius: "1rem",
      boxShadow: "0 6px 15px rgba(0,0,0,0.1)",
      padding: "1.5rem",
    },
    title: {
      fontSize: "2rem",
      fontWeight: "bold",
      textAlign: "center",
      marginBottom: "1.5rem",
    },
    form: {
      display: "flex",
      flexDirection: "column",
      gap: "1rem",
    },
    input: {
      padding: "0.5rem",
      border: "1px solid #d1d5db",
      borderRadius: "0.5rem",
      fontSize: "1rem",
    },
    button: {
      background: "#16a34a",
      color: "white",
      padding: "0.75rem",
      borderRadius: "0.5rem",
      fontWeight: "bold",
      cursor: "pointer",
      border: "none",
    },
    resultBox: {
      background: "#f9fafb",
      border: "1px solid #e5e7eb",
      padding: "1rem",
      borderRadius: "0.5rem",
      marginTop: "1rem",
    },
    heading: {
      fontSize: "1.2rem",
      fontWeight: "600",
      marginBottom: "0.5rem",
    },
    riskText: {
      fontSize: "1.5rem",
      fontWeight: "bold",
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
    },
  };

  // ---------- Helpers ----------
  const getRiskColor = (risk) => {
    if (!risk) return { color: "#374151" };
    const r = risk.toLowerCase();
    if (r.includes("low")) return { color: "#15803d" };
    if (r.includes("medium")) return { color: "#ca8a04" };
    if (r.includes("high")) return { color: "#dc2626" };
    return { color: "#2563eb" };
  };

  const getProbaColor = (label) => {
    const r = label.toLowerCase();
    if (r.includes("low")) return { background: "#bbf7d0", color: "#166534" };
    if (r.includes("medium")) return { background: "#fef08a", color: "#854d0e" };
    if (r.includes("high")) return { background: "#fecaca", color: "#991b1b" };
    return { background: "#e5e7eb", color: "#374151" };
  };

  // ---------- JSX ----------
  return (
    <div style={styles.container}>
      <BackButton />
      <div style={styles.card}>
        <h2 style={styles.title}>🪲 Pest Risk Prediction</h2>

        {/* Form */}
        <form onSubmit={handleSubmit} style={styles.form}>
          {/* Crop */}
          <select
            name="Crop"
            value={formData.Crop}
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

          {/* Variety (depends on Crop) */}
          <select
            name="Variety"
            value={formData.Variety}
            onChange={handleChange}
            style={styles.input}
            required
            disabled={!formData.Crop}
          >
            <option value="">Select Variety</option>
            {formData.Crop &&
              cropVarietyMap[formData.Crop].map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
          </select>

          {/* Growth Stage */}
          <select
            name="Growth_Stage"
            value={formData.Growth_Stage}
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

          {/* State + District (keep as free text for now) */}
          <input
            type="text"
            name="State"
            placeholder="State"
            value={formData.State}
            onChange={handleChange}
            style={styles.input}
            required
          />
          <input
            type="text"
            name="District"
            placeholder="District"
            value={formData.District}
            onChange={handleChange}
            style={styles.input}
            required
          />

          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? "Predicting..." : "Predict Pest Risk"}
          </button>
        </form>

        {/* Results */}
        {result && (
          <div>
            {/* Risk */}
            <div style={styles.resultBox}>
              <h3 style={styles.heading}>🌱 Risk Prediction</h3>
              <p style={{ ...styles.riskText, ...getRiskColor(result.prediction) }}>
                {result.prediction}
              </p>
            </div>

            {/* Probabilities */}
            {result.prediction_proba && (
              <div style={styles.resultBox}>
                <h3 style={styles.heading}>📊 Prediction Probabilities</h3>
                {Object.entries(result.prediction_proba).map(([label, prob]) => (
                  <div key={label} style={styles.probaRow}>
                    <span
                      style={{
                        padding: "0.25rem 0.5rem",
                        borderRadius: "0.25rem",
                        fontSize: "0.9rem",
                        fontWeight: "500",
                        minWidth: "70px",
                        textAlign: "center",
                        ...getProbaColor(label),
                      }}
                    >
                      {label}
                    </span>
                    <div style={styles.probaBar}>
                      <div
                        style={{
                          ...styles.probaFill,
                          ...getProbaColor(label),
                          width: `${prob * 100}%`,
                        }}
                      ></div>
                    </div>
                    <span style={{ fontSize: "0.9rem", fontWeight: "600" }}>
                      {(prob * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Suggestion */}
            <div style={{ ...styles.resultBox, ...styles.suggestionBox }}>
              <h3 style={styles.heading}>💡 Suggestion</h3>
              <p>{result.suggestion}</p>
            </div>

            {/* Weather + Soil */}
            <div style={styles.resultBox}>
              <h3 style={styles.heading}>🌍 Environmental Stats</h3>
              <p><strong>🌡 Temperature:</strong> {result.temperature} °C</p>
              <p><strong>💧 Humidity:</strong> {result.humidity} %</p>
              <p><strong>🌧 Rainfall:</strong> {result.rainfall} mm</p>
              <p><strong>⚗️ Soil pH:</strong> {result.ph}</p>
              <p><strong>🪨 Soil Type:</strong> {result.soil_type}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
