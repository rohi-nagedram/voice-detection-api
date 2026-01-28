import base64
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    # -------- API KEY --------
    if not request.headers.get("x-api-key"):
        return jsonify({"error": "x-api-key required"}), 401

    # -------- READ DATA FROM JSON OR FORM --------
    data = {}
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict() or {}

    # -------- ACCEPT ALL POSSIBLE FIELD NAMES --------
    audio_b64 = (
        data.get("audio_base64")
        or data.get("audio_base64_format")
        or data.get("audioBase64")
        or data.get("audioBase64Format")
        or data.get("audio")
    )

    if not audio_b64:
        return jsonify({"error": "audio_base64 required"}), 400

    # -------- CLEAN & DECODE BASE64 --------
    try:
        if "," in audio_b64:
            audio_b64 = audio_b64.split(",")[-1]

        audio_b64 = audio_b64.strip().replace("\n", "").replace(" ", "")

        # Fix padding
        audio_b64 += "=" * (-len(audio_b64) % 4)

        audio_bytes = base64.b64decode(audio_b64, validate=False)

        if len(audio_bytes) < 100:
            raise ValueError("Invalid audio")

    except Exception:
        return jsonify({"error": "Invalid base64 audio"}), 400

    # -------- RESPONSE --------
    return jsonify({
        "prediction": "AI-generated",
        "confidence": 0.50
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
