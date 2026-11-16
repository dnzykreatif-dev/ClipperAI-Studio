"""
ClipperAI Studio - Remote & Mobile Automation Suite (automation_bridge.py)
Industrial-grade automation modules for mobile control, cross-posting, and video optimization.

Contains 5 High-Impact Automation Modules:
1. Cloudflare Quick Tunnel (Zero-Config Smartphone Remote Access)
2. Google Drive Session Uploader (Direct Chrome Profile upload - No API Key needed)
3. Wireless ADB Android Bridge (Shopee Video & Mobile Device Auto-Poster)
4. Mathematical Seamless Video Looper & Audio Sync (Cross-Fade Loop Algorithm)
5. High-Contrast Hook & Subtitle Styler (Upper-Third Gold Accent Box)
"""

import os
import sys
import re
import time
import shutil
import ssl
import json
import logging
import urllib.request
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger("automation_bridge")

BASE_DIR = Path(__file__).resolve().parent
TOOLS_DIR = BASE_DIR / "tools"
TOOLS_DIR.mkdir(parents=True, exist_ok=True)

IS_WIN = sys.platform.startswith("win")
CLOUDFLARED_EXE = TOOLS_DIR / ("cloudflared.exe" if IS_WIN else "cloudflared")
ADB_DIR = TOOLS_DIR / "platform-tools"
ADB_EXE = ADB_DIR / ("adb.exe" if IS_WIN else "adb")

# Global state for Cloudflare Quick Tunnel
_cf_tunnel_process: Optional[subprocess.Popen] = None
_cf_public_url: str = ""
_cf_tunnel_thread: Optional[threading.Thread] = None
_cf_tunnel_lock = threading.Lock()


def get_startupinfo():
    """Hide console window on Windows."""
    if IS_WIN:
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE
        return info
    return None


# ==============================================================================
# 1. CLOUDFLARE QUICK TUNNEL (REMOTE SMARTPHONE CONTROL)
# ==============================================================================

def ensure_cloudflared_available(callback_status=None) -> Optional[str]:
    """
    Downloads official Cloudflare tunnel binary (~35MB) if not already present.
    Zero-config: No account, no DNS, no token required.
    """
    exe_str = str(CLOUDFLARED_EXE)
    if CLOUDFLARED_EXE.exists() and CLOUDFLARED_EXE.stat().st_size > 1_000_000:
        return exe_str

    # Also check if cloudflared is in system PATH
    sys_cf = shutil.which("cloudflared")
    if sys_cf:
        return sys_cf

    if callback_status:
        callback_status("📥 [Cloudflare Tunnel] Mengunduh komponen remote access (~35MB)...")
    logger.info("Downloading official Cloudflare tunnel binary...")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    if IS_WIN:
        url_dl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    elif sys.platform == "darwin":
        url_dl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz"
    else:
        url_dl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"

    try:
        req = urllib.request.Request(url_dl, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=90, context=ctx) as resp, open(CLOUDFLARED_EXE, "wb") as out_f:
            shutil.copyfileobj(resp, out_f)

        if not IS_WIN:
            os.chmod(CLOUDFLARED_EXE, 0o755)

        if callback_status:
            callback_status("✅ [Cloudflare Tunnel] Komponen cloudflared siap digunakan!")
        logger.info("Cloudflared binary successfully downloaded.")
        return exe_str
    except Exception as e:
        logger.error(f"Failed to download cloudflared: {e}")
        if callback_status:
            callback_status(f"⚠️ Gagal mengunduh cloudflared: {e}")
        return None


