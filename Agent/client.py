import argparse
import requests
import json
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any

# Import speech utilities (optional)
try:
    from speech_utils import SpeechHandler
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("Warning: Speech utilities not available. Install required packages for speech features.")

class ChatClient:
    def __init__(self, base_url: str = "http://localhost:5000", session_id: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_history = []
        
        # Initialize speech handler if available
        self.speech_handler = None
        if SPEECH_AVAILABLE:
            try:
                self.speech_handler = SpeechHandler(use_offline_tts=False)
                print("✓ Speech features enabled")
            except Exception as e:
                print(f"Warning: Speech features disabled due to error: {e}")
    
    def send_message(self, message: str) -> Optional[str]:
        try:
            # Prepare request payload
            payload = {
                "session_id": self.session_id,
                "message": message
            }
            
            # Send POST request to /chat endpoint
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "No response received")
                
                # Store in conversation history
                self.conversation_history.append({
                    "timestamp": datetime.now(),
                    "user": message,
                    "ai": ai_response
                })
                
                return ai_response
            else:
                print(f"Error: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to backend at {self.base_url}")
            print("Make sure the Flask backend is running.")
            return None
        except requests.exceptions.Timeout:
            print("Error: Request timed out")
            return None
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def get_conversation_history(self) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(f"{self.base_url}/history/{self.session_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error retrieving history: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error retrieving history: {e}")
            return None
    
    def chat_loop(self, use_mic: bool = False, use_tts: bool = False, save_file: Optional[str] = None):
        print(f"🤖 Conversational Agent Client")
        print(f"📡 Backend: {self.base_url}")
        print(f"🆔 Session: {self.session_id}")
        print(f"🎤 Microphone: {'Enabled' if use_mic else 'Disabled'}")
        print(f"🔊 Text-to-Speech: {'Enabled' if use_tts else 'Disabled'}")
        if save_file:
            print(f"💾 Saving to: {save_file}")
        print("=" * 50)
        print("Type 'quit', 'exit', or 'bye' to end the conversation")
        print("Type 'history' to see conversation history")
        print("Type 'help' for available commands")
        print("=" * 50)
        
        while True:
            try:
                # Get user input
                if use_mic and self.speech_handler:
                    print("\n🎤 Listening... (speak your message)")
                    success, user_input = self.speech_handler.listen_to_mic()
                    if not success:
                        print(f"Speech recognition failed: {user_input}")
                        continue
                    print(f"🎯 Recognized: {user_input}")
                else:
                    user_input = input("\n💬 You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("👋 Goodbye!")
                    break
                
                # Check for special commands
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'history':
                    self._show_history()
                    continue
                elif user_input.lower() == 'status':
                    self._show_status()
                    continue
                elif user_input.lower() == 'clear':
                    self.conversation_history.clear()
                    print("🗑️  Conversation history cleared")
                    continue
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Send message to backend
                print("🔄 Sending message...")
                ai_response = self.send_message(user_input)
                
                if ai_response:
                    print(f"🤖 AI: {ai_response}")
                    
                    # Text-to-speech if enabled
                    if use_tts and self.speech_handler:
                        print("🔊 Speaking response...")
                        if self.speech_handler.speak_text(ai_response):
                            print("✓ Response spoken successfully")
                        else:
                            print("✗ Failed to speak response")
                    
                    # Save to file if specified
                    if save_file:
                        self._save_to_file(user_input, ai_response, save_file)
                else:
                    print("❌ Failed to get response from backend")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                break
            except EOFError:
                print("\n\n👋 End of input")
                break
        
        # Final summary
        print(f"\n📊 Conversation Summary:")
        print(f"   Messages exchanged: {len(self.conversation_history)}")
        print(f"   Session ID: {self.session_id}")
        if save_file:
            print(f"   Saved to: {save_file}")
    
    def _show_help(self):
        """Show available commands."""
        print("\n📚 Available Commands:")
        print("  help     - Show this help message")
        print("  history  - Show conversation history")
        print("  status   - Show connection status")
        print("  clear    - Clear local conversation history")
        print("  quit/exit/bye - End conversation")
    
    def _show_history(self):
        """Show conversation history."""
        if not self.conversation_history:
            print("📝 No local conversation history")
            return
        
        print(f"\n📝 Local Conversation History ({len(self.conversation_history)} messages):")
        for i, conv in enumerate(self.conversation_history, 1):
            timestamp = conv['timestamp'].strftime('%H:%M:%S')
            print(f"  {i}. [{timestamp}] You: {conv['user']}")
            print(f"     [{timestamp}] AI:  {conv['ai']}")
            print()
    
    def _show_status(self):
        """Show connection and feature status."""
        print(f"\n📊 Status:")
        print(f"  Backend URL: {self.base_url}")
        print(f"  Session ID: {self.session_id}")
        print(f"  Speech Available: {'Yes' if SPEECH_AVAILABLE else 'No'}")
        print(f"  Speech Handler: {'Active' if self.speech_handler else 'Inactive'}")
        print(f"  Local Messages: {len(self.conversation_history)}")
        
        # Test backend connection
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"  Backend Status: {health_data.get('status', 'Unknown')}")
                print(f"  MongoDB: {health_data.get('mongodb', 'Unknown')}")
                print(f"  OpenAI: {health_data.get('openai', 'Unknown')}")
            else:
                print(f"  Backend Status: HTTP {response.status_code}")
        except:
            print("  Backend Status: Connection failed")
    
    def _save_to_file(self, user_msg: str, ai_msg: str, filename: str):
        """Save conversation to file."""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] User: {user_msg}\n")
                f.write(f"[{timestamp}] AI: {ai_msg}\n")
                f.write("-" * 50 + "\n")
        except Exception as e:
            print(f"⚠️  Failed to save to file: {e}")

