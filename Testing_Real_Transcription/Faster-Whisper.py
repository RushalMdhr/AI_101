import sounddevice as sd
import numpy as np
import queue
import time
import sys
from faster_whisper import WhisperModel
import threading

# Load model (same as yours)
model = WhisperModel("base", device="cpu", compute_type="int8")

# Settings
SAMPLE_RATE = 16000
CHUNK_SECONDS = 2.0  # Process every 2 seconds
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_SECONDS)

audio_queue = queue.Queue()
running = True
last_text = ""

def audio_callback(indata, frames, time_info, status):
    audio_queue.put(indata[:, 0].copy())

def process_audio():
    global last_text
    audio_buffer = np.array([], dtype=np.int16)
    
    while running:
        try:
            # Get audio
            data = audio_queue.get(timeout=0.2)
            audio_buffer = np.append(audio_buffer, data)
            
            # Process when buffer is full
            if len(audio_buffer) >= CHUNK_SAMPLES:
                chunk = audio_buffer[:CHUNK_SAMPLES]
                audio_float = chunk.astype(np.float32) / 32768.0
                
                # Transcribe (like your working code)
                segments, _ = model.transcribe(
                    audio_float,
                    language="en",  # Change to "ne" for Nepali
                    vad_filter=True
                )
                
                # Get text
                text = " ".join([seg.text for seg in segments]).strip()
                
                if text and text != last_text:
                    # Clear line and show new text (streaming effect)
                    sys.stdout.write('\r' + ' ' * 80 + '\r')
                    sys.stdout.write(f"📝 {text}")
                    sys.stdout.flush()
                    last_text = text
                
                # Slide window (50% overlap for smooth streaming)
                audio_buffer = audio_buffer[CHUNK_SAMPLES // 2:]
                
        except queue.Empty:
            continue
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

# Start processing
thread = threading.Thread(target=process_audio, daemon=True)
thread.start()

print("\n🎤 Speak now! (Press Ctrl+C to stop)\n")
print("📝 ", end="", flush=True)

try:
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, dtype=np.int16):
        while running:
            time.sleep(0.1)
except KeyboardInterrupt:
    running = False
    print("\n\n👋 Stopped!")