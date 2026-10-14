import os
import soundfile as sf
from celery import Celery
from TTS.api import TTS

# Initialize Celery to handle async generation tasks
celery_app = Celery('voice_tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# Global variable to cache the model in GPU memory on worker boot
tts_model = None

def get_model():
    global tts_model
    if tts_model is None:
        # Load the highly advanced XTTS v2 foundational model onto the GPU
        tts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
    return tts_model

@celery_app.task(name="generate_voice_clone")
def generate_voice_clone(text: str, speaker_wav_path: str, output_path: str, language: str = "en"):
    try:
        model = get_model()

        # Zero-shot cross-lingual voice cloning synthesis
        model.tts_to_file(
            text=text,
            speaker_wav=speaker_wav_path,
            language=language,
            file_path=output_path
        )
        return {"status": "success", "file_path": output_path}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

