import os
import uuid
import requests
import json
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 🧠 Load environment variables
SF_DOMAIN = os.getenv("SF_DOMAIN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AGENT_ID = os.getenv("AGENT_ID")
API_HOST = "https://api.salesforce.com"

if not all([SF_DOMAIN, CLIENT_ID, CLIENT_SECRET, AGENT_ID]):
    raise EnvironmentError("❗️ Ensure SF_DOMAIN, CLIENT_ID, CLIENT_SECRET, and AGENT_ID are set.")

# Global token storage (in production, use proper session management)
_token_cache = {"token": None, "expires_at": None}

def get_token():
    """Retrieve OAuth token from Salesforce"""
    token_url = f"{SF_DOMAIN}/services/oauth2/token"
    resp = requests.post(token_url,
                         headers={"Content-Type": "application/x-www-form-urlencoded"},
                         data={
                             "grant_type": "client_credentials",
                             "client_id": CLIENT_ID,
                             "client_secret": CLIENT_SECRET
                         })
    logger.info(f"Token status: {resp.status_code}")
    resp.raise_for_status()
    return resp.json()["access_token"]

def start_session(token):
    """Start a new agent session"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {
        "externalSessionKey": str(uuid.uuid4()),
        "instanceConfig": {"endpoint": SF_DOMAIN},
        "streamingCapabilities": {"chunkTypes": ["Text"]},
        "bypassUser": True
    }
    url = f"{API_HOST}/einstein/ai-agent/v1/agents/{AGENT_ID}/sessions"
    resp = requests.post(url, headers=headers, json=body)
    logger.info(f"Start session status: {resp.status_code}")
    resp.raise_for_status()
    return resp.json()

def send_message(token, session_id, message_text, sequence_id=1):
    """Send a message to the agent"""
    payload = {
        "message": {
            "sequenceId": sequence_id,
            "type": "Text", 
            "text": message_text
        },
        "variables": []
    }
    url = f"{API_HOST}/einstein/ai-agent/v1/sessions/{session_id}/messages"
    
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload
    )
    logger.info(f"Send message status: {resp.status_code}")
    resp.raise_for_status()
    return resp.json()

def end_session(token, session_id):
    """End an agent session"""
    resp = requests.delete(
        f"{API_HOST}/einstein/ai-agent/v1/sessions/{session_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "x-session-end-reason": "UserRequest"
        }
    )
    logger.info(f"End session status: {resp.status_code}")
    return resp.status_code == 200

# Store active sessions - using a simple file-based approach for Heroku

# Create a shared session file in /tmp (persists across workers but not restarts)
SESSION_FILE = "/tmp/chat_sessions.json"

def load_sessions():
    """Load sessions from shared file"""
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load sessions: {e}")
    return {}

def save_sessions(sessions):
    """Save sessions to shared file"""
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump(sessions, f)
    except Exception as e:
        logger.error(f"Could not save sessions: {e}")

def get_active_sessions():
    """Get current active sessions"""
    return load_sessions()

def add_session(chat_id, session_info):
    """Add a new session"""
    sessions = load_sessions()
    sessions[chat_id] = session_info
    save_sessions(sessions)

def remove_session(chat_id):
    """Remove a session"""
    sessions = load_sessions()
    if chat_id in sessions:
        del sessions[chat_id]
        save_sessions(sessions)

def get_session(chat_id):
    """Get a specific session"""
    sessions = load_sessions()
    return sessions.get(chat_id)

@app.route('/')
def index():
    """Serve the chat interface"""
    return render_template('chat.html')

@app.route('/api/start-chat', methods=['POST'])
def start_chat():
    """Initialize a new chat session"""
    try:
        # Get token
        token = get_token()
        
        # Start session
        session_data = start_session(token)
        session_id = session_data["sessionId"]
        
        # Store session info
        chat_id = str(uuid.uuid4())
        session_info = {
            "token": token,
            "session_id": session_id,
            "sequence_id": 1
        }
        add_session(chat_id, session_info)
        
        logger.info(f"Created new chat session: {chat_id}")
        
        # Get initial message from agent
        initial_message = session_data.get("messages", [{}])[0].get("message", "Hello! How can I help you today?")
        
        return jsonify({
            "success": True,
            "chat_id": chat_id,
            "initial_message": initial_message
        })
        
    except Exception as e:
        logger.error(f"Error starting chat: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/send-message', methods=['POST'])
def send_message_api():
    """Send a message to the agent"""
    try:
        # Handle case where request.json is None
        if not request.is_json:
            logger.error("Request is not JSON")
            return jsonify({"success": False, "error": "Request must be JSON"}), 400
            
        data = request.get_json()
        logger.info(f"Received request data: {data}")
        
        if not data:
            logger.error("No JSON data received")
            return jsonify({"success": False, "error": "No data received"}), 400
            
        chat_id = data.get('chat_id')
        message = data.get('message')
        
        logger.info(f"chat_id: {chat_id}, message: {message}")
        
        if not chat_id or not message:
            logger.error(f"Missing required fields - chat_id: {chat_id}, message: {message}")
            return jsonify({"success": False, "error": "Missing chat_id or message"}), 400
            
        session_info = get_session(chat_id)
        if not session_info:
            all_sessions = list(get_active_sessions().keys())
            logger.error(f"Chat session not found. chat_id: {chat_id}, active_sessions: {all_sessions}")
            return jsonify({"success": False, "error": "Invalid chat session"}), 400
        
        # Send message to agent
        response = send_message(
            session_info["token"],
            session_info["session_id"], 
            message,
            session_info["sequence_id"]
        )
        
        # Update sequence ID and save back
        session_info["sequence_id"] += 1
        add_session(chat_id, session_info)
        
        # Extract agent response
        messages = response.get("messages", [])
        agent_reply = messages[-1]["message"] if messages else "I'm sorry, I couldn't process that request."
        
        return jsonify({
            "success": True,
            "reply": agent_reply
        })
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/end-chat', methods=['POST'])
def end_chat():
    """End a chat session"""
    try:
        data = request.get_json() if request.is_json else {}
        chat_id = data.get('chat_id')
        
        session_info = get_session(chat_id) if chat_id else None
        if session_info:
            end_session(session_info["token"], session_info["session_id"])
            remove_session(chat_id)
            logger.info(f"Ended chat session: {chat_id}")
            
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"Error ending chat: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Use PORT environment variable if available (for Heroku), otherwise default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 