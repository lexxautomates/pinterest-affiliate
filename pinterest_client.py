"""Direct Pinterest v5 REST client (works even before MCP restart).

Token source: env PINTEREST_ACCESS_TOKEN, else ~/.pinterest-mcp/token.json
(written by D:/repos/pinterest-mcp/auth.js after one-time OAuth).
"""
import json
import os
import urllib.request
import urllib.error

API = "https://api.pinterest.com/v5"
TOKEN_PATH = os.path.join(os.path.expanduser("~"), ".pinterest-mcp", "token.json")


def load_token(explicit=None):
    if explicit:
        return explicit
    if os.environ.get("PINTEREST_ACCESS_TOKEN"):
        return os.environ["PINTEREST_ACCESS_TOKEN"]
    try:
        return json.load(open(TOKEN_PATH))["access_token"]
    except Exception:
        return None


class PinterestClient:
    def __init__(self, token=None):
        self.token = load_token(token)

    def _req(self, method, sub, body=None):
        if not self.token:
            return {"error": "NO_TOKEN: set PINTEREST_ACCESS_TOKEN or run auth.js"}
        url = API + sub
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            return {"error": f"{e.code} {e.read().decode()[:400]}"}

    def get_user(self):
        return self._req("GET", "/user_account")

    def list_boards(self):
        return self._req("GET", "/boards")

    def create_pin(self, board_id, title, description, link, image_base64, content_type="image/png"):
        body = {
            "board_id": board_id,
            "title": title,
            "description": description,
            "link": link,
            "media_source": {
                "source_type": "image_base64",
                "base64": image_base64,
                "content_type": content_type,
            },
        }
        return self._req("POST", "/pins", body)

    def get_pin_analytics(self, pin_id, start="2024-01-01", end="2026-12-31"):
        sub = (
            f"/pins/{pin_id}/analytics"
            f"?metric_types=IMPRESSION,ENGAGEMENT,SAVE,CLICK,CLOSEUP"
            f"&start_date={start}&end_date={end}"
        )
        return self._req("GET", sub)
