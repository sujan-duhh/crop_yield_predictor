import { Routes, Route } from "react-router-dom";

// import your pages
import HomePage from "./pages/HomePage";
import YieldPrediction from "./pages/yield_prediction";
import Fertilizer from "./pages/fertilizer";
import Irrigation from "./pages/irrigation";
import PestControl from "./pages/pest_control";

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/yield" element={<YieldPrediction />} />
        <Route path="/fertilizer" element={<Fertilizer />} />
        <Route path="/irrigation" element={<Irrigation />} />
        <Route path="/pest" element={<PestControl />} />
        <Route path="*" element={<HomePage />} />
      </Routes>
    </div>
  );
}

export default App;
