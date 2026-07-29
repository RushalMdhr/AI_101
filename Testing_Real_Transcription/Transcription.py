import whisper
import pyaudio
import wave
import numpy as np
import threading
import queue
import time

class RealtimeWhisperTranscriber:
    def __init__(self, model_size="base"):
        """
        Initialize the transcriber with a Whisper model.
        Model sizes: 'tiny', 'base', 'small', 'medium', 'large'
        """
        print(f"Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size)
        self.audio_queue = queue.Queue()
        self.is_running = False
        
        # Audio recording parameters
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.record_seconds = 3  # Process audio in 3-second chunks
        
    def record_audio(self):
        """Record audio from microphone in a separate thread"""
        p = pyaudio.PyAudio()
        
        stream = p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        print("🎤 Recording started... Speak now!")
        
        while self.is_running:
            frames = []
            for _ in range(0, int(self.rate / self.chunk * self.record_seconds)):
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
            
            # Convert to numpy array
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
            self.audio_queue.put(audio_data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    def transcribe_audio(self):
        """Transcribe audio from the queue"""
        while self.is_running:
            try:
                audio_data = self.audio_queue.get(timeout=1)
                
                # Transcribe using Whisper
                result = self.model.transcribe(audio_data, language=None,word_timestamps=True, initial_prompt="There may be international names so make sure to transcribe some words without making sense")
                text = result['text'].strip()
                
                if text:
                    print(f"📝 {text}")
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error during transcription: {e}")
    
    def start(self):
        """Start real-time transcription"""
        self.is_running = True
        
        # Start recording thread
        record_thread = threading.Thread(target=self.record_audio)
        record_thread.daemon = True
        record_thread.start()
        
        # Start transcription thread
        transcribe_thread = threading.Thread(target=self.transcribe_audio)
        transcribe_thread.daemon = True
        transcribe_thread.start()
        
        print("🎙️ Real-time transcription running... Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n👋 Stopping transcription...")
            self.is_running = False

if __name__ == "__main__":
    # Install required packages:
    # pip install openai-whisper pyaudio numpy
    
    # Choose model size: 'tiny', 'base', 'small', 'medium', 'large'
    transcriber = RealtimeWhisperTranscriber(model_size="base")
    transcriber.start()