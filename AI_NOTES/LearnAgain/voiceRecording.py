import sounddevice as sd
from scipy.io.wavfile import write

# Record audio
duration = 5  # seconds
sample_rate = 44100  # Hz

print("Recording...")
recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
recording = recording * 5
sd.wait()  # Wait until recording is complete
print("Done!")

# Save to file
write("output.wav", sample_rate, recording)