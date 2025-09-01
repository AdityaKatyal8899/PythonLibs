
# Conversational Agent - Full Stack Project

A complete conversational AI system with a Flask backend, MongoDB integration, OpenAI API, and an optional speech-enabled client.

## 🚀 Features

### Backend (Flask + MongoDB + OpenAI)
- **Chat API**: RESTful `/chat` endpoint for AI conversations
- **Persistent Storage**: MongoDB integration for conversation history
- **AI Integration**: OpenAI GPT-4o-mini powered responses
- **Session Management**: Unique session IDs for different users
- **Health Monitoring**: Built-in health check endpoints

### Client (CLI + Speech)
- **Command Line Interface**: Easy-to-use text-based chat
- **Speech Input**: Microphone support for hands-free interaction
- **Text-to-Speech**: AI responses can be spoken aloud
- **Conversation Logging**: Save chats to files
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Speech Capabilities
- **Speech-to-Text**: Google Speech Recognition API
- **Text-to-Speech**: gTTS (online) or pyttsx3 (offline)
- **Microphone Testing**: Built-in audio device testing
- **Flexible Configuration**: Choose between online/offline TTS

## 📁 Project Structure

```
project/
├── app.py              # Flask backend (MongoDB + OpenAI)
├── client.py           # CLI client with speech features
├── speech_utils.py     # STT/TTS utilities
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
└── SETUP.md           # Detailed setup guide
```

## 🛠️ Quick Setup

### 1. Environment Configuration
Create a `.env` file:
```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=conversational_agent
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Backend
```bash
python app.py
```

### 4. Use Client
```bash
# Basic text chat
python client.py

# Full speech interaction
python client.py --mic --tts

# Save conversation
python client.py --save chat.txt
```

## 🎯 Usage Examples

### Basic Chat Session
```bash
# Terminal 1: Start backend
python app.py

# Terminal 2: Start client
python client.py
```

### Speech-Enabled Interaction
```bash
# Use microphone for input
python client.py --mic

# Speak AI responses aloud
python client.py --tts

# Full speech interaction
python client.py --mic --tts

# Offline TTS (no internet for speech)
python client.py --mic --tts --offline-tts
```

### Advanced Features
```bash
# Custom backend URL
python client.py --url http://192.168.1.100:5000

# Custom session ID
python client.py --session user123

# Save conversation to file
python client.py --save my_chat.txt

# Test speech features
python client.py --test-speech
```

## 🔧 API Endpoints

### POST /chat
Send a message and get AI response.
```json
{
  "session_id": "user123",
  "message": "Hello, how are you?"
}
```

### GET /history/<session_id>
Retrieve conversation history.

### GET /health
Check system health and status.

## 🎤 Speech Features

### Speech-to-Text (STT)
- Uses Google Speech Recognition API
- Automatic noise adjustment
- Configurable timeout and phrase limits
- Cross-platform microphone support

### Text-to-Speech (TTS)
- **Online**: gTTS with natural-sounding voices
- **Offline**: pyttsx3 for internet-free operation
- Automatic audio playback
- Temporary file management

## 🐛 Troubleshooting

### Speech Issues
- **Microphone not working**: Run `python client.py --test-speech`
- **PyAudio installation**: Use `pipwin install pyaudio` on Windows
- **Internet required**: Google STT needs internet connection

### Backend Issues
- **Connection failed**: Ensure MongoDB is running
- **API errors**: Check OpenAI API key and rate limits
- **Port conflicts**: Verify port 5000 is available

## 🚀 Production Deployment

1. **Environment**: Set production environment variables
2. **WSGI Server**: Use Gunicorn or uWSGI
3. **MongoDB**: Production instance with authentication
4. **Security**: HTTPS, rate limiting, authentication
5. **Monitoring**: Logging and health checks

## 📚 Dependencies

### Core
- `Flask`: Web framework
- `pymongo`: MongoDB driver
- `openai`: OpenAI API client
- `python-dotenv`: Environment management

### Speech
- `SpeechRecognition`: Speech-to-text
- `gTTS`: Google Text-to-Speech
- `pyttsx3`: Offline text-to-speech
- `PyAudio`: Audio input/output

### Utilities
- `requests`: HTTP client
- `Werkzeug`: WSGI utilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

- Check the [SETUP.md](SETUP.md) for detailed configuration
- Test individual components separately
- Verify environment variables are set correctly
- Ensure all dependencies are installed

---

**Happy chatting! 🎉**
