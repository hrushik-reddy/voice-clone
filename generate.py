import outetts
import time
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

speaker = interface.load_speaker("peter-drucker-voicemap.json")
text = """Hello, I am Peter Drucker.
Soon, you will be able to... hear my ideas — in my own voice.
Selected excerpts from my most influential books, brought to life for you.
Stay tuned! A new way to listen,learn, and be inspired... is coming soon!
"""

start_generate = time.time()
output = interface.generate(
    config=outetts.GenerationConfig(
        text=text,
        generation_type=outetts.GenerationType.CHUNKED,
        speaker=speaker,
        sampler_config=outetts.SamplerConfig(
            temperature=0.4
        ),
    )
)
end_generate = time.time()
print(f"Time to generate speech: {end_generate - start_generate:.2f} seconds")