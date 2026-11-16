"""
ClipperAI Studio - Social Media Multi-Platform Publisher & Account Hub
Supports 1-Click Cross-Posting to:
1. YouTube Shorts (via Google OAuth2 & YouTube Data API v3)
2. Facebook Reels (via Meta Graph API v19.0 / Pages API)
3. TikTok (via TikTok Content Posting API v2 & 1-Click Web Bridge)
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests

import yt_uploader

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "social_accounts.json"
CLIENT_SECRETS_FILE = BASE_DIR / "client_secrets.json"
TOKEN_FILE = BASE_DIR / "token.json"

logger = logging.getLogger("social_poster")


def _load_config() -> Dict[str, Any]:
    """Load social_accounts.json or return default structure."""
    defaults = {
        "facebook": {
            "page_id": "",
            "page_name": "",
            "access_token": "",
            "connected": False
        },
        "tiktok": {
            "access_token": "",
            "creator_username": "",
            "connected": False
        }
    }
    if not CONFIG_FILE.exists():
        return defaults
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # merge defaults
            for k, v in defaults.items():
                if k not in data:
                    data[k] = v
                else:
                    for subk, subv in v.items():
                        if subk not in data[k]:
                            data[k][subk] = subv
            return data
    except Exception as e:
        logger.warning(f"Failed to read {CONFIG_FILE}: {e}")
        return defaults


def _save_config(config: Dict[str, Any]) -> None:
    """Save config to social_accounts.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save {CONFIG_FILE}: {e}")


def get_social_status() -> Dict[str, Any]:
    """
    Returns live authentication and connection status for YouTube, Facebook, and TikTok.
    """
    cfg = _load_config()
    
    # 1. YouTube Status
    yt_status = yt_uploader.check_auth_status()
    
    # 2. Facebook Status
    fb_cfg = cfg.get("facebook", {})
    fb_connected = False
    fb_page_name = fb_cfg.get("page_name", "")
    fb_page_id = fb_cfg.get("page_id", "")
    fb_token = fb_cfg.get("access_token", "")
    fb_message = "Belum terhubung. Masukkan Page ID & Access Token."
    
    if fb_page_id and fb_token:
        # Validate token with Meta Graph API
        try:
            r = requests.get(
                f"https://graph.facebook.com/v19.0/{fb_page_id}",
                params={"access_token": fb_token, "fields": "name,id"},
                timeout=5
            )
            if r.status_code == 200:
                data = r.json()
                fb_page_name = data.get("name", fb_page_name)
                fb_connected = True
                fb_message = f"Terhubung ke Halaman: {fb_page_name} (ID: {fb_page_id})"
                # Update saved name if changed
                if fb_cfg.get("page_name") != fb_page_name:
                    fb_cfg["page_name"] = fb_page_name
                    fb_cfg["connected"] = True
                    _save_config(cfg)
            else:
                err_data = r.json().get("error", {})
                fb_message = f"Token tidak valid: {err_data.get('message', 'Periksa izin token')}"
        except Exception as e:
            fb_message = f"Koneksi Meta Graph API gagal: {str(e)}"
    
    # 3. TikTok Status
    tt_cfg = cfg.get("tiktok", {})
    tt_token = tt_cfg.get("access_token", "")
    tt_user = tt_cfg.get("creator_username", "")
    tt_connected = bool(tt_token)
    tt_message = "Mode 1-Klik Web Studio Aktif (Siap pakai tanpa daftar API)" if not tt_connected else f"Terhubung via API ({tt_user or 'Akun TikTok'})"
    
    return {
        "youtube": {
            "connected": yt_status.get("authenticated", False),
            "secrets_present": yt_status.get("secrets_present", False),
            "channel": yt_status.get("channel"),
            "message": "Terhubung ke channel" if yt_status.get("authenticated") else "Belum terhubung ke Akun YouTube"
        },
        "facebook": {
            "connected": fb_connected,
            "page_id": fb_page_id,
            "page_name": fb_page_name,
            "message": fb_message
        },
        "tiktok": {
            "connected": tt_connected,
            "username": tt_user,
            "mode": "api" if tt_connected else "web_bridge",
            "message": tt_message
        }
    }


