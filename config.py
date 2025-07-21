import os
import requests

def get_access_token():
    domain = os.getenv("SF_DOMAIN")
    cid = os.getenv("CLIENT_ID")
    cs = os.getenv("CLIENT_SECRET")
    token_url = f"{domain}/services/oauth2/token"

    resp = requests.post(token_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": cid,
            "client_secret": cs
        }
    )
    resp.raise_for_status()
    return domain, resp.json()["access_token"]
