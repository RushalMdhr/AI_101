import pyttsx3


# import sounddevice as sd
# from scipy.io.wavfile import write
# import whisper

# fs = 16000
# seconds = 5

# print("Speak now...")
# audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
# sd.wait()

# write("input.wav", fs, audio)

# model = whisper.load_model("base")
# result = model.transcribe("input.wav")

# print("You said:", result["text"])
# bol = result["text"]

engine = pyttsx3.init()
# engine.say(bol)
# engine.runAndWait()

import ollama

prompt = "You are an English tutor. Reply simply."
response = ollama.chat(
    model="phi",
    messages=[{"role": "user", "content": "Help me learn English"}]
)

# print(response["message"]["content"])
bol = response.message.content
print(bol)
engine.say(bol)
engine.runAndWait()
