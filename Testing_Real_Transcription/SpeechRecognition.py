import speech_recognition as sr
import time

def transcribe_realtime():
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Use the default microphone as source
    with sr.Microphone() as source:
        print("🎤 Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("🎤 Listening... Speak now! (Press Ctrl+C to stop)")
        
        try:
            while True:
                try:
                    # Listen for speech with a timeout
                    print("\nListening...")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    
                    # Recognize speech using Google Web Speech API
                    print("Processing...")
                    text = recognizer.recognize_google(audio)
                    print(f"📝 You said: {text}")
                    
                except sr.WaitTimeoutError:
                    print("⏰ No speech detected. Still listening...")
                    continue
                    
                except sr.UnknownValueError:
                    print("🔊 Could not understand audio. Please try again.")
                    continue
                    
                except sr.RequestError as e:
                    print(f"❌ Error with the speech recognition service: {e}")
                    break
                    
        except KeyboardInterrupt:
            print("\n👋 Stopping transcription... Goodbye!")

if __name__ == "__main__":
    # Install required packages:
    # pip install SpeechRecognition pyaudio
    transcribe_realtime()