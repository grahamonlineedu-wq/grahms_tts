import os
import psycopg2
from flask import Flask, request, jsonify, send_file
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("DEFAULT_VOICE_ID", "pNInz6obpgDQGcFmaJgB")
DATABASE_URL = os.getenv("DATABASE_URL")
OUTPUT_DIR = "static"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def log_to_db(text, voice, model, path):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tts_logs (text_content, voice_id, model_id, audio_file_path) VALUES (%s, %s, %s, %s)",
            (text, voice, model, path)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ Database Log Error: {e}")

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "Grahms TTS/STT Engine",
        "endpoints": {
            "tts": "/api/tts (POST)",
            "history": "/api/history (GET)"
        }
    })

@app.route("/api/tts", methods=["POST"])
def text_to_speech():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field in JSON body"}), 400

    text_input = data["text"]
    model_id = "eleven_flash_v2_5"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }

    payload = {
        "text": text_input,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            file_path = os.path.join(OUTPUT_DIR, "output.mp3")
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            log_to_db(text_input, VOICE_ID, model_id, file_path)
            
            return send_file(file_path, mimetype="audio/mpeg", as_attachment=True, download_name="grahms_speech.mp3")
        else:
            return jsonify({
                "error": "Failed to generate speech", 
                "details": response.json()
            }), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/history", methods=["GET"])
def get_history():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT id, text_content, voice_id, model_id, created_at FROM tts_logs ORDER BY created_at DESC LIMIT 10;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        history = []
        for row in rows:
            history.append({
                "id": row[0],
                "text": row[1],
                "voice_id": row[2],
                "model_id": row[3],
                "created_at": row[4].strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

