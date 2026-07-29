import vosk
import pyaudio
import json
import sys
import queue

class VoskTranscriber:
    def __init__(self, model_path="vosk-model-en-us-daanzu-20200905"):
        """
        Initialize Vosk transcriber.
        Download models from: https://alphacephei.com/vosk/models
        """
        try:
            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("Please download a model from: https://alphacephei.com/vosk/models")
            sys.exit(1)
        
        self.audio_queue = queue.Queue()
        self.is_running = False
        
    def record_audio(self):
        """Record and process audio"""
        p = pyaudio.PyAudio()
        
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8000
        )
        
        print("🎤 Listening... Speak now! (Press Ctrl+C to stop)")
        
        while self.is_running:
            try:
                data = stream.read(4000, exception_on_overflow=False)
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        print(f"📝 {text}")
                else:
                    # Partial result
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get("partial", "")
                    if partial_text:
                        print(f"⏳ {partial_text}", end="\r")
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    def start(self):
        """Start real-time transcription"""
        self.is_running = True
        self.record_audio()

if __name__ == "__main__":
    # Install required packages:
    # pip install vosk pyaudio
    # Download model: wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    # Unzip and place in the same directory
    
    transcriber = VoskTranscriber("vosk-model-small-en-us-0.15")
    transcriber.start()