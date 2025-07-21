import os
import uuid
import requests
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

# Store active sessions (in production, use Redis or database)
active_sessions = {}

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
        active_sessions[chat_id] = {
            "token": token,
            "session_id": session_id,
            "sequence_id": 1
        }
        
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
        data = request.json
        chat_id = data.get('chat_id')
        message = data.get('message')
        
        if not chat_id or not message:
            return jsonify({"success": False, "error": "Missing chat_id or message"}), 400
            
        if chat_id not in active_sessions:
            return jsonify({"success": False, "error": "Invalid chat session"}), 400
            
        session_info = active_sessions[chat_id]
        
        # Send message to agent
        response = send_message(
            session_info["token"],
            session_info["session_id"], 
            message,
            session_info["sequence_id"]
        )
        
        # Update sequence ID
        session_info["sequence_id"] += 1
        
        # Extract agent response
        messages = response.get("messages", [])
        agent_reply = messages[-1]["message"] if messages else "I'm sorry, I couldn't process that request."
        
        return jsonify({
            "success": True,
            "reply": agent_reply
        })
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/end-chat', methods=['POST'])
def end_chat():
    """End a chat session"""
    try:
        data = request.json
        chat_id = data.get('chat_id')
        
        if chat_id and chat_id in active_sessions:
            session_info = active_sessions[chat_id]
            end_session(session_info["token"], session_info["session_id"])
            del active_sessions[chat_id]
            
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"Error ending chat: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Use PORT environment variable if available (for Heroku), otherwise default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 