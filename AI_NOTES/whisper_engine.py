from faster_whisper import WhisperModel

# model = WhisperModel("base", compute_type="int8")
model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

def transcribe_audio(audio_path):
    # segments, info = model.transcribe(audio_path)
    segments, info = model.transcribe(
        audio_path,
        language="ne"
    )

    full_text = ""

    for segment in segments:
        full_text += segment.text + " "

    return full_text.strip()