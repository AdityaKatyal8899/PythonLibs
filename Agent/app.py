from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import openai
import os
from dotenv import load_dotenv
from bson import ObjectId
import json
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'conversational_agent')
COLLECTION_NAME = 'conversations'

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# Initialize MongoDB client
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    conversations = db[COLLECTION_NAME]
    # Create index on session_id for better query performance
    conversations.create_index("session_id")
    print("MongoDB connected successfully")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    client = None

# Initialize OpenAI client
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    print("OpenAI API key loaded successfully")
else:
    print("Warning: OpenAI API key not found")

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat messages:
    1. Save user message to DB
    2. Fetch conversation history
    3. Send to OpenAI API
    4. Save agent response
    5. Return response
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data or 'session_id' not in data or 'message' not in data:
            return jsonify({'error': 'Missing session_id or message'}), 400
        
        session_id = data['session_id']
        user_message = data['message']
        
        if not session_id or not user_message:
            return jsonify({'error': 'session_id and message cannot be empty'}), 400
        
        # Check if MongoDB is connected
        if not client:
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Check if OpenAI is configured
        if not OPENAI_API_KEY:
            return jsonify({'error': 'OpenAI API not configured'}), 500
        
        # Save user message to database
        user_msg_doc = {
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow()
        }
        
        # Update or create conversation document
        conversations.update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": user_msg_doc},
                "$setOnInsert": {"session_id": session_id, "timestamp": datetime.utcnow()}
            },
            upsert=True
        )
        
        # Fetch last 10 messages for context
        conversation_doc = conversations.find_one({"session_id": session_id})
        if not conversation_doc:
            return jsonify({'error': 'Failed to retrieve conversation'}), 500
        
        # Get last 10 messages and format for OpenAI API
        recent_messages = conversation_doc['messages'][-10:]
        openai_messages = []
        
        for msg in recent_messages:
            # Convert 'agent' role to 'assistant' for OpenAI API
            role = 'assistant' if msg['role'] == 'agent' else msg['role']
            openai_messages.append({
                "role": role,
                "content": msg['content']
            })
        
        # Call OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=openai_messages,
                max_tokens=500,
                temperature=0.7
            )
            
            agent_response = response.choices[0].message.content
            
        except Exception as e:
            return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500
        
        # Save agent response to database
        agent_msg_doc = {
            "role": "agent",
            "content": agent_response,
            "timestamp": datetime.utcnow()
        }
        
        conversations.update_one(
            {"session_id": session_id},
            {"$push": {"messages": agent_msg_doc}}
        )
        
        return jsonify({
            'session_id': session_id,
            'response': agent_response,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """
    Retrieve full conversation history for a session
    """
    try:
        if not client:
            return jsonify({'error': 'Database connection failed'}), 500
        
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400
        
        # Find conversation document
        conversation_doc = conversations.find_one({"session_id": session_id})
        
        if not conversation_doc:
            return jsonify({'error': 'Session not found'}), 404
        
        # Format response
        history = {
            'session_id': session_id,
            'timestamp': conversation_doc.get('timestamp', '').isoformat() if conversation_doc.get('timestamp') else None,
            'messages': conversation_doc.get('messages', [])
        }
        
        # Convert ObjectId to string for JSON serialization
        if '_id' in conversation_doc:
            history['_id'] = str(conversation_doc['_id'])
        
        return jsonify(history)
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    try:
        # Check MongoDB connection
        mongo_status = "connected" if client and client.admin.command('ping') else "disconnected"
        
        # Check OpenAI configuration
        openai_status = "configured" if OPENAI_API_KEY else "not configured"
        
        return jsonify({
            'status': 'healthy',
            'mongodb': mongo_status,
            'openai': openai_status,
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

if __name__ == '__main__':
    # Check required environment variables
    if not OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY not set. Chat functionality will not work.")
    
    if not MONGO_URI or MONGO_URI == 'mongodb://localhost:27017/':
        print("Warning: Using default MongoDB URI. Set MONGO_URI environment variable for production.")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