def start_cloudflare_tunnel(port_local: int = 8000, on_url_ready=None) -> Dict[str, Any]:
    """
    Starts a Cloudflare Quick Tunnel forwarding to port_local.
    Returns status dictionary with tunnel URL.
    """
    global _cf_tunnel_process, _cf_public_url, _cf_tunnel_thread

    with _cf_tunnel_lock:
        if _cf_tunnel_process and _cf_tunnel_process.poll() is None and _cf_public_url:
            return {"status": "already_running", "url": _cf_public_url}

        cf_path = ensure_cloudflared_available()
        if not cf_path:
            return {"status": "error", "message": "cloudflared binary unavailable"}

        _cf_public_url = ""

        def _worker():
            global _cf_tunnel_process, _cf_public_url
            cmd = [cf_path, "tunnel", "--url", f"http://127.0.0.1:{port_local}"]
            try:
                _cf_tunnel_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    startupinfo=get_startupinfo(),
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                logger.info(f"Cloudflare tunnel spawned: PID {_cf_tunnel_process.pid}")

                for line in iter(_cf_tunnel_process.stdout.readline, ""):
                    if not line:
                        break
                    line_clean = line.strip()
                    m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line_clean)
                    if m and not _cf_public_url:
                        _cf_public_url = m.group(0)
                        logger.info(f"🌐 [Cloudflare Quick Tunnel Ready]: {_cf_public_url}")
                        if on_url_ready:
                            try:
                                on_url_ready(_cf_public_url)
                            except Exception as e_cb:
                                logger.warning(f"Error in on_url_ready callback: {e_cb}")

                _cf_tunnel_process.wait()
            except Exception as e:
                logger.error(f"Tunnel process exception: {e}")
            finally:
                _cf_public_url = ""

        _cf_tunnel_thread = threading.Thread(target=_worker, daemon=True)
        _cf_tunnel_thread.start()

        # Wait up to 10 seconds for URL
        for _ in range(20):
            if _cf_public_url:
                break
            time.sleep(0.5)

        if _cf_public_url:
            return {"status": "connected", "url": _cf_public_url}
        else:
            return {"status": "starting", "message": "Tunnel starting, URL will be available shortly"}


def stop_cloudflare_tunnel() -> Dict[str, Any]:
    """Stops the active Cloudflare Quick Tunnel."""
    global _cf_tunnel_process, _cf_public_url
    with _cf_tunnel_lock:
        if _cf_tunnel_process and _cf_tunnel_process.poll() is None:
            try:
                _cf_tunnel_process.terminate()
                _cf_tunnel_process.wait(timeout=3)
            except Exception:
                try:
                    _cf_tunnel_process.kill()
                except Exception:
                    pass
            _cf_tunnel_process = None
            _cf_public_url = ""
            return {"status": "stopped", "message": "Tunnel stopped successfully"}
        return {"status": "not_running", "message": "Tunnel is not running"}


def get_cloudflare_tunnel_status() -> Dict[str, Any]:
    """Returns the current status and public URL of the tunnel."""
    is_running = (_cf_tunnel_process is not None and _cf_tunnel_process.poll() is None)
    return {
        "is_running": is_running,
        "url": _cf_public_url if is_running else "",
        "pid": _cf_tunnel_process.pid if is_running else None
    }


# ==============================================================================
# 2. GOOGLE DRIVE WEB SESSION UPLOADER (ZERO API KEY)
# ==============================================================================

def extract_gdrive_folder_id(input_str: str) -> str:
    """Extract folder ID from Google Drive folder link or direct ID."""
    s = str(input_str or "").strip()
    if not s:
        return ""
    m = re.search(r"/folders/([a-zA-Z0-9_\-]+)", s)
    if m:
        return m.group(1)
    m2 = re.search(r"[?&]id=([a-zA-Z0-9_\-]+)", s)
    if m2:
        return m2.group(1)
    return s.split("?")[0].strip()


