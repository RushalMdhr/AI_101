from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np
import queue
import time
import threading
from datetime import datetime

# ---------- CONFIGURATION ----------
MODEL_SIZE = "large-v3"  # Use "base" or "small" for speed, "large-v3" for accuracy
SAMPLE_RATE = 16000
BUFFER_SECONDS = 1.5  # Smaller buffer = faster response
OVERLAP_SECONDS = 0.3  # Keep some context

# ---------- LOAD MODEL ----------
print(f"🔄 Loading {MODEL_SIZE} model...")
model = WhisperModel(
    MODEL_SIZE, 
    device="cuda",
    compute_type="float16"
)
print("✅ Model loaded!\n")

audio_queue = queue.Queue()
transcription_results = []
is_speaking = False
last_activity = time.time()

# ---------- AUDIO CALLBACK ----------
def audio_callback(indata, frames, time, status):
    if status:
        print(f"⚠️ {status}")
    audio_queue.put(indata.copy())

# ---------- REAL-TIME TRANSCRIPTION ----------
def process_audio_stream():
    """Process audio in small chunks for real-time response"""
    global is_speaking, last_activity
    
    buffer = np.array([], dtype=np.int16)
    last_transcription = ""
    chunk_count = 0
    
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype=np.int16,
        callback=audio_callback,
        blocksize=int(SAMPLE_RATE * 0.1),  # Small blocks for responsiveness
    ):
        print("🎤 Ready! Speak continuously for best results...")
        print("💡 The transcription will appear as you speak\n")
        print("-" * 60)
        
        while True:
            try:
                # Get audio chunk (non-blocking with timeout)
                chunk = audio_queue.get(timeout=0.1)
                buffer = np.append(buffer, chunk.flatten())
                chunk_count += 1
                
                # Process when we have enough audio
                required_samples = int(SAMPLE_RATE * BUFFER_SECONDS)
                
                if len(buffer) >= required_samples:
                    # Get the audio chunk
                    audio_chunk = buffer[:required_samples]
                    
                    # Convert to float32
                    audio_float32 = audio_chunk.astype(np.float32) / 32768.0
                    
                    # Quick silence check
                    if np.max(np.abs(audio_float32)) > 0.01:
                        is_speaking = True
                        last_activity = time.time()
                        
                        # Transcribe
                        start_time = time.time()
                        
                        segments, info = model.transcribe(
                            audio_float32,
                            beam_size=3,  # Smaller for speed
                            language="en",
                            vad_filter=True,
                            temperature=0.0,
                            best_of=1,  # Only one candidate for speed
                        )
                        
                        # Get text
                        text = " ".join(seg.text for seg in segments).strip()
                        elapsed = time.time() - start_time
                        
                        # Only print if there's new text
                        if text and text != last_transcription:
                            # Clear the line and print
                            print(f"\r{' ' * 80}", end='')  # Clear line
                            print(f"\r🗣️ {text}", end='', flush=True)
                            last_transcription = text
                            
                            # Store full transcription
                            if len(transcription_results) == 0 or text != transcription_results[-1]['text']:
                                transcription_results.append({
                                    'time': datetime.now().strftime("%H:%M:%S"),
                                    'text': text,
                                    'delay': elapsed
                                })
                                
                    # Keep overlap for context
                    overlap_samples = int(SAMPLE_RATE * OVERLAP_SECONDS)
                    if len(buffer) > overlap_samples:
                        buffer = buffer[-overlap_samples:]
                    else:
                        buffer = np.array([], dtype=np.int16)
                    
                    # Print processing stats occasionally
                    if chunk_count % 20 == 0:
                        print(f"\r⏱️ Processing... (buffer: {len(buffer)} samples)", end='', flush=True)
                    
            except queue.Empty:
                # Check if speaking stopped
                if is_speaking and time.time() - last_activity > 2.0:
                    is_speaking = False
                    print("\n⏸️ Paused... waiting for speech")
                continue
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue

# ---------- MAIN ----------
if __name__ == "__main__":
    try:
        process_audio_stream()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped")
    finally:
        # Print summary
        if transcription_results:
            print("\n\n📊 Summary:")
            print(f"Total transcriptions: {len(transcription_results)}")
            print(f"Average delay: {sum(r['delay'] for r in transcription_results) / len(transcription_results):.2f}s")
            print("\nLast few transcriptions:")
            for r in transcription_results[-5:]:
                print(f"  [{r['time']}] {r['text']}")