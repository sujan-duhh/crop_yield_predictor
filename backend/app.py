from flask import Flask, jsonify
from flask_cors import CORS

# Import Blueprints
from fertilizers import fertilizer_bp
from yeild_prediction import yield_bp
from irrigation import irrigation_bp
from pest_control import pest_bp

app = Flask(__name__)
CORS(app)

# Register all routes with prefixes
app.register_blueprint(fertilizer_bp, url_prefix="/fertilizer")
app.register_blueprint(yield_bp, url_prefix="/yield_prediction")
app.register_blueprint(irrigation_bp, url_prefix="/irrigation")
app.register_blueprint(pest_bp, url_prefix="/pest_control")

# ✅ Root route for status check
@app.route("/")
def home():
    return jsonify({
        "message": "🌾 Crop Advisory API is running!",
        "available_endpoints": {
            "fertilizer": "/fertilizer/predict",
            "yield_prediction": "/yield_prediction/predict",
            "irrigation": "/irrigation/predict",
            "pest_control": "/pest_control/predict"
        }
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
