from faster_whisper import WhisperModel
import os

# Use smaller model for faster loading. Change to "large-v3" only if you have GPU
model_size = "base"  # Options: tiny, base, small, medium, large-v3
audio_file = "audio.mp3"

# Check if audio file exists
if not os.path.exists(audio_file):
    print(f"Error: {audio_file} not found!")
    print("Available files:", os.listdir())
    exit(1)

print(f"Loading {model_size} model...")
# Run on GPU with FP16 (recommended if available)
model = WhisperModel(model_size, device="cuda", compute_type="float16")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")

# or run on CPU with INT8 (slower but no GPU required)
# model = WhisperModel(model_size, device="cpu", compute_type="int8")
print("Model loaded successfully!\n")

print(f"Transcribing {audio_file}...")
segments, info = model.transcribe(audio_file, beam_size=5)

print(f"Detected language '{info.language}' with probability {info.language_probability:.2f}\n")

print("Transcription:")
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))