from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Simple API key for GUVI tester
API_KEY = "test123"

# Hugging Face config (token comes from Render env variable)
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
    # ---- Auth check ----
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {API_KEY}":
        return jsonify({"error": "Unauthorized"}), 401

    # ---- Input check ----
    data = request.get_json()
    if not data or "audio_url" not in data:
        return jsonify({"error": "audio_url required"}), 400

    audio_url = data["audio_url"]

    # ---- Download audio ----
    try:
        audio_resp = requests.get(audio_url, timeout=15)
        if audio_resp.status_code != 200:
            return jsonify({"error": "Failed to download audio"}), 400
    except Exception:
        return jsonify({"error": "Invalid audio URL"}), 400

    # ---- HuggingFace inference ----
    try:
        hf_resp = requests.post(
            HF_API_URL,
            headers=HF_HEADERS,
            data=audio_resp.content,
            timeout=30
        )
        result = hf_resp.json()
    except Exception:
        return jsonify({"error": "Inference failed"}), 500

    # ---- Parse result ----
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
