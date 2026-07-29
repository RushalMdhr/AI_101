import whisper
import ollama
import pyttsx3
import sounddevice as sd
from scipy.io.wavfile import write

# load models once
whisper_model = whisper.load_model("base")
tts = pyttsx3.init()

fs = 16000
seconds = 5

print("Speak now...")
audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
sd.wait()
write("input.wav", fs, audio)

result = whisper_model.transcribe("input.wav")
user_text = result["text"]

print("You:", user_text)

response = ollama.chat(
    model="phi",
    messages=[
        {"role": "system", "content": "talk in nepali language."},
        {"role": "user", "content": user_text}
    ]
)
# response = ollama.chat(
#     model="phi",
#     messages=[
#         {"role": "system", "content": "You are a friendly English tutor."},
#         {"role": "user", "content": user_text}
#     ]
# )

ai_text = response["message"]["content"]
print("AI:", ai_text)

tts.say(ai_text)
tts.runAndWait()
