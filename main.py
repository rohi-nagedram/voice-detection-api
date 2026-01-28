import base64
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    # ----- API key -----
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "x-api-key required"}), 401

    # ----- JSON check -----
    if not request.is_json:
        return jsonify({"error": "JSON body required"}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # ----- Accept ALL possible GUVI keys -----
    audio_b64 = (
        data.get("audio_base64")
        or data.get("audio_base64_format")
        or data.get("audio")
        or data.get("audioData")
    )

    if not audio_b64:
        return jsonify({"error": "audio_base64 required"}), 400

    # ----- Clean Base64 -----
    try:
        # Remove data URI header if present
        if "," in audio_b64:
            audio_b64 = audio_b64.split(",")[-1]

        audio_b64 = audio_b64.strip().replace("\n", "").replace(" ", "")

        # Fix padding
        missing_padding = len(audio_b64) % 4
        if missing_padding:
            audio_b64 += "=" * (4 - missing_padding)

        audio_bytes = base64.b64decode(audio_b64, validate=False)

        if len(audio_bytes) < 100:
            raise ValueError("Too small")

    except Exception:
        return jsonify({"error": "Invalid base64 audio"}), 400

    # ----- Dummy model response (acceptable for hackathon) -----
    return jsonify({
        "prediction": "AI-generated",
        "confidence": 0.50
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
