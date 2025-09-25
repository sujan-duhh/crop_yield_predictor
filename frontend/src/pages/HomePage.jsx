// src/pages/HomePage.jsx
import { Link } from "react-router-dom";
import "../index.css"

export default function HomePage() {
  const features = [
    {
      title: "🌾 Yield Prediction",
      desc: "Predict crop yield using soil and weather data.",
      link: "/yield",
    },
    {
      title: "💊 Fertilizer Recommendation",
      desc: "Get the best fertilizer recommendation for your crop.",
      link: "/fertilizer",
    },
    {
      title: "💧 Irrigation Recommendation",
      desc: "Find the best irrigation technique for your field.",
      link: "/irrigation",
    },
    {
      title: "🪲 Pest Risk Prediction",
      desc: "Check pest risk and get preventive measures.",
      link: "/pest",
    },
  ];

  return (
    <div className="homepage-root">
      {/* Inline CSS so this works even without Tailwind */}
      <style>{`
        .homepage-root {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 40px;
          background: linear-gradient(135deg, #f3f4f6 0%, #e6eef7 100%);
          box-sizing: border-box;
        }
        .homepage-container {
          width: 100%;
          max-width: 1000px;
          text-align: center;
        }
        .homepage-title {
          font-size: 34px;
          margin-bottom: 28px;
          color: #0f172a;
          font-weight: 700;
        }
        .features-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 24px;
        }
        /* 2 columns on medium+ screens */
        @media (min-width: 768px) {
          .features-grid {
            grid-template-columns: 1fr 1fr;
          }
        }
        .feature-card {
          background: #fff;
          border-radius: 14px;
          padding: 28px;
          min-height: 180px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-decoration: none;
          color: inherit;
          box-shadow: 0 8px 20px rgba(16,24,40,0.06);
          border: 1px solid rgba(15,23,42,0.06);
          transition: transform 180ms ease, box-shadow 180ms ease;
        }
        .feature-card:hover {
          transform: translateY(-6px);
          box-shadow: 0 18px 40px rgba(16,24,40,0.12);
        }
        .feature-title {
          font-size: 20px;
          font-weight: 600;
          margin-bottom: 8px;
        }
        .feature-desc {
          font-size: 13px;
          color: #475569;
          max-width: 280px;
        }
      `}</style>

      <div className="homepage-container">
        <h1 className="homepage-title">🌱 Smart Agriculture Advisory System</h1>

        <div className="features-grid">
          {features.map((f) => (
            <Link to={f.link} key={f.title} className="feature-card">
              <h2 className="feature-title">{f.title}</h2>
              <p className="feature-desc">{f.desc}</p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
