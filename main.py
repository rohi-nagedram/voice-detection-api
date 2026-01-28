from flask import Flask, request, jsonify
import base64
import re

app = Flask(__name__)

API_KEY = "test123"

# ---------- helpers ----------

def clean_base64(b64_str: str) -> str:
    """
    Cleans base64 string:
    - removes data:audio/...;base64,
    - removes whitespace and newlines
    - validates base64 characters
    """
    if not b64_str:
        return ""

    # remove data URI prefix if present
    b64_str = re.sub(r"^data:audio/.+;base64,", "", b64_str)

    # remove spaces and newlines
    b64_str = re.sub(r"\s+", "", b64_str)

    return b64_str


def is_valid_base64(b64_str: str) -> bool:
    try:
        base64.b64decode(b64_str, validate=True)
        return True
    except Exception:
        return False


# ---------- health ----------

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ---------- voice detection ----------

@app.route("/predict", methods=["POST"])
def predict():
    # auth
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}

    audio_b64 = (
        data.get("audio_base64")
        or data.get("audioBase64")
        or data.get("audio")
    )

    if not audio_b64:
        return jsonify({"error": "audio_base64 required"}), 400

    audio_b64 = clean_base64(audio_b64)

    if not is_valid_base64(audio_b64):
        return jsonify({"error": "Invalid base64 audio"}), 400

    # dummy prediction (safe placeholder)
    return jsonify({
        "prediction": "AI-generated",
        "confidence": 0.5
    }), 200


# ---------- honey pot ----------

@app.route("/honeypot", methods=["POST"])
def honeypot():
    # auth
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    payload = str(data).lower()

    suspicious_keywords = [
        "drop", "delete", "truncate", "hack",
        "bypass", "admin", "password",
        "token", "sql", "script", "eval"
    ]

    threat = any(word in payload for word in suspicious_keywords)

    return jsonify({
        "threat_detected": threat,
        "threat_type": "malicious_input" if threat else "none",
        "risk_level": "high" if threat else "low",
        "action": "blocked" if threat else "allowed"
    }), 200


# ---------- entry ----------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
