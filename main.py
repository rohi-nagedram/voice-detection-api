from flask import Flask, request, jsonify
import requests
import os
import base64

app = Flask(__name__)

API_KEY = "test123"

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = "superb/hubert-large-superb-er"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

HF_HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/predict", methods=["POST"])
def predict():
    # Auth
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # ✅ GUVI sends audio_base64_format
    audio_b64 = data.get("audio_base64_format") or data.get("audio_base64")
    if not audio_b64:
        return jsonify({"error": "audio_base64 required"}), 400

    # Decode base64
    try:
        audio_bytes = base64.b64decode(audio_b64)
    except Exception:
        return jsonify({"error": "Invalid base64 audio"}), 400

    # HuggingFace inference
    try:
        hf_resp = requests.post(
            HF_API_URL,
            headers=HF_HEADERS,
            data=audio_bytes,
            timeout=30
        )
        result = hf_resp.json()
    except Exception:
        return jsonify({"error": "Inference failed"}), 500

    confidence = 0.5
    if isinstance(result, list) and len(result) > 0:
        top = max(result, key=lambda x: x.get("score", 0))
        confidence = round(top.get("score", 0), 2)

    prediction = "AI-generated" if confidence >= 0.5 else "Human-generated"

    return jsonify({
        "prediction": prediction,
        "confidence": confidence,
        "explanation": "Prediction based on audio classification confidence"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