def save_youtube_keys(client_id: str, client_secret: str) -> Dict[str, Any]:
    """
    Saves Client ID and Secret directly into client_secrets.json.
    Eliminates the need for manual JSON file download and renaming.
    """
    client_id = client_id.strip()
    client_secret = client_secret.strip()
    
    if not client_id or not client_secret:
        return {"ok": False, "error": "Client ID dan Client Secret tidak boleh kosong."}
    
    data = {
        "installed": {
            "client_id": client_id,
            "project_id": "clipperai-studio",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost:8088/"]
        }
    }
    
    try:
        with open(CLIENT_SECRETS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return {
            "ok": True,
            "message": "client_secrets.json berhasil dibuat! Sekarang klik 'Hubungkan Akun YouTube'."
        }
    except Exception as e:
        return {"ok": False, "error": f"Gagal menyimpan file: {str(e)}"}


def save_youtube_secrets_file(content_str: str) -> Dict[str, Any]:
    """Save an uploaded client_secrets.json file directly."""
    try:
        parsed = json.loads(content_str)
        if "installed" not in parsed and "web" not in parsed:
            return {"ok": False, "error": "Format file tidak valid. Pastikan file JSON dari Google Cloud Console."}
        
        with open(CLIENT_SECRETS_FILE, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)
        return {
            "ok": True,
            "message": "File client_secrets.json berhasil disimpan! Klik tombol login YouTube."
        }
    except Exception as e:
        return {"ok": False, "error": f"Format JSON tidak valid: {str(e)}"}


def save_facebook_config(page_id: str, access_token: str) -> Dict[str, Any]:
    """
    Tests and saves Facebook Page ID & Access Token into social_accounts.json.
    """
    page_id = page_id.strip()
    access_token = access_token.strip()
    
    if not page_id or not access_token:
        return {"ok": False, "error": "Page ID dan Access Token Facebook tidak boleh kosong."}
    
    try:
        r = requests.get(
            f"https://graph.facebook.com/v19.0/{page_id}",
            params={"access_token": access_token, "fields": "name,id"},
            timeout=8
        )
        if r.status_code != 200:
            err = r.json().get("error", {}).get("message", "Periksa Page ID dan Access Token Anda.")
            return {"ok": False, "error": f"Verifikasi Facebook gagal: {err}"}
        
        data = r.json()
        page_name = data.get("name", "Halaman Facebook")
        
        cfg = _load_config()
        cfg["facebook"] = {
            "page_id": page_id,
            "page_name": page_name,
            "access_token": access_token,
            "connected": True
        }
        _save_config(cfg)
        
        return {
            "ok": True,
            "message": f"Berhasil terhubung ke Halaman Facebook: {page_name} (ID: {page_id})",
            "page_name": page_name
        }
    except Exception as e:
        return {"ok": False, "error": f"Gagal menghubungi server Facebook: {str(e)}"}


def save_tiktok_config(access_token: str, username: Optional[str] = None) -> Dict[str, Any]:
    """
    Saves TikTok Access Token & Username into social_accounts.json.
    """
    access_token = access_token.strip()
    username = (username or "").strip()
    
    cfg = _load_config()
    cfg["tiktok"] = {
        "access_token": access_token,
        "creator_username": username,
        "connected": bool(access_token)
    }
    _save_config(cfg)
    
    return {
        "ok": True,
        "message": "Konfigurasi TikTok berhasil disimpan!"
    }


def upload_to_facebook_reels(video_path: str, caption: str) -> Dict[str, Any]:
    """
    Uploads a short vertical video to Facebook Reels using official Meta Graph API v19.0.
    """
    cfg = _load_config().get("facebook", {})
    page_id = cfg.get("page_id")
    access_token = cfg.get("access_token")
    
    if not page_id or not access_token:
        return {
            "ok": False,
            "error": "Belum terhubung ke Akun Facebook. Hubungkan Page ID & Access Token terlebih dahulu.",
            "web_fallback_url": "https://www.facebook.com/reels/create"
        }
    
    if not os.path.exists(video_path):
        return {"ok": False, "error": f"File video tidak ditemukan: {video_path}"}
    
    file_size = os.path.getsize(video_path)
    
    try:
        # Step 1: Initialize Reel Upload Session
        init_url = f"https://graph.facebook.com/v19.0/{page_id}/video_reels"
        init_res = requests.post(
            init_url,
            data={
                "upload_phase": "start",
                "access_token": access_token
            },
            timeout=15
        )
        if init_res.status_code != 200:
            err = init_res.json().get("error", {}).get("message", "Gagal inisialisasi sesi Reel.")
            return {"ok": False, "error": f"Facebook Init Error: {err}"}
        
        init_data = init_res.json()
        video_id = init_data.get("video_id")
        upload_url = init_data.get("upload_url")
        
        if not upload_url or not video_id:
            return {"ok": False, "error": "Facebook tidak mengembalikan URL upload yang valid."}
        
        # Step 2: Upload Video Binary
        with open(video_path, "rb") as vf:
            upload_headers = {
                "Authorization": f"OAuth {access_token}",
                "offset": "0",
                "file_size": str(file_size)
            }
            bin_res = requests.post(
                upload_url,
                headers=upload_headers,
                data=vf,
                timeout=120
            )
            if bin_res.status_code not in (200, 201):
                return {"ok": False, "error": f"Gagal upload file video ke Facebook: HTTP {bin_res.status_code}"}
        
        # Step 3: Finish and Publish
        finish_res = requests.post(
            init_url,
            data={
                "upload_phase": "finish",
                "access_token": access_token,
                "video_id": video_id,
                "video_state": "PUBLISHED",
                "description": caption
            },
            timeout=20
        )
        if finish_res.status_code != 200:
            err = finish_res.json().get("error", {}).get("message", "Gagal mempublikasikan Reel.")
            return {"ok": False, "error": f"Facebook Publish Error: {err}"}
        
        return {
            "ok": True,
            "video_id": video_id,
            "url": f"https://www.facebook.com/reel/{video_id}",
            "message": "Berhasil mempublikasikan Facebook Reel!"
        }
    except Exception as e:
        return {"ok": False, "error": f"Error posting ke Facebook Reels: {str(e)}"}


def upload_to_tiktok(video_path: str, caption: str) -> Dict[str, Any]:
    """
    Handles TikTok posting. If API token is set, initiates Content Posting API.
    Otherwise provides direct 1-Click Web Bridge URL for instant upload.
    """
    cfg = _load_config().get("tiktok", {})
    access_token = cfg.get("access_token")
    
    if not os.path.exists(video_path):
        return {"ok": False, "error": f"File video tidak ditemukan: {video_path}"}
    
    # If Access Token is available, try official API
    if access_token:
        try:
            file_size = os.path.getsize(video_path)
            init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=UTF-8"
            }
            payload = {
                "post_info": {
                    "title": caption[:2200],
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_stitch": False,
                    "disable_comment": False
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": file_size,
                    "chunk_size": file_size,
                    "total_chunk_count": 1
                }
            }
            r = requests.post(init_url, headers=headers, json=payload, timeout=15)
            if r.status_code == 200:
                res_data = r.json()
                upload_url = res_data.get("data", {}).get("upload_url")
                publish_id = res_data.get("data", {}).get("publish_id")
                if upload_url:
                    with open(video_path, "rb") as vf:
                        up_res = requests.put(
                            upload_url,
                            headers={
                                "Content-Type": "video/mp4",
                                "Content-Range": f"bytes 0-{file_size - 1}/{file_size}"
                            },
                            data=vf,
                            timeout=120
                        )
                        if up_res.status_code in (200, 201):
                            return {
                                "ok": True,
                                "mode": "api",
                                "publish_id": publish_id,
                                "message": "Video berhasil diunggah ke TikTok Creator Account!"
                            }
        except Exception as e:
            logger.warning(f"TikTok API direct upload failed: {e}")
    
    # Web Bridge Fallback: 100% reliable for all creators
    return {
        "ok": True,
        "mode": "web_bridge",
        "url": "https://www.tiktok.com/creator-center/upload?from=webapp",
        "caption": caption,
        "message": "Caption siap di-paste! Buka TikTok Creator Center untuk upload instan."
    }


