from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import genai
import os
from dotenv import load_dotenv
from flask_cors import CORS

# -------------------------
# Load .env reliably on Windows
# -------------------------
# Replace with the full path to your .env file
dotenv_path = r"C:\Users\AdityaJi\Agent\.env"
load_dotenv(dotenv_path)

# Fetch environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gpt-4o-mini")
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'conversational_agent')

print("Loaded GEMINI_API_KEY:", GEMINI_API_KEY)
print("MongoDB URI:", MONGO_URI)

# -------------------------
# Configure GenAI
# -------------------------
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini API key loaded successfully")
else:
    print("Warning: GEMINI_API_KEY not found")

# -------------------------
# Initialize Flask & CORS
# -------------------------
app = Flask(__name__)
CORS(app)

# -------------------------
# Initialize MongoDB
# -------------------------
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    conversations = db['conversations']
    conversations.create_index("session_id")
    print("MongoDB connected successfully")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    client = None

# -------------------------
# Utility to serialize documents
# -------------------------
def serialize_doc(doc):
    if not doc:
        return None
    doc_copy = dict(doc)
    doc_copy['_id'] = str(doc_copy['_id'])
    for msg in doc_copy.get('messages', []):
        if 'timestamp' in msg and isinstance(msg['timestamp'], datetime):
            msg['timestamp'] = msg['timestamp'].isoformat()
    if 'timestamp' in doc_copy and isinstance(doc_copy['timestamp'], datetime):
        doc_copy['timestamp'] = doc_copy['timestamp'].isoformat()
    return doc_copy

# -------------------------
# Routes
# -------------------------
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'session_id' not in data or 'message' not in data:
            return jsonify({'error': 'Missing session_id or message'}), 400
        
        session_id = data['session_id']
        user_message = data['message']
        if not session_id or not user_message:
            return jsonify({'error': 'session_id and message cannot be empty'}), 400
        
        if not client:
            return jsonify({'error': 'Database connection failed'}), 500
        if not GEMINI_API_KEY:
            return jsonify({'error': 'Gemini API not configured'}), 500
        
        # Save user message
        user_msg_doc = {
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow()
        }
        conversations.update_one(
            {"session_id": session_id},
            {"$push": {"messages": user_msg_doc},
             "$setOnInsert": {"session_id": session_id, "timestamp": datetime.utcnow()}},
            upsert=True
        )
        
        # Fetch last 10 messages
        conversation_doc = conversations.find_one({"session_id": session_id})
        if not conversation_doc:
            return jsonify({'error': 'Failed to retrieve conversation'}), 500
        
        recent_messages = conversation_doc['messages'][-10:]
        genai_messages = [{"role": "assistant" if msg['role']=='agent' else msg['role'], "content": msg['content']} for msg in recent_messages]
        
        # Call GenAI
        try:
            response = genai.chat.create(
                model=GEMINI_MODEL,
                messages=genai_messages,
                max_output_tokens=500,
                temperature=0.7
            )
            agent_response = response.output_text
        except Exception as e:
            return jsonify({'error': f'GenAI API error: {str(e)}'}), 500
        
        # Save agent response
        agent_msg_doc = {
            "role": "agent",
            "content": agent_response,
            "timestamp": datetime.utcnow()
        }
        conversations.update_one({"session_id": session_id}, {"$push": {"messages": agent_msg_doc}})
        
        return jsonify({
            'session_id': session_id,
            'response': agent_response,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    try:
        if not client:
            return jsonify({'error': 'Database connection failed'}), 500
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400
        
        conversation_doc = conversations.find_one({"session_id": session_id})
        if not conversation_doc:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify(serialize_doc(conversation_doc))
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    try:
        mongo_status = "connected" if client and client.admin.command('ping') else "disconnected"
        gemini_status = "configured" if GEMINI_API_KEY else "not configured"
        return jsonify({
            'status': 'healthy',
            'mongodb': mongo_status,
            'gemini': gemini_status,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# -------------------------
# Main entry
# -------------------------
if __name__ == '__main__':
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set. Chat functionality will not work.")
    if not MONGO_URI or MONGO_URI == 'mongodb://localhost:27017/':
        print("Warning: Using default MongoDB URI. Set MONGO_URI environment variable for production.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