def main():
    """Main entry point for the client application."""
    parser = argparse.ArgumentParser(
        description="Conversational Agent Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python client.py                    # Text-based chat
  python client.py --mic             # Use microphone for input
  python client.py --tts             # Speak AI responses aloud
  python client.py --mic --tts       # Full speech interaction
  python client.py --save chat.txt   # Save conversation to file
  python client.py --url http://192.168.1.100:5000  # Custom backend URL
        """
    )
    
    parser.add_argument('--url', default='http://localhost:5000',
                       help='Backend URL (default: http://localhost:5000)')
    parser.add_argument('--session', help='Custom session ID')
    parser.add_argument('--mic', action='store_true',
                       help='Use microphone for speech input')
    parser.add_argument('--tts', action='store_true',
                       help='Use text-to-speech for AI responses')
    parser.add_argument('--offline-tts', action='store_true',
                       help='Use offline TTS (pyttsx3) instead of online (gTTS)')
    parser.add_argument('--save', metavar='FILE',
                       help='Save conversation to specified file')
    parser.add_argument('--test-speech', action='store_true',
                       help='Test speech features and exit')
    
    args = parser.parse_args()
    
    # Test speech features if requested
    if args.test_speech:
        if not SPEECH_AVAILABLE:
            print("❌ Speech features not available")
            sys.exit(1)
        
        print("🧪 Testing Speech Features...")
        handler = SpeechHandler(use_offline_tts=args.offline_tts)
        
        # Test microphone
        if handler.test_microphone():
            print("✓ Microphone test passed")
            
            # Test speech recognition
            print("\n🎤 Speak something when prompted...")
            success, result = handler.listen_to_mic()
            if success:
                print(f"✓ Speech recognition: {result}")
                
                # Test TTS
                print("\n🔊 Testing text-to-speech...")
                if handler.speak_text("Speech test successful!"):
                    print("✓ TTS test passed")
                else:
                    print("✗ TTS test failed")
            else:
                print(f"✗ Speech recognition failed: {result}")
        else:
            print("✗ Microphone test failed")
        
        sys.exit(0)
    
    # Create and run client
    try:
        client = ChatClient(base_url=args.url, session_id=args.session)
        
        # Update speech handler if offline TTS requested
        if args.offline_tts and client.speech_handler:
            try:
                client.speech_handler = SpeechHandler(use_offline_tts=True)
                print("✓ Offline TTS enabled")
            except Exception as e:
                print(f"Warning: Failed to enable offline TTS: {e}")
        
        # Start chat loop
        client.chat_loop(
            use_mic=args.mic,
            use_tts=args.tts,
            save_file=args.save
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Client stopped by user")
    except Exception as e:
        print(f"❌ Client error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
