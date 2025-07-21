# main.py
import os
import uuid
import requests

# 🧠 Load environment variables
SF_DOMAIN = os.getenv("SF_DOMAIN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AGENT_ID = os.getenv("AGENT_ID")
API_HOST = "https://api.salesforce.com"

if not all([SF_DOMAIN, CLIENT_ID, CLIENT_SECRET, AGENT_ID]):
    raise EnvironmentError("❗️ Ensure SF_DOMAIN, CLIENT_ID, CLIENT_SECRET, and AGENT_ID are set.")

# 1️⃣ Retrieve OAuth token
def get_token():
    token_url = f"{SF_DOMAIN}/services/oauth2/token"
    resp = requests.post(token_url,
                         headers={"Content-Type": "application/x-www-form-urlencoded"},
                         data={
                             "grant_type": "client_credentials",
                             "client_id": CLIENT_ID,
                             "client_secret": CLIENT_SECRET
                         })
    print("Token status:", resp.status_code, "| body:", resp.text[:200] + "…")
    resp.raise_for_status()
    return resp.json()["access_token"]

token = get_token()
print("✅ Token retrieved")

# 2️⃣ Start Agent session
def start_session():
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {
        "externalSessionKey": str(uuid.uuid4()),
        "instanceConfig": {"endpoint": SF_DOMAIN},
        "streamingCapabilities": {"chunkTypes": ["Text"]},
        "bypassUser": True
    }
    url = f"{API_HOST}/einstein/ai-agent/v1/agents/{AGENT_ID}/sessions"
    resp = requests.post(url, headers=headers, json=body)
    print("Start session:", resp.status_code, "| body:", resp.text[:200] + "…")
    resp.raise_for_status()
    return resp.json()

session_data = start_session()
session_id = session_data["sessionId"]
print("✅ Session started:", session_id)
print("Initial message:", session_data.get("messages")[0]["message"])

# 3️⃣ Send test message with correct payload schema
sequence_id = 1  # Initialize sequence number
payload = {
    "message": {
        "sequenceId": sequence_id,
        "type": "Text",
        "text": "Can you tell me about product pricing?"
    },
    "variables": []  # Optional: include as per API specs :contentReference[oaicite:2]{index=2}
}
url_msg = f"{API_HOST}/einstein/ai-agent/v1/sessions/{session_id}/messages"

try:
    resp = requests.post(
        url_msg,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload
    )
    print("Send msg status:", resp.status_code, "| body:", resp.text[:200] + "…")
    resp.raise_for_status()
    messages = resp.json().get("messages", [])
    print("🤖 Agent replies:", messages[-1]["message"])
except Exception as e:
    print("⚠️ Sending message failed. See details above.")
    raise

# existing token fetch, start_session, send message same as before

# 4️⃣ Properly end the session
resp = requests.delete(
    f"{API_HOST}/einstein/ai-agent/v1/sessions/{session_id}",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-session-end-reason": "UserRequest"
    }
)
print("Session closed, status:", resp.status_code)
print("Body:", resp.text)
print("✅ Done.")

