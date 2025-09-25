import { useState } from "react";
import BackButton from "../components/BackButton";

function YieldPrediction() {
  const [formData, setFormData] = useState({
    crop: "",
    state_name: "",
    dist_name: "",
    area_in_acres: "",
  });
  const [prediction, setPrediction] = useState(null);

  // ✅ Handle input changes
  const handleChange = (e) => {
    let value = e.target.value;

    if (e.target.name === "area_in_acres" && !isNaN(value) && value.trim() !== "") {
      value = Number(value);
    }

    setFormData({ ...formData, [e.target.name]: value });
  };

  // ✅ Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://127.0.0.1:5000/yield_prediction/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();
      if (res.ok) {
        setPrediction(data);
      } else {
        alert("Error: " + data.error);
      }
    } catch (err) {
      alert("Error contacting backend API");
    }
  };

  return (
    <div className="yield-root">
      <style>{`
        .yield-root {
          min-height: 100vh;
          background: #f3f4f6;
          padding: 32px;
          box-sizing: border-box;
        }
        .title {
          font-size: 28px;
          font-weight: 700;
          text-align: center;
          margin-bottom: 32px;
          color: #1f2937;
        }
        .form-box {
          max-width: 900px;
          margin: 0 auto;
          background: #fff;
          padding: 24px;
          border-radius: 16px;
          box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        }
        .form-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 16px;
        }
        @media (min-width: 768px) {
          .form-grid {
            grid-template-columns: 1fr 1fr;
          }
        }
        .form-input {
          border: 1px solid #d1d5db;
          border-radius: 8px;
          padding: 10px;
          font-size: 14px;
          outline: none;
          transition: border-color 0.2s;
        }
        .form-input:focus {
          border-color: #22c55e;
          box-shadow: 0 0 0 2px rgba(34,197,94,0.3);
        }
        .submit-btn {
          margin-top: 24px;
          width: 100%;
          background: #16a34a;
          color: #fff;
          font-weight: 600;
          padding: 12px;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          transition: background 0.2s;
        }
        .submit-btn:hover {
          background: #15803d;
        }
        .prediction-section {
          margin-top: 40px;
          max-width: 900px;
          margin-left: auto;
          margin-right: auto;
          display: flex;
          flex-direction: column;
          gap: 24px;
        }
        .card {
          background: #fff;
          border-radius: 16px;
          box-shadow: 0 8px 24px rgba(0,0,0,0.08);
          padding: 24px;
          text-align: center;
        }
        .card h2 {
          font-size: 18px;
          font-weight: 600;
          color: #374151;
          margin-bottom: 8px;
        }
        .yield-value {
          font-size: 22px;
          font-weight: 700;
          color: #16a34a;
        }
        .total-value {
          font-size: 22px;
          font-weight: 700;
          color: #2563eb;
        }
        .inputs-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
        }
        @media (min-width: 768px) {
          .inputs-grid {
            grid-template-columns: 1fr 1fr 1fr;
          }
        }
        .input-card {
          background: #f3f4f6;
          padding: 10px;
          border-radius: 8px;
          text-align: center;
        }
        .input-card p {
          margin: 4px 0;
        }
        .input-key {
          font-size: 13px;
          color: #6b7280;
        }
        .input-value {
          font-weight: 600;
        }
      `}</style>

      <BackButton />
      <h1 className="title">🌾 Crop Yield Predictor</h1>

      <form onSubmit={handleSubmit} className="form-box">
        <div className="form-grid">
          {/* Crop dropdown */}
          <select
            name="crop"
            value={formData.crop}
            onChange={handleChange}
            required
            className="form-input"
          >
            <option value="">Select Crop</option>
            <option value="rice">Rice</option>
            <option value="maize">Maize</option>
            <option value="chickpea">Chickpea</option>
            <option value="cotton">Cotton</option>
          </select>

          {/* Other inputs */}
          <input
            type="text"
            name="state_name"
            placeholder="State"
            value={formData.state_name}
            onChange={handleChange}
            required
            className="form-input"
          />
          <input
            type="text"
            name="dist_name"
            placeholder="District"
            value={formData.dist_name}
            onChange={handleChange}
            required
            className="form-input"
          />
          <input
            type="number"
            name="area_in_acres"
            placeholder="Area (in acres)"
            value={formData.area_in_acres}
            onChange={handleChange}
            required
            className="form-input"
          />
        </div>
        <button type="submit" className="submit-btn">
          Predict
        </button>
      </form>

      {prediction && (
        <div className="prediction-section">
          {/* Predicted Yield */}
          <div className="card">
            <h2>Predicted Yield</h2>
            <p className="yield-value">
              {prediction.prediction} {prediction.prediction_unit}
            </p>
          </div>

          {/* Total Yield */}
          <div className="card">
            <h2>Total Yield</h2>
            <p className="total-value">
              {prediction.total_prediction} {prediction.total_prediction_unit}
            </p>
          </div>

          {/* Inputs used */}
          <div className="card">
            <h2>Inputs Used by Model (Fetched from api's based on the state and district name provided)</h2>
            <div className="inputs-grid">
              {Object.entries(prediction.inputs_used).map(([key, value]) => (
                <div key={key} className="input-card">
                  <p className="input-key">{key}</p>
                  <p className="input-value">{value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default YieldPrediction;
