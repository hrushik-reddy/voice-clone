from flask import Flask, request, jsonify
import os
import tempfile
import json
import uuid
import time
import traceback
from datetime import timedelta

import requests
from pydub import AudioSegment

# ─── Google Cloud ───────────────────────────────────────────────────────────────
from google.cloud import storage
from google.oauth2 import service_account

# ─── outetts (voice-clone) ──────────────────────────────────────────────────────
import outetts

# ────────────────────────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────────────────────────
PROJECT_ID               = "680fa00bacc14688f44d5526"
BUCKET_NAME              = "creative-workspace"

LOCAL_VOICE_MAPS_DIR     = "voice_maps"
GCS_VOICE_MAPS_DIR       = "voice_maps"
GCS_GENERATED_AUDIO_DIR  = "generated_audio"

# Service-account JSON (set GOOGLE_APPLICATION_CREDENTIALS env-var or fall back)
SERVICE_ACCOUNT_PATH = "var/secrets/google/proposals-creds.json"

# ────────────────────────────────────────────────────────────────────────────────
app = Flask(__name__)
os.makedirs(LOCAL_VOICE_MAPS_DIR, exist_ok=True)

# ─── Helpers ────────────────────────────────────────────────────────────────────
def _creds():
    """Load service-account creds exactly once (cached)."""
    if not hasattr(_creds, "_cache"):
        _creds._cache = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_PATH
        )
    return _creds._cache


def get_storage_client() -> storage.Client:
    """Always build a client with explicit creds + project."""
    return storage.Client(project=PROJECT_ID, credentials=_creds())


def get_outetts_interface():
    return outetts.Interface(
        config=outetts.ModelConfig.auto_config(
            model=outetts.Models.VERSION_1_0_SIZE_1B,
            quantization=outetts.LlamaCppQuantization.FP16,
            backend=outetts.Backend.HF,
        )
    )


def download_from_signed_url(signed_url: str) -> bytes:
    r = requests.get(signed_url)
    r.raise_for_status()
    return r.content


def upload_to_gcs(file_bytes: bytes, gcs_path: str, content_type: str) -> str:
    client  = get_storage_client()
    bucket  = client.bucket(BUCKET_NAME)
    blob    = bucket.blob(gcs_path)

    blob.upload_from_string(file_bytes, content_type=content_type)

    return blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=30),
        method="GET",
    )


def process_audio(audio_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(audio_bytes)
        src_path = tmp.name

    try:
        audio = AudioSegment.from_file(src_path)[:20_000]          # trim 20 s
        wav_path = f"{src_path}.wav"
        audio.export(wav_path, format="wav")
        return wav_path
    finally:
        os.remove(src_path)


# ─── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/generate_voicemap", methods=["POST"])
def generate_voicemap():
    try:
        data = request.get_json(silent=True) or {}
        signed_url  = data.get("signed_url")
        if not signed_url:
            return jsonify(error="Missing signed_url"), 400

        speaker_name = data.get("speaker_name", f"speaker_{uuid.uuid4().hex[:8]}")

        audio_bytes  = download_from_signed_url(signed_url)
        wav_path     = process_audio(audio_bytes)

        interface    = get_outetts_interface()
        start_time   = time.time()
        speaker      = interface.create_speaker(wav_path)
        end_time     = time.time()

        vm_filename  = f"{speaker_name}_voice_map.json"
        local_path   = os.path.join(LOCAL_VOICE_MAPS_DIR, vm_filename)
        interface.save_speaker(speaker, local_path)

        with open(local_path, "rb") as f:
            vm_bytes = f.read()

        gcs_path   = f"{GCS_VOICE_MAPS_DIR}/{vm_filename}"
        vm_url     = upload_to_gcs(vm_bytes, gcs_path, "application/json")

        os.remove(wav_path)

        return jsonify(
            status="success",
            speaker_name=speaker_name,
            voice_map_path=local_path,
            voice_map_url=vm_url,
            time_taken=f"{end_time - start_time:.2f} s",
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify(error=str(e)), 500


@app.route("/list_voice_maps", methods=["GET"])
def list_voice_maps():
    try:
        maps = [
            {
                "speaker_name": f.replace("_voice_map.json", ""),
                "file_path": os.path.join(LOCAL_VOICE_MAPS_DIR, f),
            }
            for f in os.listdir(LOCAL_VOICE_MAPS_DIR)
            if f.endswith("_voice_map.json")
        ]
        return jsonify(status="success", voice_maps=maps)
    except Exception as e:
        traceback.print_exc()
        return jsonify(error=str(e)), 500


@app.route("/generate_voice", methods=["POST"])
def generate_voice():
    try:
        data = request.get_json(silent=True) or {}
        speaker_name = data.get("speaker_name")
        text         = data.get("text")
        if not speaker_name or not text:
            return jsonify(error="Missing speaker_name or text"), 400

        vm_path = os.path.join(LOCAL_VOICE_MAPS_DIR, f"{speaker_name}_voice_map.json")
        if not os.path.exists(vm_path):
            return jsonify(error=f"Voice map '{speaker_name}' not found"), 404

        interface = get_outetts_interface()
        speaker   = interface.load_speaker(vm_path)

        start = time.time()
        output = interface.generate(
            config=outetts.GenerationConfig(
                text=text,
                generation_type=outetts.GenerationType.CHUNKED,
                speaker=speaker,
                sampler_config=outetts.SamplerConfig(temperature=0.4),
            )
        )
        end = time.time()

        audio_name = f"{speaker_name}_{uuid.uuid4().hex[:8]}.wav"
        local_audio = os.path.join(tempfile.gettempdir(), audio_name)
        output.save(local_audio)

        with open(local_audio, "rb") as f:
            audio_bytes = f.read()

        gcs_path = f"{GCS_GENERATED_AUDIO_DIR}/{audio_name}"
        audio_url = upload_to_gcs(audio_bytes, gcs_path, "audio/wav")

        os.remove(local_audio)

        return jsonify(
            status="success",
            speaker_name=speaker_name,
            audio_url=audio_url,
            time_taken=f"{end - start:.2f} s",
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify(error=str(e)), 500


# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
