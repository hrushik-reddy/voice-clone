# Hrushik's Voice Cloning API

A Flask-based API for voice cloning and text-to-speech generation using the OuteTTS library.

> **IMPORTANT**: This application requires a GPU (NVIDIA L4 or greater recommended) for optimal performance. Voice cloning is computationally intensive and will be significantly slower without adequate GPU resources.

## Overview

This project enables you to:
- Generate voice maps from audio samples
- List available voice maps
- Generate speech using cloned voices with custom text

The system uses Google Cloud Storage for storing voice maps and generated audio files, making them accessible via signed URLs.

## Directory Structure

```
└── hrushik-reddy-voice-clone/
    ├── README.md
    ├── api.py
    ├── postman.json
    └── requirements.txt
```

## Features

- **Voice Map Generation**: Create voice fingerprints from audio samples
- **Voice Cloning**: Generate speech with cloned voices using custom text
- **Cloud Storage**: Store and retrieve voice maps and generated audio using Google Cloud Storage
- **API Interface**: Easy-to-use REST API endpoints

## Requirements

- Python 3.8+
- NVIDIA GPU (L4 or greater recommended)
- CUDA and cuDNN properly installed
- Google Cloud credentials
- OuteTTS library
- Flask and additional dependencies (see `requirements.txt`)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hrushik-reddy/voice-clone.git
cd hrushik-reddy-voice-clone
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Cloud credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-file.json"
```
   Alternatively, place your credentials file at `var/secrets/google/proposals-creds.json`

4. Create necessary directories:
```bash
mkdir -p voice_maps
```

## Usage

### Running the API Server

```bash
python api.py
```

The server will start on http://0.0.0.0:5000

### API Endpoints

#### 1. Generate Voice Map

Create a voice map from an audio sample:

```
POST /generate_voicemap
```

**Request Body**:
```json
{
  "signed_url": "https://storage.googleapis.com/your-audio-file.mp3",
  "speaker_name": "custom_speaker_name"
}
```

**Response**:
```json
{
  "status": "success",
  "speaker_name": "custom_speaker_name",
  "voice_map_path": "voice_maps/custom_speaker_name_voice_map.json",
  "voice_map_url": "https://storage.googleapis.com/...",
  "time_taken": "2.45 s"
}
```

#### 2. List Voice Maps

Get a list of all available voice maps:

```
GET /list_voice_maps
```

**Response**:
```json
{
  "status": "success",
  "voice_maps": [
    {
      "speaker_name": "custom_speaker_name",
      "file_path": "voice_maps/custom_speaker_name_voice_map.json"
    }
  ]
}
```

#### 3. Generate Voice

Generate speech using a cloned voice:

```
POST /generate_voice
```

**Request Body**:
```json
{
  "speaker_name": "custom_speaker_name",
  "text": "Hello, this is a test of voice generation."
}
```

**Response**:
```json
{
  "status": "success",
  "speaker_name": "custom_speaker_name",
  "audio_url": "https://storage.googleapis.com/...",
  "time_taken": "1.23 s"
}
```

## Postman Collection

A Postman collection is included in the repository (`postman.json`) to help you test the API endpoints. Import this collection into Postman to get started quickly.

## Technical Details

- **Audio Processing**: Uses PyDub to process and normalize audio files
- **Voice Cloning**: Leverages OuteTTS for voice cloning and speech generation
- **Storage**: Uses Google Cloud Storage for cloud-based file storage
- **API Framework**: Built with Flask for lightweight API endpoints

## Limitations

- Audio samples are trimmed to 20 seconds for voice map generation
- Requires proper Google Cloud credentials with access to the specified bucket

## License

[MIT License](LICENSE)

## Author

Hrushik Reddy
