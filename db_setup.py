import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Create TTS history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tts_logs (
                id SERIAL PRIMARY KEY,
                text_content TEXT NOT NULL,
                voice_id VARCHAR(100) NOT NULL,
                model_id VARCHAR(100) NOT NULL,
                audio_file_path VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database table 'tts_logs' successfully created/verified!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

if __name__ == "__main__":
    init_db()

