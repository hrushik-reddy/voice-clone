```markdown
# 🎙️ Hrushik Voice-Clone

Light-weight Flask API for **cloning a speaker’s voice** from a short audio sample and generating new speech on-demand.  
Powered by **[outetts](https://pypi.org/project/outetts)** for TTS and **Google Cloud Storage** for artifact hosting.

---

## ✨ Features
| Endpoint | Purpose |
|----------|---------|
| `POST /generate_voicemap` | Create & save a *voice map* (speaker embedding) from a signed-URL audio clip. |
| `GET  /list_voice_maps`  | List all locally cached voice maps. |
| `POST /generate_voice`   | Synthesize speech in a cloned voice for arbitrary text. |

All routes return signed GCS URLs so you can fetch results securely for **30 minutes**.

---

## 🗂️ Repo Layout
```
hrushik-reddy-voice-clone/
├── api.py              # Flask app with three endpoints
├── postman.json        # Ready-to-import requests for testing
├── requirements.txt    # Python deps
└── README.md           # You are here
```

---

## ⚙️ Quick-start

> **Prereqs:** Python 3.10+, ffmpeg (pydub), a GCP service account with GCS write access.

```bash
# 1. Clone + install
git clone https://github.com/<your-user>/hrushik-reddy-voice-clone.git
cd hrushik-reddy-voice-clone
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Export creds
export GOOGLE_APPLICATION_CREDENTIALS=/abs/path/to/proposals-creds.json
export FLASK_ENV=development               # optional

# 3. Run API
python api.py          # listens on 0.0.0.0:5000
```

---

## 🔑 Configuration

| Var | Default | Description |
|-----|---------|-------------|
| `PROJECT_ID`  | `680fa00bacc14688f44d5526` | GCP project id for Storage client |
| `BUCKET_NAME` | `creative-workspace`       | GCS bucket for voice maps & audio |
| `SERVICE_ACCOUNT_PATH` | `var/secrets/google/proposals-creds.json` | Fallback if env-var unset |

Edit these in **api.py** or override via environment variables.

---

## 🚀 Using the API

### 1 · Generate a voice map
```json
POST /generate_voicemap
{
  "signed_url": "https://storage.googleapis.com/<audio>.mp3",
  "speaker_name": "peter_drucker"   // optional
}
```
Returns a signed `voice_map_url` and processing time.

### 2 · List maps
`GET /list_voice_maps`

### 3 · Synthesize speech
```json
POST /generate_voice
{
  "speaker_name": "peter_drucker",
  "text": "Hello, world!"
}
```
Response JSON contains a time-limited `audio_url` (WAV).

Import **postman.json** into Postman/Insomnia for ready-made requests.

---

## 🏗️ How It Works
1. **Audio → WAV (≤20 s)** via *pydub*  
2. **outetts** extracts a speaker embedding and/or generates speech.  
3. Artifacts are pushed to **GCS** and a signed URL is returned.  

---

## 🤝 Contributing
PRs are welcome! Please open an issue first to discuss major changes.

---

## 📝 License
MIT © 2025 Hrushik Reddy
```
