from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from bson import ObjectId
import json
from flask_cors import CORS

# ✅ Correct Gemini import
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# Database setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["ChatApp"]
conversations = db["conversations"]

# Gemini setup
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"

chat_model = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=0.7,
    google_api_key=GOOGLE_API_KEY
)

# ✅ Custom JSON Encoder for ObjectId and datetime
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = JSONEncoder

# Root endpoint
@app.route("/")
def home():
    return jsonify({"message": "Welcome to Flask Backend!"})

# Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    session_id = data.get("session_id")
    user_message = data.get("message", "")

    if not session_id or not user_message:
        return jsonify({"error": "session_id and message are required"}), 400

    # Push user message into the session document
    user_msg_doc = {
        "role": "user",
        "content": user_message,
        "timestamp": datetime.utcnow()
    }
    conversations.update_one(
        {"session_id": session_id},
        {"$push": {"messages": user_msg_doc},
         "$setOnInsert": {"session_id": session_id, "created_at": datetime.utcnow()}},
        upsert=True
    )

    # Fetch last 10 messages for context
    conversation_doc = conversations.find_one({"session_id": session_id})
    recent_messages = conversation_doc.get("messages", [])[-10:]

    # Convert messages to LangChain format
    history = []
    for msg in recent_messages:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        else:
            history.append(SystemMessage(content=msg["content"]))

    # Generate response using Gemini
    try:
        agent_message = chat_model.invoke(history)
        agent_response = agent_message.content
    except Exception as e:
        print("GenAI invocation error:", e)
        agent_response = "Sorry, I am having trouble generating a response."

    # Push agent response into the same session document
    agent_msg_doc = {
        "role": "assistant",
        "content": agent_response,
        "timestamp": datetime.utcnow()
    }
    conversations.update_one(
        {"session_id": session_id},
        {"$push": {"messages": agent_msg_doc}}
    )

    return jsonify({"response": agent_response})

# Fetch conversation by session
@app.route("/messages/<session_id>", methods=["GET"])
def get_messages(session_id):
    conversation_doc = conversations.find_one({"session_id": session_id})
    if not conversation_doc:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(conversation_doc)

# Clear a session's messages
@app.route("/clear/<session_id>", methods=["POST"])
def clear_messages(session_id):
    conversations.delete_one({"session_id": session_id})
    return jsonify({"message": f"Session {session_id} cleared!"})

# Health check
@app.route("/health", methods=["GET"])
def health():
    try:
        client.admin.command('ping')
        mongo_status = "connected"
    except Exception as e:
        mongo_status = f"disconnected ({str(e)})"

    gemini_status = "configured" if GOOGLE_API_KEY else "not configured"

    return jsonify({
        "status": "connected" if mongo_status == "connected" else "disconnected",
        "mongodb": mongo_status,
        "openai": gemini_status,  # points to Gemini for frontend
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    app.run(debug=True)
