import outetts

interface = outetts.Interface(
    config=outetts.ModelConfig.auto_config(
        model=outetts.Models.VERSION_1_0_SIZE_1B,
        # For llama.cpp backend
        # backend=outetts.Backend.LLAMACPP,
        quantization=outetts.LlamaCppQuantization.FP16,
        # For transformers backend
        backend=outetts.Backend.HF,
    )
)

import time

start = time.time()
speaker = interface.create_speaker("Peter Drucker on Joseph Juran and Quality-[AudioTrimmer.com] (1).mp3")
end = time.time()
interface.save_speaker(speaker, "peter-drucker-voicemap.json")

duration = end - start
print(f"Time taken: {duration:.2f} seconds")
