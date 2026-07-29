### for whisper setup installation
pip install openai-whisper pyaudio numpy

### for speech recognition
pip install SpeechRecognition pyaudio
**was too slow as each time process seperately and processing takes time missing most of the words**

### for using Vosk
pip install vosk pyaudio
# Download a model:
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip

### for faster-whisper
# Install required packages
pip install faster-whisper sounddevice numpy torch

# For GPU support (optional but recommended for larger models)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118