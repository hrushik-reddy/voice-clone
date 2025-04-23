from fastapi import FastAPI, HTTPException
import outetts
from pydantic import BaseModel
import time
import os
from fastapi.responses import FileResponse
import uuid

app = FastAPI()

# Initialize the interface
interface = outetts.Interface(
    config=outetts.ModelConfig.auto_config(
        model=outetts.Models.VERSION_1_0_SIZE_1B,
        quantization=outetts.LlamaCppQuantization.FP16,
        backend=outetts.Backend.HF,
    )
)

class AudioRequest(BaseModel):
    text: str

@app.post("/generate-map")
async def generate_map():
    try:
        start = time.time()
        speaker = interface.create_speaker("Peter Drucker on Joseph Juran and Quality-[AudioTrimmer.com] (1).mp3")
        end = time.time()
        
        # Save the speaker map
        interface.save_speaker(speaker, "peter-drucker-voicemap.json")
        
        return {
            "message": "Voice map generated successfully",
            "time_taken": f"{end - start:.2f} seconds"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-audio")
async def generate_audio(request: AudioRequest):
    try:
        if not os.path.exists("peter-drucker-voicemap.json"):
            raise HTTPException(status_code=400, detail="Voice map not found. Please generate it first using /generate-map")
        
        # Load the speaker
        speaker = interface.load_speaker("peter-drucker-voicemap.json")
        
        # Generate audio
        start_generate = time.time()
        output = interface.generate(
            config=outetts.GenerationConfig(
                text=request.text,
                generation_type=outetts.GenerationType.CHUNKED,
                speaker=speaker,
                sampler_config=outetts.SamplerConfig(
                    temperature=0.4
                ),
            )
        )
        end_generate = time.time()
        
        # Save the audio to a temporary file
        output_filename = f"output_{uuid.uuid4()}.wav"
        output.save(output_filename)
        
        # Return the audio file
        return FileResponse(
            output_filename,
            media_type="audio/wav",
            filename="generated_audio.wav",
            background=output_filename  # This will delete the file after sending
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
