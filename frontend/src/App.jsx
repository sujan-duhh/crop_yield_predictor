import { useState } from "react";

function App() {
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

    // Convert numeric-looking inputs to numbers
    if (e.target.name === "area_in_acres" && !isNaN(value) && value.trim() !== "") {
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
        setPrediction(data); // Save full response
      } else {
        alert("Error: " + data.error);
      }
    } catch (err) {
      alert("Error contacting backend API");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold text-center mb-8">🌾 Crop Yield Predictor</h1>

      <form
        onSubmit={handleSubmit}
        className="max-w-4xl mx-auto bg-white p-6 rounded-2xl shadow-lg"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {["crop", "state_name", "dist_name", "area_in_acres"].map((field) => (
            <input
              key={field}
              type={field === "area_in_acres" ? "number" : "text"}
              name={field}
              placeholder={field.replace("_", " ")}
              value={formData[field]}
              onChange={handleChange}
              required
              className="border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          ))}
        </div>
        <button
          type="submit"
          className="mt-6 w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition"
        >
          Predict
        </button>
      </form>

      {prediction && (
        <div className="mt-10 max-w-4xl mx-auto space-y-6">
          {/* Predicted Yield */}
          <div className="bg-white rounded-2xl shadow-lg p-6 text-center">
            <h2 className="text-xl font-semibold text-gray-700 mb-2">Predicted Yield</h2>
            <p className="text-2xl font-bold text-green-600">
              {prediction.prediction} {prediction.prediction_unit}
            </p>
          </div>

          {/* Total Yield */}
          <div className="bg-white rounded-2xl shadow-lg p-6 text-center">
            <h2 className="text-xl font-semibold text-gray-700 mb-2">Total Yield</h2>
            <p className="text-2xl font-bold text-blue-600">
              {prediction.total_prediction} {prediction.total_prediction_unit}
            </p>
          </div>

          {/* Inputs used by model */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-700 mb-2">Inputs Used by Model</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(prediction.inputs_used).map(([key, value]) => (
                <div key={key} className="bg-gray-100 rounded-lg p-2 text-center">
                  <p className="text-sm text-gray-600">{key}</p>
                  <p className="font-semibold">{value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
