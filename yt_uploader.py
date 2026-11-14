"""
ClipperAI Studio - YouTube Shorts Automated Uploader
Implements YouTube Data API v3 OAuth2 upload with resumable chunks,
credentials management, channel status checking, and Studio manual upload fallback.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent
CLIENT_SECRETS_FILE = BASE_DIR / "client_secrets.json"
TOKEN_FILE = BASE_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]


def check_auth_status() -> Dict[str, Any]:
    """
    Checks if client_secrets.json and token.json exist and if credentials are valid.
    """
    if not GOOGLE_API_AVAILABLE:
        return {
            "google_api_installed": False,
            "secrets_present": False,
            "authenticated": False,
            "message": "Library google-api-python-client belum terpasang."
        }

    secrets_present = CLIENT_SECRETS_FILE.exists()
    token_present = TOKEN_FILE.exists()
    authenticated = False
    channel_info = None

    if token_present:
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            if creds and creds.valid:
                authenticated = True
            elif creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())
                authenticated = True

            if authenticated:
                # Fetch Channel Title
                youtube = build("youtube", "v3", credentials=creds)
                req = youtube.channels().list(mine=True, part="snippet")
                res = req.execute()
                if "items" in res and len(res["items"]) > 0:
                    channel_info = {
                        "id": res["items"][0]["id"],
                        "title": res["items"][0]["snippet"]["title"],
                        "customUrl": res["items"][0]["snippet"].get("customUrl", "")
                    }
        except Exception as e:
            authenticated = False
            print(f"[YouTube Auth Check Warning]: {e}")

    return {
        "google_api_installed": True,
        "secrets_present": secrets_present,
        "token_present": token_present,
        "authenticated": authenticated,
        "channel": channel_info,
        "secrets_path": str(CLIENT_SECRETS_FILE)
    }


def authenticate_flow() -> Dict[str, Any]:
    """
    Initiates Google OAuth2 authentication flow on local machine.
    Opens browser for user consent and writes token.json.
    """
    if not CLIENT_SECRETS_FILE.exists():
        return {
            "ok": False,
            "error": f"File '{CLIENT_SECRETS_FILE.name}' tidak ditemukan di folder proyek. Buat OAuth Client ID di Google Cloud Console dan simpan sebagai client_secrets.json."
        }

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CLIENT_SECRETS_FILE),
            SCOPES
        )
        creds = flow.run_local_server(port=8088, prompt="consent")
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

        # Test and get channel name
        youtube = build("youtube", "v3", credentials=creds)
        res = youtube.channels().list(mine=True, part="snippet").execute()
        channel_title = res["items"][0]["snippet"]["title"] if "items" in res and res["items"] else "Akun YouTube"

        return {
            "ok": True,
            "message": f"Berhasil terhubung dengan channel: {channel_title}",
            "channel_title": channel_title
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Gagal autentikasi Google OAuth: {str(e)}"
        }


def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: List[str],
    category_id: str = "22",
    privacy_status: str = "public",
    made_for_kids: bool = False
) -> Dict[str, Any]:
    """
    Uploads a video to YouTube using resumable upload chunks.
    """
    if not os.path.exists(video_path):
        return {"ok": False, "error": f"File video tidak ditemukan: {video_path}"}

    if not TOKEN_FILE.exists():
        return {
            "ok": False,
            "error": "Belum terhubung ke Akun YouTube. Klik tombol 'Hubungkan Akun YouTube' terlebih dahulu."
        }

    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())

        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": title[:100],  # YouTube max title length 100
                "description": description[:5000],  # YouTube max description length 5000
                "tags": [t.strip() for t in tags if t.strip()][:50],
                "categoryId": str(category_id)
            },
            "status": {
                "privacyStatus": privacy_status,  # 'public', 'unlisted', 'private'
                "selfDeclaredMadeForKids": made_for_kids,
                "embeddable": True
            }
        }

        # 5MB chunk size for reliable resumable upload
        media = MediaFileUpload(
            video_path,
            chunksize=1024 * 1024 * 5,
            resumable=True,
            mimetype="video/mp4"
        )

        insert_request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = insert_request.next_chunk()
            if status:
                print(f"[YouTube Upload]: Progress {int(status.progress() * 100)}%")

        video_id = response.get("id")
        return {
            "ok": True,
            "video_id": video_id,
            "url": f"https://youtu.be/{video_id}",
            "studio_url": f"https://studio.youtube.com/video/{video_id}/edit",
            "title": title
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Gagal mengunggah video ke YouTube: {str(e)}"
        }
