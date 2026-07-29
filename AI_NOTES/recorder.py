import sounddevice as sd
from scipy.io.wavfile import write
import os
import time

SAMPLE_RATE = 16000
CHUNK_DURATION = 10

os.makedirs("audio_chunks", exist_ok=True)


def record_chunk(index):
    print(f"Recording chunk {index}...")

    audio = sd.rec(
        int(CHUNK_DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='int16'
    )

    sd.wait()

    filename = f"audio_chunks/chunk_{index}.wav"

    write(filename, SAMPLE_RATE, audio)

    print(f"Saved: {filename}")

    return filename