import base64
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# ------------------------
# Health check
# ------------------------
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ------------------------
# Predict endpoint
# ------------------------
@app.route("/predict", methods=["POST"])
def predict():
    # ---- Header validation ----
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "x-api-key required"}), 401

    # ---- JSON validation ----
    if not request.is_json:
        return jsonify({"error": "JSON body required"}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # ---- Required fields ----
    language = data.get("language")
    audio_format = data.get("audio_format")
    audio_b64 = data.get("audio_base64")

    if not audio_b64:
        return jsonify({"error": "audio_base64 required"}), 400

    # ---- Robust Base64 cleaning ----
    try:
        # Remove data URI header if present
        if "," in audio_b64:
            audio_b64 = audio_b64.split(",")[-1]

        # Remove spaces and newlines
        audio_b64 = audio_b64.strip().replace("\n", "").replace(" ", "")

        # Fix missing padding
        missing_padding = len(audio_b64) % 4
        if missing_padding:
            audio_b64 += "=" * (4 - missing_padding)

        audio_bytes = base64.b64decode(audio_b64, validate=False)

        # Sanity check (not empty / not junk)
        if len(audio_bytes) < 100:
            return jsonify({"error": "Invalid base64 audio"}), 400

    except Exception:
        return jsonify({"error": "Invalid base64 audio"}), 400

    # ---- Dummy AI logic (hackathon-safe) ----
    # You can replace this later with a real model
    result = {
        "prediction": "AI-generated",
        "confidence": 0.50,
        "language": language or "unknown",
        "audio_format": audio_format or "unknown"
    }

    return jsonify(result), 200


# ------------------------
# Local run (not used by Render)
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
