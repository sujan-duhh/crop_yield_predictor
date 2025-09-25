// src/pages/fertilizer.jsx
import { useState } from "react";
import BackButton from "../components/BackButton";

export default function Fertilizer() {
  const [formData, setFormData] = useState({
    N: "",
    P: "",
    K: "",
    crop: "",
    state: "",
    district: "",
  });
  const [recommendation, setRecommendation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Crop options list
  const cropOptions = [
    "rice", "maize", "chickpea", "kidneybeans", "pigeonpeas", "mothbeans",
    "mungbean", "blackgram", "lentil", "pomegranate", "banana", "mango",
    "grapes", "watermelon", "muskmelon", "apple", "orange", "papaya",
    "coconut", "cotton", "jute", "coffee"
  ];


  const handleChange = (e) => {
    let value = e.target.value;
    if (["N", "P", "K"].includes(e.target.name) && !isNaN(value) && value.trim() !== "") {
      value = Number(value);
    }
    setFormData({ ...formData, [e.target.name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setRecommendation(null);
    try {
      const res = await fetch("http://127.0.0.1:5000/fertilizer/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (res.ok) {
        setRecommendation(data);
      } else {
        alert("Error: " + data.error);
      }
    } catch (err) {
      alert("Error contacting backend API");
    } finally {
      setIsLoading(false);
    }
  };

  const getProbaColor = (fert) => {
    const f = fert.toLowerCase();
    if (f.includes("urea")) return "blue";
    if (f.includes("dap")) return "purple";
    if (f.includes("mop")) return "green";
    if (f.includes("ssp")) return "goldenrod";
    if (f.includes("compost")) return "orange";
    return "gray";
  };

  return (
    <div className="fertilizer-root">
      <style>{`
        .fertilizer-root {
          min-height: 100vh;
          padding: 24px;
          background: linear-gradient(to bottom, #f0fdf4, #dcfce7);
          box-sizing: border-box;
        }
        .fertilizer-container {
          max-width: 1200px;
          margin: 0 auto;
        }
        .fertilizer-title {
          font-size: 28px;
          font-weight: 700;
          text-align: center;
          color: #166534;
          margin-bottom: 24px;
          border: 30px;
        }
        .fertilizer-layout {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }
        @media (min-width: 768px) {
          .fertilizer-layout {
            flex-direction: row;
          }
        }
        .fertilizer-form {
          flex: 1;
          background: #fff;
          border-radius: 14px;
          padding: 40px;
          padding-right-30px;
          box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        }
        .fertilizer-form input {
          width: 100%;
          margin-bottom: 12px;
          padding: 10px;
          border: 1px solid #d1d5db;
          border-radius: 8px;
          font-size: 14px;
        }
        .fertilizer-form input:focus {
          outline: none;
          border-color: #22c55e;
          box-shadow: 0 0 0 2px #22c55e33;
        }
        .fertilizer-submit {
          width: 100%;
          padding: 12px;
          border: none;
          border-radius: 8px;
          background: #16a34a;
          color: white;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s ease;
        }
        .fertilizer-submit:hover {
          background: #15803d;
        }
        .fertilizer-submit:disabled {
          background: #9ca3af;
          cursor: not-allowed;
        }
        .fertilizer-results {
          flex: 2;
          background: #fff;
          border-radius: 14px;
          padding: 24px;
          box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        }
        .fertilizer-placeholder {
          border: 2px dashed #cbd5e1;
          border-radius: 14px;
          padding: 40px;
          text-align: center;
          color: #64748b;
        }
        .prob-row {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
        }
        .prob-bar {
          flex: 1;
          height: 16px;
          border-radius: 8px;
          background: #e5e7eb;
          overflow: hidden;
        }
        .prob-fill {
          height: 100%;
          border-radius: 8px;
        }
      `}</style>

      <div className="fertilizer-container">
        <BackButton />
        <h1 className="fertilizer-title">💊 Fertilizer Recommendation</h1>

        <div className="fertilizer-layout">
          {/* Input Form */}
          <form onSubmit={handleSubmit} className="fertilizer-form">
            {["N", "P", "K", "state", "district"].map((field) => (
              <input
                key={field}
                type={["state", "district"].includes(field) ? "text" : "number"}
                name={field}
                placeholder={field.toUpperCase()}
                value={formData[field]}
                onChange={handleChange}
                required
              />
            ))}

            {/* 🔽 Crop dropdown with datalist */}
            <input
              type="text"
              name="crop"
              list="crop-options"
              placeholder="CROP"
              value={formData.crop}
              onChange={handleChange}
              required
            />
            <datalist id="crop-options">
              {cropOptions.map((crop) => (
                <option key={crop} value={crop} />
              ))}
            </datalist>

            <button type="submit" className="fertilizer-submit" disabled={isLoading}>
              {isLoading ? "Analyzing..." : "Get Recommendation"}
            </button>
          </form>

          {/* Results / Placeholder */}
          <div className="fertilizer-results">
            {recommendation ? (
              <div>
                <h2 style={{ textAlign: "center", fontWeight: "600", marginBottom: "12px" }}>
                  🌱 Recommended Fertilizer
                </h2>
                <div style={{ textAlign: "center", marginBottom: "20px" }}>
                  <p style={{ fontSize: "20px", fontWeight: "700", color: "#1d4ed8" }}>
                    {recommendation.fertilizer_full}
                  </p>
                  <span style={{ fontSize: "13px", color: "#6b7280" }}>
                    ({recommendation.fertilizer})
                  </span>
                </div>

                {/* Probabilities */}
                {recommendation.prediction_proba && (
                  <div>
                    <h3 style={{ marginBottom: "8px" }}>📊 Prediction Probabilities</h3>
                    {Object.entries(recommendation.prediction_proba).map(([fert, prob]) => (
                      <div key={fert} className="prob-row">
                        <span style={{
                          minWidth: "70px",
                          fontSize: "12px",
                          fontWeight: "600",
                          textAlign: "center",
                          color: getProbaColor(fert)
                        }}>
                          {fert}
                        </span>
                        <div className="prob-bar">
                          <div
                            className="prob-fill"
                            style={{
                              width: `${prob * 100}%`,
                              background: getProbaColor(fert)
                            }}
                          ></div>
                        </div>
                        <span style={{ minWidth: "40px", textAlign: "right", fontSize: "12px" }}>
                          {(prob * 100).toFixed(1)}%
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Other Info */}
                <div style={{
                  marginTop: "20px",
                  padding: "16px",
                  border: "1px solid #e5e7eb",
                  borderRadius: "10px",
                  background: "#f9fafb"
                }}>
                  <h3 style={{ marginBottom: "8px" }}>🌍 Field Conditions</h3>
                  <p><strong>🌡 Temperature:</strong> {recommendation.temperature} °C</p>
                  <p><strong>💧 Humidity:</strong> {recommendation.humidity} %</p>
                  <p><strong>⚗️ Soil pH:</strong> {recommendation.ph}</p>
                  <p><strong>🌧 Rainfall:</strong> {recommendation.rainfall} mm</p>
                </div>

                {recommendation.suggestion && (
                  <div style={{
                    marginTop: "20px",
                    padding: "12px",
                    borderLeft: "4px solid #16a34a",
                    background: "#f0fdf4",
                    borderRadius: "8px"
                  }}>
                    <p>{recommendation.suggestion}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="fertilizer-placeholder">
                <div style={{ fontSize: "40px", marginBottom: "12px" }}>🔬</div>
                <h2>Awaiting Input</h2>
                <p>Fill out the form and click "Get Recommendation" to see the analysis here.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
