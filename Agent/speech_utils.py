import speech_recognition as sr
from gtts import gTTS
import pyttsx3
import os
import tempfile
import time
from typing import Optional, Tuple

class SpeechHandler:    
    """Handles speech recognition and text-to-speech operations."""
    
    def __init__(self, use_offline_tts: bool = False):
        self.use_offline_tts = use_offline_tts
        self.recognizer = sr.Recognizer()
        
        # Initialize TTS engine
        if use_offline_tts:
            try:
                self.tts_engine = pyttsx3.init()
                # Configure voice properties
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    self.tts_engine.setProperty('voice', voices[0].id)
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 0.9)
                print("Offline TTS engine initialized successfully")
            except Exception as e:
                print(f"Failed to initialize offline TTS: {e}")
                print("Falling back to online TTS")
                self.use_offline_tts = False
        else:
            self.tts_engine = None
            print("Online TTS (gTTS) will be used")
    
    def listen_to_mic(self, timeout: int = 5, phrase_time_limit: int = 10) -> Tuple[bool, str]:
        try:
            with sr.Microphone() as source:
                print("Listening... (speak now)")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio input
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                
                print("Processing speech...")
                
                # Use Google's speech recognition (requires internet)
                text = self.recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
                return True, text
                
        except sr.WaitTimeoutError:
            return False, "No speech detected within timeout period"
        except sr.UnknownValueError:
            return False, "Could not understand the audio"
        except sr.RequestError as e:
            return False, f"Could not request results from speech recognition service: {e}"
        except Exception as e:
            return False, f"Error during speech recognition: {e}"
    
    def speak_text(self, text: str) -> bool:
        try:
            if self.use_offline_tts and self.tts_engine:
                # Use offline TTS (pyttsx3)
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                return True
            else:
                # Use online TTS (gTTS)
                return self._speak_with_gtts(text)
                
        except Exception as e:
            print(f"Error in TTS: {e}")
            return False
    
    def _speak_with_gtts(self, text: str) -> bool:
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_filename = temp_file.name
            
            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_filename)
            
            # Play audio (platform-specific)
            if os.name == 'nt':  # Windows
                os.system(f'start {temp_filename}')
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open {temp_filename}' if os.uname().sysname == 'Darwin' else f'xdg-open {temp_filename}')
            
            # Clean up after a delay
            time.sleep(0.5)
            try:
                os.unlink(temp_filename)
            except:
                pass
                
            return True
            
        except Exception as e:
            print(f"Error with gTTS: {e}")
            return False
    
    def test_microphone(self) -> bool:
        try:
            with sr.Microphone() as source:
                print("Microphone test successful")
                return True
        except Exception as e:
            print(f"Microphone test failed: {e}")
            return False
    
    def list_available_voices(self) -> list:
        if not self.use_offline_tts or not self.tts_engine:
            return []
        
        try:
            voices = self.tts_engine.getProperty('voices')
            return [voice.name for voice in voices]
        except:
            return []

# Convenience functions for easy use
def listen_to_mic(timeout: int = 5, phrase_time_limit: int = 10) -> Tuple[bool, str]:
    """Simple function to listen to microphone and get text."""
    handler = SpeechHandler()
    return handler.listen_to_mic(timeout, phrase_time_limit)

def speak_text(text: str, use_offline: bool = False) -> bool:
    """Simple function to convert text to speech."""
    handler = SpeechHandler(use_offline_tts=use_offline)
    return handler.speak_text(text)

if __name__ == "__main__":
    # Test the speech utilities
    print("Testing Speech Utilities...")
    
    # Test microphone
    handler = SpeechHandler()
    if handler.test_microphone():
        print("✓ Microphone is working")
        
        # Test speech recognition
        print("\nSpeak something when prompted...")
        success, result = handler.listen_to_mic()
        if success:
            print(f"✓ Speech recognized: {result}")
            
            # Test TTS
            print("\nTesting text-to-speech...")
            if handler.speak_text("Hello, this is a test of the speech utilities."):
                print("✓ TTS working")
            else:
                print("✗ TTS failed")
        else:
            print(f"✗ Speech recognition failed: {result}")
    else:
        print("✗ Microphone test failed")
    
    # List available voices if using offline TTS
    voices = handler.list_available_voices()
    if voices:
        print(f"\nAvailable voices: {voices}")
