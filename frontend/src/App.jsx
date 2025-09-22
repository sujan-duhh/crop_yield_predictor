import { useEffect, useState } from "react";

function App() {
  const [features, setFeatures] = useState([]);
  const [formData, setFormData] = useState({});
  const [prediction, setPrediction] = useState(null);

  // ✅ Fetch feature names from backend
  useEffect(() => {
    fetch("http://127.0.0.1:5000/features")
      .then((res) => res.json())
      .then((data) => {
        setFeatures(data.features);
        const initialForm = {};
        data.features.forEach((f) => (initialForm[f] = ""));
        setFormData(initialForm);
      })
      .catch((err) => console.error("Error fetching features:", err));
  }, []);

  // ✅ Handle input changes
  const handleChange = (e) => {
    let value = e.target.value;

    // Convert numeric-looking inputs to numbers
    if (!isNaN(value) && value.trim() !== "") {
      value = Number(value);
    }

    setFormData({ ...formData, [e.target.name]: value });
  };

  // ✅ Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();
      if (res.ok) {
        setPrediction(data.prediction);
      } else {
        alert("Error: " + data.error);
      }
    } catch (err) {
      alert("Error contacting backend API");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>🌾 Crop Yield Predictor</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px" }}>
          {features.map((feature) => (
            <input
              key={feature}
              type="text"
              name={feature}
              placeholder={feature}
              value={formData[feature] || ""}
              onChange={handleChange}
              required
            />
          ))}
        </div>
        <button type="submit" style={{ marginTop: "20px" }}>
          Predict
        </button>
      </form>

      {prediction !== null && (
        <h2 style={{ marginTop: "20px" }}>Predicted Yield: {prediction}</h2>
      )}
    </div>
  );
}

export default App;