def publish_to_all_platforms(
    video_path: str,
    title: str,
    caption: str,
    tags: List[str],
    platforms: List[str],
    privacy: str = "public"
) -> Dict[str, Any]:
    """
    One-click multi-platform publisher for YouTube Shorts, TikTok, and Facebook Reels.
    """
    results: Dict[str, Any] = {}
    
    # Clean tags
    cleaned_tags = [t.strip().lstrip("#") for t in tags if t.strip()]
    
    # 1. YouTube Shorts
    if "youtube" in platforms:
        try:
            yt_res = yt_uploader.upload_to_youtube(
                video_path=video_path,
                title=title[:100],
                description=caption[:5000],
                tags=cleaned_tags[:50],
                privacy_status=privacy
            )
            results["youtube"] = yt_res
        except Exception as e:
            results["youtube"] = {"ok": False, "error": str(e)}
    
    # 2. Facebook Reels
    if "facebook" in platforms:
        try:
            fb_res = upload_to_facebook_reels(
                video_path=video_path,
                caption=caption
            )
            results["facebook"] = fb_res
        except Exception as e:
            results["facebook"] = {"ok": False, "error": str(e)}
    
    # 3. TikTok
    if "tiktok" in platforms:
        try:
            tt_res = upload_to_tiktok(
                video_path=video_path,
                caption=caption
            )
            results["tiktok"] = tt_res
        except Exception as e:
            results["tiktok"] = {"ok": False, "error": str(e)}
    
    # Check overall success
    any_success = any(r.get("ok") for r in results.values())
    
    return {
        "ok": any_success,
        "results": results
    }
