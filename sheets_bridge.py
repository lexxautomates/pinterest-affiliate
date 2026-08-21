"""Google Sheets bulk-create interface for Pinterest pins (Drive-scope version).

The Hermes google_token currently grants DRIVE + PHOTOS scopes (no Sheets
scope), so we create/update the spreadsheet via the DRIVE API (a
application/vnd.google.apps.spreadsheet file). It opens as a fully editable
Google Sheet in the browser. Cell-level append would need Sheets scope — for
now we re-upload the whole sheet content (Drive update), which is fine for a
monthly bulk plan.

Sheets columns:
  Title | Media URL | Pinterest board | Description | Link | Publish date | Keywords | APPROVED | STATUS

To enable true append/sync without re-upload, re-auth the Hermes Google token
with the Sheets scope (one-time human step) — then switch _client to gspread.
"""
import os
import io
import csv
import json
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.path.expanduser("~/AppData/Local/hermes/google_token.json")
SECRET = os.path.expanduser("~/AppData/Local/hermes/google_client_secret.json")
SHEET_TITLE = "Pinterest Amazon Bulk Pins"
CSV_OUT = os.path.join(HERE, "bulk_upload.csv")
HEADERS = ["Title", "Media URL", "Pinterest board", "Description", "Link",
           "Publish date", "Keywords", "APPROVED", "STATUS"]
DISCLOSURE = "As an Amazon Associate, I earn from qualifying purchases."


def _creds():
    t = json.load(open(TOKEN))
    s = json.load(open(SECRET))
    return Credentials(
        token=t.get("token"), refresh_token=t.get("refresh_token"),
        token_uri=t.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=s["installed"]["client_id"], client_secret=s["installed"]["client_secret"],
        scopes=t.get("scopes"),
    )


def _drive():
    return build("drive", "v3", credentials=_creds())


def _find(title=SHEET_TITLE):
    d = _drive()
    q = f"name='{title}' and mimeType='application/vnd.google.apps.spreadsheet' and trashed=false"
    res = d.files().list(q=q, fields="files(id,name,webViewLink)").execute()
    return res.get("files", [])[0] if res.get("files") else None


def build_rows(pins):
    rows = []
    for p in pins:
        rows.append([
            p["title"][:100], p["media_url"], p["board"], p["description"][:500],
            p["link"], p.get("publish_date", ""), p["keywords"], "NO", "ready",
        ])
    return rows


def sync_sheet(pins, title=SHEET_TITLE):
    d = _drive()
    csv_buf = io.StringIO()
    w = csv.writer(csv_buf)
    w.writerow(HEADERS)
    w.writerows(build_rows(pins))
    data = csv_buf.getvalue().encode("utf-8")
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype="text/csv", resumable=True)
    existing = _find(title)
    if existing:
        # update keeps current mimeType (sheets); re-upload CSV content
        f = d.files().update(fileId=existing["id"], media_body=media,
                             fields="id,name,webViewLink,mimeType").execute()
    else:
        # single combined call: Drive converts CSV source -> Sheets destination
        body = {"name": title, "mimeType": "application/vnd.google.apps.spreadsheet"}
        f = d.files().create(body=body, media_body=media,
                             fields="id,name,webViewLink,mimeType").execute()
    print(f"Sheet '{title}' synced ({len(pins)} rows). URL: {f.get('webViewLink')} "
          f"[{f.get('mimeType')}]")
    return f.get("webViewLink")


def export_approved(csv_out=CSV_OUT):
    """Read the live Sheet, export APPROVED=YES rows to bulk_upload.csv (first 7 cols)."""
    d = _drive()
    f = _find()
    if not f:
        print("Sheet not found"); return 0
    import io as _io
    from googleapiclient.http import MediaIoBaseDownload
    fh = _io.BytesIO()
    dl = MediaIoBaseDownload(fh, d.files().export_media(fileId=f["id"], mimeType="text/csv"))
    done = False
    while not done:
        _, done = dl.next_chunk()
    fh.seek(0)
    reader = csv.reader(_io.TextIOWrapper(fh, encoding="utf-8"))
    rows = list(reader)
    if not rows:
        print("empty"); return 0
    header, *data = rows
    approved = [r for r in data if len(r) > 7 and r[7].strip().upper() == "YES"]
    with open(csv_out, "w", newline="", encoding="utf-8") as out:
        w = csv.writer(out); w.writerow(header[:7]); w.writerows([r[:7] for r in approved])
    print(f"Exported {len(approved)} approved pins -> {csv_out}")
    return len(approved)


if __name__ == "__main__":
    import sys
    sample = [{
        "title": "5 Amazon Finds Under $25", "description": "Budget must-haves. " + DISCLOSURE,
        "link": "https://www.amazon.com/REPLACE_ASIN_1?tag=lexxdigital03-20",
        "board": "Amazon Finds", "keywords": "amazonfinds,deals",
        "media_url": "https://lexxautomates.github.io/pinterest-pins/images/demo_pin.png",
        "publish_date": "",
    }]
    if "--export" in sys.argv:
        print(export_approved())
    else:
        print(sync_sheet(sample))
