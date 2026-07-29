from recorder import record_chunk
from whisper_engine import transcribe_audio
import os
from ai_summarizer import summarize_text
import keyboard

os.makedirs("notes", exist_ok=True)

TRANSCRIPT_FILE = "notes/transcript.md"


def save_transcript(text):
    with open(TRANSCRIPT_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n\n")


chunk_index = 1
full_transcript = ""

while True:

    if keyboard.is_pressed('q'):
        print("Stopping program...")
        break

    audio_file = record_chunk(chunk_index)

    print("Transcribing...")

    text = transcribe_audio(audio_file)

    print("Transcript:")
    print(text)

    full_transcript += text + "\n"

    summary = summarize_text(full_transcript)

    print(summary)

    save_transcript(summary)

    chunk_index += 1