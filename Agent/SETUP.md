# Setup Guide for Conversational Agent Project

## Quick Start

### 1. Environment Setup

Create a `.env` file in the project root with the following variables:

```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
DB_NAME=conversational_agent

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Flask Configuration (optional)
FLASK_ENV=development
FLASK_DEBUG=true
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** On Windows, you might need to install PyAudio separately:
```bash
pip install pipwin
pipwin install pyaudio
```

### 3. Start the Backend

```bash
python app.py
```

The Flask server will start on `http://localhost:5000`

### 4. Test the Client

#### Basic Text Chat
```bash
python client.py
```

#### Speech-Enabled Chat
```bash
# Use microphone for input
python client.py --mic

# Use text-to-speech for responses
python client.py --tts

# Full speech interaction
python client.py --mic --tts

# Save conversation to file
python client.py --save conversation.txt

# Test speech features
python client.py --test-speech
```

## Project Structure

```
project/
├── app.py              # Flask backend with MongoDB + OpenAI
├── client.py           # CLI client with optional speech features
├── speech_utils.py     # STT/TTS utilities
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
└── SETUP.md           # This setup guide
```

## Features

### Backend (app.py)
- ✅ Flask REST API with `/chat` endpoint
- ✅ MongoDB integration for conversation storage
- ✅ OpenAI API integration (GPT-4o-mini)
- ✅ Session management
- ✅ Health check endpoint
- ✅ Error handling and validation

### Client (client.py)
- ✅ Command-line interface
- ✅ Optional speech input (microphone)
- ✅ Optional text-to-speech output
- ✅ Conversation history
- ✅ File logging
- ✅ Custom backend URL support
- ✅ Session management

### Speech Utils (speech_utils.py)
- ✅ Speech-to-Text (STT) using Google Speech Recognition
- ✅ Text-to-Speech (TTS) using gTTS (online) or pyttsx3 (offline)
- ✅ Microphone testing and configuration
- ✅ Cross-platform audio playback

## Usage Examples

### Basic Chat Session
```bash
# Terminal 1: Start backend
python app.py

# Terminal 2: Start client
python client.py
```

### Speech-Enabled Session
```bash
# Full speech interaction
python client.py --mic --tts

# Offline TTS (no internet required for speech output)
python client.py --mic --tts --offline-tts
```

### Custom Configuration
```bash
# Connect to remote backend
python client.py --url http://192.168.1.100:5000

# Custom session ID
python client.py --session user123

# Save conversation
python client.py --save my_chat.txt
```

## Troubleshooting

### Speech Recognition Issues
1. **Microphone not working**: Run `python client.py --test-speech`
2. **PyAudio installation**: Use `pipwin install pyaudio` on Windows
3. **Internet required**: Google Speech Recognition needs internet connection

### Backend Connection Issues
1. **Check if backend is running**: `python app.py`
2. **Verify MongoDB**: Ensure MongoDB service is running
3. **Check environment variables**: Verify `.env` file exists and has correct values

### OpenAI API Issues
1. **API key**: Ensure `OPENAI_API_KEY` is set in `.env`
2. **Rate limits**: Check OpenAI usage dashboard
3. **Model availability**: Verify model name in `.env`

## Development

### Adding New Features
- **Backend**: Modify `app.py` for new endpoints
- **Client**: Extend `client.py` for new client features
- **Speech**: Enhance `speech_utils.py` for new speech capabilities

### Testing
```bash
# Test speech features
python client.py --test-speech

# Test backend health
curl http://localhost:5000/health

# Test chat endpoint
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": "Hello"}'
```

## Production Deployment

1. **Environment**: Set `FLASK_ENV=production` and `FLASK_DEBUG=false`
2. **WSGI Server**: Use Gunicorn or uWSGI instead of Flask development server
3. **MongoDB**: Use production MongoDB instance with authentication
4. **Security**: Implement rate limiting, authentication, and HTTPS
5. **Monitoring**: Add logging and health monitoring

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure environment variables are set properly
4. Test individual components separately