def upload_via_chrome_ke_folder_gdrive(
    path_file: str,
    folder_id: str,
    profil_chrome_target: Optional[str] = None,
    callback_status=None,
    headless: bool = True
) -> bool:
    """
    Uploads a file to Google Drive using an active logged-in Chrome Profile session
    without needing any Google Cloud Service Account or API credentials!
    Uses JavaScript input prototype interception to bypass cloud API limits.
    """
    if not folder_id:
        if callback_status:
            callback_status("❌ Folder ID Google Drive belum diisi!")
        return False

    folder_id = extract_gdrive_folder_id(folder_id)
    path_file_obj = Path(path_file)
    if not path_file_obj.exists():
        if callback_status:
            callback_status(f"❌ File tidak ditemukan: {path_file}")
        return False

    nama_file = path_file_obj.name
    url_folder = f"https://drive.google.com/drive/folders/{folder_id}"

    if callback_status:
        callback_status(f"☁️ [GDrive Web] Membuka Google Drive & menyiapkan upload '{nama_file}'...")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
    except ImportError:
        logger.error("Selenium not installed. Install with `pip install selenium`.")
        if callback_status:
            callback_status("❌ Selenium belum terpasang. Jalankan `pip install selenium`.")
        return False

    driver = None
    try:
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)

        if profil_chrome_target and os.path.exists(profil_chrome_target):
            opts.add_argument(f"--user-data-dir={profil_chrome_target}")

        driver = webdriver.Chrome(options=opts)
        driver.set_page_load_timeout(60)
        driver.get(url_folder)
        time.sleep(4)

        # Hook input type=file click prototype
        hook_js = """
        window.__gdriveFileInput = null;
        const origClick = HTMLInputElement.prototype.click;
        HTMLInputElement.prototype.click = function() {
            if (this.type === 'file') {
                window.__gdriveFileInput = this;
                if (!this.isConnected) {
                    this.style.position = 'fixed';
                    this.style.top = '0px';
                    this.style.opacity = '0.01';
                    document.body.appendChild(this);
                }
                return;
            }
            return origClick.apply(this, arguments);
        };
        """
        driver.execute_script(hook_js)
        time.sleep(1)

        # Find and click "New" / "Baru" button
        click_new_js = """
        let btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
        for (let b of btns) {
            if (b.offsetParent === null) continue;
            let r = b.getBoundingClientRect();
            let t = (b.innerText || b.textContent || '').trim().toLowerCase();
            if (r.left < 260 && r.top < 220 && (t === 'new' || t === 'baru' || t.includes('new') || t.includes('baru'))) {
                b.click();
                return true;
            }
        }
        return false;
        """
        driver.execute_script(click_new_js)
        time.sleep(1.5)

        # Click "File upload" / "Unggah file"
        click_upload_item_js = """
        let items = Array.from(document.querySelectorAll('[role="menuitem"], div, span'));
        for (let it of items) {
            if (it.offsetParent === null) continue;
            let t = (it.innerText || it.textContent || '').trim().toLowerCase();
            if (t === 'file upload' || t === 'upload file' || t === 'unggah file') {
                let el = it.closest('[role="menuitem"]') || it;
                el.click();
                return true;
            }
        }
        return false;
        """
        driver.execute_script(click_upload_item_js)
        time.sleep(1)

        # Get intercepted input
        inp = driver.execute_script("return window.__gdriveFileInput || document.querySelector('input[type=\"file\"]') || null;")
        if not inp:
            if callback_status:
                callback_status("⚠️ Gagal menangkap input file GDrive. Pastikan akun sudah login di profil Chrome.")
            return False

        if callback_status:
            callback_status(f"⏳ [GDrive Web] Mengirim file '{nama_file}'...")
        inp.send_keys(os.path.abspath(path_file))

        # Wait for completion
        uploaded = False
        for _ in range(60):
            time.sleep(2)
            check_js = """
            let txt = (document.body.innerText || '').toLowerCase();
            return txt.includes('upload complete') || txt.includes('upload selesai') || txt.includes('unggahan selesai');
            """
            if driver.execute_script(check_js):
                uploaded = True
                break

        if uploaded:
            if callback_status:
                callback_status(f"✅ [GDrive Web] '{nama_file}' berhasil diunggah ke Google Drive!")
            return True
        else:
            if callback_status:
                callback_status(f"⚠️ [GDrive Web] Upload '{nama_file}' mungkin masih berlangsung di background.")
            return True
    except Exception as e:
        logger.error(f"GDrive upload exception: {e}")
        if callback_status:
            callback_status(f"❌ Error GDrive Upload: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


# ==============================================================================
# 3. WIRELESS ADB ANDROID BRIDGE (AUTO SHOPEE & TIKTOK UPLOADER)
# ==============================================================================

def ensure_adb_available(callback_status=None) -> Optional[str]:
    """Ensures ADB executable is present, downloading Google Platform-Tools if needed."""
    if ADB_EXE.exists():
        return str(ADB_EXE)

    sys_adb = shutil.which("adb")
    if sys_adb:
        return sys_adb

    if callback_status:
        callback_status("📥 [ADB Bridge] Mengunduh Google Platform-Tools resmi (~6MB)...")
    logger.info("Downloading official Google Android Platform-Tools...")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    if IS_WIN:
        url_dl = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    elif sys.platform == "darwin":
        url_dl = "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
    else:
        url_dl = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"

    zip_tmp = TOOLS_DIR / "platform_tools.zip"
    try:
        req = urllib.request.Request(url_dl, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp, open(zip_tmp, "wb") as out_f:
            shutil.copyfileobj(resp, out_f)

        import zipfile
        with zipfile.ZipFile(zip_tmp, "r") as zf:
            zf.extractall(TOOLS_DIR)

        if zip_tmp.exists():
            zip_tmp.unlink()

        if ADB_EXE.exists():
            if callback_status:
                callback_status("✅ [ADB Bridge] Google ADB siap digunakan!")
            return str(ADB_EXE)
    except Exception as e:
        logger.error(f"Failed to setup ADB: {e}")
        if callback_status:
            callback_status(f"⚠️ Gagal mengunduh ADB: {e}")
    return None


def run_adb_cmd(args: List[str], timeout_sec: int = 30) -> Tuple[int, str]:
    """Executes an ADB command with hidden console window."""
    adb_path = ensure_adb_available()
    if not adb_path:
        return -1, "ADB not available"
    cmd = [adb_path] + args
    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            startupinfo=get_startupinfo(),
            text=True,
            timeout=timeout_sec
        )
        return p.returncode, p.stdout.strip()
    except subprocess.TimeoutExpired:
        return -1, "ADB command timed out"
    except Exception as e:
        return -1, str(e)


def pair_adb_wireless(ip: str, port_pairing: str, kode_pairing: str) -> Dict[str, Any]:
    """
    Performs 1-time wireless pairing for Android 11+ via Wi-Fi.
    Zero-cable required.
    """
    ip_clean = str(ip or "").strip()
    port_p = str(port_pairing or "").strip()
    kode_p = str(kode_pairing or "").strip()

    if not ip_clean or not port_p or not kode_p:
        return {"success": False, "message": "IP, Port Pairing, dan 6-Digit Kode wajib diisi"}

    run_adb_cmd(["start-server"], timeout_sec=5)
    target = f"{ip_clean}:{port_p}"
    rc, out = run_adb_cmd(["pair", target, kode_p], timeout_sec=15)
    out_low = out.lower()

    if "successfully paired" in out_low or rc == 0:
        return {"success": True, "message": f"Berhasil Pair dengan HP ({target})!"}
    else:
        return {"success": False, "message": f"Gagal Pair: {out}"}


def connect_adb(target_ip_or_serial: str = "") -> Dict[str, Any]:
    """
    Connects to Android device via Wireless TCP/IP or USB.
    Returns connected device ID.
    """
    run_adb_cmd(["start-server"], timeout_sec=5)
    target = str(target_ip_or_serial or "").strip()

    if target and ":" in target:
        run_adb_cmd(["connect", target], timeout_sec=10)

    rc, out = run_adb_cmd(["devices"])
    lines = out.splitlines()[1:]
    devices = [l.split()[0] for l in lines if "\tdevice" in l]

    if devices:
        active_dev = target if target in devices else devices[0]
        return {"success": True, "device_id": active_dev, "devices": devices}
    else:
        return {"success": False, "device_id": "", "devices": [], "message": "Tidak ada perangkat Android terhubung."}


def set_clipboard_and_paste_adb(device_id: str, text: str) -> bool:
    """
    Copies text (including #hashtags) to Android clipboard and pastes safely,
    avoiding the infamous shell hashtag truncate bug.
    """
    clean_text = " ".join(str(text).splitlines()).strip()
    # 1. Try modern cmd clipboard set-text (Android 8+)
    rc, out = run_adb_cmd(["-s", device_id, "shell", "cmd", "clipboard", "set-text", clean_text])
    if rc == 0:
        # Paste via KEYCODE_PASTE (279)
        run_adb_cmd(["-s", device_id, "shell", "input", "keyevent", "279"])
        return True

    # 2. Fallback: chunked input text with escaped # and spaces
    safe_text = clean_text.replace(" ", "%s").replace("#", "\\#")
    run_adb_cmd(["-s", device_id, "shell", "input", "text", f'"{safe_text}"'])
    return True


# ==============================================================================
# 4. MATHEMATICAL SEAMLESS VIDEO LOOPER & AUDIO MIXER
# ==============================================================================

def create_seamless_loop(
    input_path: str,
    output_path: str,
    target_duration_sec: float = 30.0,
    overlap_sec: float = 1.0,
    ffmpeg_exe: Optional[str] = None
) -> bool:
    """
    Creates a mathematically smooth cross-fade video loop (Seamless Looper)
    using the ClipperAI FFmpeg Alpha Crossfade Filtergraph.
    Completely eliminates jump cuts when looping short AI video clips (8-10s)!
    """
    input_p = Path(input_path)
    if not input_p.exists():
        logger.error(f"Input file not found: {input_path}")
        return False

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if not ffmpeg_exe:
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            ffmpeg_exe = shutil.which("ffmpeg") or "ffmpeg"

    # Get input duration
    probe_cmd = [
        ffmpeg_exe, "-i", str(input_p),
        "-hide_banner"
    ]
    p_info = subprocess.run(probe_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, startupinfo=get_startupinfo())
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", p_info.stderr)
    if not m:
        logger.error("Could not determine video duration.")
        return False

    dur_asli = float(m.group(1)) * 3600 + float(m.group(2)) * 60 + float(m.group(3))
    if dur_asli <= 1.5:
        logger.warning("Video too short for seamless overlap.")
        return False

    overlap = min(overlap_sec, dur_asli * 0.25)
    dur_base = dur_asli - overlap

    # Base seamless transition filtergraph
    # [0:v] split into main and tail; fade out tail and overlay at beginning
    fv = (
        f"[0:v]split=2[v_main][v_tail];"
        f"[v_main]trim=start=0:end={dur_base:.2f},setpts=PTS-STARTPTS[base_v];"
        f"[v_tail]trim=start={dur_base:.2f}:end={dur_asli:.2f},setpts=PTS-STARTPTS,format=yuva420p,fade=t=out:st=0:d={overlap:.2f}:alpha=1[tail_faded];"
        f"[base_v][tail_faded]overlay=0:0:enable='between(t,0,{overlap:.2f})'[outv]"
    )

    temp_seamless_base = out_p.parent / f"_base_loop_{int(time.time())}.mp4"
    cmd_base = [
        ffmpeg_exe, "-y", "-i", str(input_p),
        "-filter_complex", fv,
        "-map", "[outv]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-an", str(temp_seamless_base)
    ]

    rc_b = subprocess.run(cmd_base, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, startupinfo=get_startupinfo())
    if rc_b.returncode != 0 or not temp_seamless_base.exists():
        logger.error(f"Failed to render seamless base: {rc_b.stderr.decode('utf-8', errors='ignore')}")
        return False

    # Repeat seamless base to target duration
    cmd_expand = [
        ffmpeg_exe, "-y",
        "-stream_loop", "-1",
        "-i", str(temp_seamless_base),
        "-t", f"{target_duration_sec:.2f}",
        "-c:v", "copy",
        str(out_p)
    ]
    rc_e = subprocess.run(cmd_expand, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, startupinfo=get_startupinfo())

    if temp_seamless_base.exists():
        try:
            temp_seamless_base.unlink()
        except Exception:
            pass

    return out_p.exists() and out_p.stat().st_size > 10_000


def sync_video_to_audio_duration(
    video_path: str,
    audio_path: str,
    output_path: str,
    mode_audio: str = "replace",  # 'replace' or 'mix'
    ffmpeg_exe: Optional[str] = None
) -> bool:
    """
    Loops video smoothly to match full audio track duration, mixing or replacing audio.
    """
    v_p = Path(video_path)
    a_p = Path(audio_path)
    out_p = Path(output_path)

    if not v_p.exists() or not a_p.exists():
        return False

    if not ffmpeg_exe:
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            ffmpeg_exe = shutil.which("ffmpeg") or "ffmpeg"

    # Get audio duration
    probe_cmd = [ffmpeg_exe, "-i", str(a_p), "-hide_banner"]
    p_info = subprocess.run(probe_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, startupinfo=get_startupinfo())
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", p_info.stderr)
    if not m:
        return False
    dur_audio = float(m.group(1)) * 3600 + float(m.group(2)) * 60 + float(m.group(3))

    temp_looped = out_p.parent / f"_temp_looped_{int(time.time())}.mp4"
    if not create_seamless_loop(str(v_p), str(temp_looped), target_duration_sec=dur_audio, ffmpeg_exe=ffmpeg_exe):
        return False

    # Mix / replace audio
    if mode_audio == "replace":
        cmd_mix = [
            ffmpeg_exe, "-y",
            "-i", str(temp_looped),
            "-i", str(a_p),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-t", f"{dur_audio:.2f}",
            "-shortest",
            str(out_p)
        ]
    else:
        filter_mix = "[1:a]volume=0.35[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        cmd_mix = [
            ffmpeg_exe, "-y",
            "-i", str(temp_looped),
            "-i", str(a_p),
            "-filter_complex", filter_mix,
            "-map", "0:v:0",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-t", f"{dur_audio:.2f}",
            str(out_p)
        ]

    subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=get_startupinfo())
    if temp_looped.exists():
        try:
            temp_looped.unlink()
        except Exception:
            pass

    return out_p.exists() and out_p.stat().st_size > 10_000


# ==============================================================================
# 5. HIGH-CONTRAST HOOK & SUBTITLE STYLER
# ==============================================================================

def overlay_high_contrast_hook(
    video_path: str,
    hook_text: str,
    output_path: Optional[str] = None,
    durasi_tampil_detik: float = 4.0,
    ffmpeg_exe: Optional[str] = None
) -> Optional[str]:
    """
    Renders high-contrast upper-third hook badge (gold/yellow text + dark translucent box)
    optimized for vertical 9:16 Shorts / Reels retention.
    """
    v_p = Path(video_path)
    if not v_p.exists() or not str(hook_text).strip():
        return None

    if not output_path:
        out_p = v_p.parent / f"{v_p.stem}_hooked.mp4"
    else:
        out_p = Path(output_path)

    if not ffmpeg_exe:
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            ffmpeg_exe = shutil.which("ffmpeg") or "ffmpeg"

    from PIL import Image, ImageDraw, ImageFont

    w_vid, h_vid = 1080, 1920
    overlay = Image.new("RGBA", (w_vid, h_vid), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = int(w_vid * 0.048)  # ~52px
    font = None
    for fn in ["segoeuib.ttf", "arialbd.ttf", "impact.ttf", "arial.ttf"]:
        try:
            font = ImageFont.truetype(fn, font_size)
            break
        except Exception:
            continue
    if not font:
        font = ImageFont.load_default()

    # Word wrap
    words = hook_text.strip().split()
    lines = []
    curr = ""
    for w in words:
        test = f"{curr} {w}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if (bbox[2] - bbox[0]) < (w_vid * 0.8):
            curr = test
        else:
            if curr:
                lines.append(curr)
            curr = w
    if curr:
        lines.append(curr)

    wrapped_text = "\n".join(lines)
    bbox_total = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center", spacing=12)
    tw = bbox_total[2] - bbox_total[0]
    th = bbox_total[3] - bbox_total[1]

    tx = (w_vid - tw) // 2
    ty = int(h_vid * 0.12)  # Upper third position

    pad_x = int(font_size * 0.55)
    pad_y = int(font_size * 0.35)

    # Dark translucent background box
    draw.rounded_rectangle(
        (tx - pad_x, ty - pad_y, tx + tw + pad_x, ty + th + pad_y),
        radius=16,
        fill=(10, 15, 30, 185),
        outline=(251, 191, 36, 220),  # Gold amber border
        width=3
    )

    # Black outline shadow
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)]:
        draw.multiline_text((tx + dx, ty + dy), wrapped_text, font=font, fill=(0, 0, 0, 240), align="center", spacing=12)

    # Primary text in bright gold
    draw.multiline_text((tx, ty), wrapped_text, font=font, fill=(253, 224, 71, 255), align="center", spacing=12)

    overlay_png = v_p.parent / f"_hook_ovr_{int(time.time())}.png"
    overlay.save(overlay_png, "PNG")

    filter_complex = f"[0:v][1:v]overlay=0:0:enable='between(t,0,{durasi_tampil_detik:.1f})'"

    cmd = [
        ffmpeg_exe, "-y",
        "-i", str(v_p),
        "-i", str(overlay_png),
        "-filter_complex", filter_complex,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "copy",
        str(out_p)
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=get_startupinfo())
    if overlay_png.exists():
        try:
            overlay_png.unlink()
        except Exception:
            pass

    return str(out_p) if out_p.exists() else None
