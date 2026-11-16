"""
ClipperAI Studio - Universal Engine
Supports all video niches: Podcasts, Business, Education, Motivation, Gaming, and Islamic Lectures.
Features:
- Niche-aware hook scoring & title formatting
- Universal & Islamic contextual auto-emojis
- Customizable top banner / channel watermark
- High-speed 10-core Whisper transcription
- Smart 9:16 vertical reframing
"""

import os
import re
import math
import uuid
import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional

import numpy as np

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False


# Universal Niche Configs
NICHE_CONFIGS = {
    "universal": {
        "header_tag": "🔥 VIRAL MOMENTS",
        "header_color": "0x10B981",
        "border_color": "0x34D399",
        "hashtags": "#shorts #reels #viral #trending #fyp #foryou"
    },
    "podcast": {
        "header_tag": "🎙️ PODCAST HIGHLIGHTS",
        "header_color": "0x1E293B",
        "border_color": "0x6366F1",
        "hashtags": "#podcast #interview #talkshow #shorts #reels #fyp"
    },
    "bisnis": {
        "header_tag": "💡 TIPS & STRATEGI BISNIS",
        "header_color": "0x064E3B",
        "border_color": "0xF59E0B",
        "hashtags": "#bisnis #keuangan #investasi #entrepreneur #sukses #shorts #reels"
    },
    "motivasi": {
        "header_tag": "🚀 MOTIVASI & MINDSET",
        "header_color": "0x4C1D95",
        "border_color": "0x8B5CF6",
        "hashtags": "#motivasi #mindset #selfimprovement #inspirasi #shorts #reels #fyp"
    },
    "edukasi": {
        "header_tag": "📚 EDUKASI & WAWASAN",
        "header_color": "0x1E3A8A",
        "border_color": "0x3B82F6",
        "hashtags": "#edukasi #belajar #kuliah #wawasan #shorts #fyp #foryou"
    },
    "gaming": {
        "header_tag": "🎮 GAMING MOMENTS",
        "header_color": "0x701A75",
        "border_color": "0xEC4899",
        "hashtags": "#gaming #gamer #gameplay #shorts #reels #fyp #trending"
    },
    "kajian": {
        "header_tag": "🕌 KAJIAN & DAKWAH",
        "header_color": "0x0D5C3A",
        "border_color": "0xD97706",
        "hashtags": "#kajian #islam #dakwah #pesantren #nasihat #shorts #reels #fyp"
    }
}

# Universal Contextual Emoji Dictionary
EMOJI_MAP = {
    # Business & Finance
    "uang": "💰 UANG",
    "cuan": "💰 CUAN",
    "kaya": "💰 KAYA",
    "harta": "💰 HARTA",
    "bisnis": "💼 BISNIS",
    "kerja": "💼 KERJA",
    "investasi": "📈 INVESTASI",
    "omset": "📈 OMSET",
    "modal": "💵 MODAL",
    "rugi": "📉 RUGI",
    "mahal": "💎 MAHAL",
    
    # Motivation & Mindset
    "sukses": "🏆 SUKSES",
    "gagal": "❌ GAGAL",
    "target": "🎯 TARGET",
    "fokus": "🎯 FOKUS",
    "mimpi": "✨ MIMPI",
    "otak": "🧠 OTAK",
    "mindset": "🧠 MINDSET",
    "mental": "💪 MENTAL",
    "rahasia": "🔑 RAHASIA",
    "kunci": "🔑 KUNCI",
    "tips": "💡 TIPS",
    "ide": "💡 IDE",
    "waktu": "⏳ WAKTU",
    "disiplin": "⚡ DISIPLIN",
    
    # Emotional & Hook Words
    "bahaya": "⚠️ BAHAYA",
    "waspada": "⚠️ WASPADA",
    "hati-hati": "⚠️ HATI-HATI",
    "kesalahan": "❌ KESALAHAN",
    "kaget": "😱 KAGET",
    "bingung": "🤯 BINGUNG",
    "mustahil": "🤯 MUSTAHIL",
    "fakta": "📌 FAKTA",
    "aturan": "📜 ATURAN",
    "hukum": "⚖️ HUKUM",
    
    # Islamic & Spiritual
    "allah": "☝️ ALLAH",
    "rasulullah": "🕌 RASULULLAH",
    "rasul": "🕌 RASUL",
    "nabi": "🕌 NABI",
    "quran": "📖 AL-QUR'AN",
    "alquran": "📖 AL-QUR'AN",
    "ayat": "📖 AYAT",
    "surat": "📖 SURAT",
    "surah": "📖 SURAH",
    "shalat": "🕌 SHALAT",
    "sholat": "🕌 SHOLAT",
    "masjid": "🕌 MASJID",
    "doa": "🤲 DOA",
    "berdoa": "🤲 BERDOA",
    "pahala": "✨ PAHALA",
    "syurga": "✨ SURGA",
    "surga": "✨ SURGA",
    "dosa": "⚠️ DOSA",
    "neraka": "🔥 NERAKA",
    "maksiat": "⚠️ MAKSIAT",
    "hati": "🤍 HATI",
    "ikhlas": "🤍 IKHLAS",
    "sedekah": "💰 SEDEKAH",
    "mati": "⚰️ KEMATIAN",
    "kematian": "⚰️ KEMATIAN",
    "ilmu": "📚 ILMU",
    "belajar": "📚 BELAJAR",
    "panglima": "⚔️ PANGLIMA",
    "perang": "⚔️ PERANG",
    "pasukan": "🛡️ PASUKAN",
    "pemimpin": "👑 PEMIMPIN",
    "raja": "👑 RAJA",
    "muda": "🔥 ANAK MUDA",
    "pemuda": "🔥 PEMUDA",
    "umur": "⏳ USIA MUDA",
    "usia": "⏳ USIA",
    "sahabat": "🤝 SAHABAT",
    "ulama": "👳 ULAMA",
    "sejarah": "📜 SEJARAH",
    "dunia": "🌍 DUNIA",
    "akhirat": "🌌 AKHIRAT",
    "iman": "✨ IMAN",
    "takwa": "✨ TAKWA",
    "sabar": "💎 SABAR",
    "syukur": "🤲 SYUKUR",
    "taubat": "💧 TAUBAT",
    "rezeki": "💎 REZEKI",
    "berkah": "✨ BERKAH",
    "halal": "✅ HALAL",
    "haram": "🚫 HARAM",
    "wajib": "❗ WAJIB",
    "keluarga": "👨‍👩‍👧‍👦 KELUARGA",
    "anak": "👶 ANAK",
    "orangtua": "🤲 ORANG TUA",
    "ibu": "❤️ IBU",
    "ayah": "🛡️ AYAH",
    "cinta": "❤️ CINTA",
    "takut": "😨 TAKUT",
    "berani": "🦁 BERANI",
    "kuat": "💪 KUAT",
    "hebat": "🔥 HEBAT",
    "penting": "❗ PENTING",
    "kunci": "🔑 KUNCI UTAMA",
    "solusi": "💡 SOLUSI",
    "masalah": "⚡ MASALAH",
    "permasalahan": "⚡ PERMASALAHAN",
    "kenapa": "❓ KENAPA?",
    "mengapa": "❓ MENGAPA?",
    "bagaimana": "💡 BAGAIMANA?",
    "bukti": "🔍 BUKTI NYATA",
    "benar": "✅ KEBENARAN",
    "salah": "❌ SALAH",
    "jujur": "💎 JUJUR",
    "amanah": "🛡️ AMANAH",
    "adil": "⚖️ KEADILAN"
}


def run_command(cmd: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True
    )


def _is_valid_video_file(path: str) -> bool:
    """Memastikan file yang diunduh benar-benar memiliki stream video/audio yang valid (bukan halaman HTML)."""
    if not path or not os.path.exists(path) or os.path.getsize(path) < 4096:
        return False
    try:
        with open(path, "rb") as f:
            head = f.read(512).lstrip().lower()
            if head.startswith(b"<!doctype html") or head.startswith(b"<html"):
                return False
        res = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return res.returncode == 0 and float(res.stdout.strip() or "0") > 0.1
    except Exception:
        return False


def download_google_photos_video(url: str, output_dir: str, progress_callback: Optional[Callable[[int, str], None]] = None) -> str:
    """
    Mengunduh video dari tautan berbagi Google Photos (photos.app.goo.gl / photos.google.com).
    Mengekstrak base media URL (lh3.googleusercontent.com / video-downloads.googleusercontent.com)
    lalu mengunduh stream video MP4 asli menggunakan parameter '=dv' / '=m37' / '=m22' / '=m18'.
    """
    import urllib.request
    import http.cookiejar

    if progress_callback:
        progress_callback(10, "Menghubungkan ke Google Photos & mengekstrak stream video...")

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,video/mp4,*/*;q=0.8",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    out_file = str(Path(output_dir) / f"gphotos_{uuid.uuid4().hex[:6]}.mp4")

    # Jika URL sudah berupa link googleusercontent langsung
    if "googleusercontent.com" in url:
        base_u = url.split("=")[0]
        candidates = [url, f"{base_u}=m22", f"{base_u}=m37", f"{base_u}=dv", f"{base_u}=m18"]
        final_url = url
        raw_html = ""
    else:
        req = urllib.request.Request(url, headers=headers)
        try:
            with opener.open(req, timeout=30) as resp:
                final_url = resp.geturl()
                ctype = (resp.headers.get("Content-Type") or "").lower()
                if ctype.startswith("video/"):
                    with open(out_file, "wb") as out:
                        shutil.copyfileobj(resp, out)
                    if _is_valid_video_file(out_file):
                        return out_file
                raw_html = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            raise RuntimeError(f"Gagal membuka halaman Google Photos: {e}")

        # Deteksi jika link yang ditempel adalah link privat 'photos.google.com/photo/...' yang diarahkan ke halaman Login Google
        if "accounts.google.com" in final_url or "ServiceLogin" in final_url:
            raise RuntimeError(
                "Link 'photos.google.com/photo/...' adalah link privat akun Google (terkunci login). "
                "Solusi: Di Google Foto, klik tombol 'Bagikan' (Share) -> pilih 'Buat link' (Create link) "
                "hingga mendapat link 'https://photos.app.goo.gl/...', lalu tempelkan link tersebut di sini! "
                "(Atau tekan Shift+D di Google Foto untuk unduh ke PC lalu klik ikon 📁)."
            )

        def _clean_html(h: str) -> str:
            return (
                h.replace("\\u003d", "=")
                .replace("\\u0026", "&")
                .replace("\\/", "/")
                .replace("&amp;", "&")
            )

        html_clean = _clean_html(raw_html)

        # Jika halaman share album memiliki sub-link item '/share/.../photo/...?key=...', ambil juga halaman item tersebut
        sub_links = re.findall(r"https://photos\.google\.com/share/[A-Za-z0-9_\-]+/photo/[A-Za-z0-9_\-]+\?key=[A-Za-z0-9_\-]+", html_clean)
        if not sub_links:
            rel_subs = re.findall(r"/share/[A-Za-z0-9_\-]+/photo/[A-Za-z0-9_\-]+\?key=[A-Za-z0-9_\-]+", html_clean)
            sub_links = [f"https://photos.google.com{s}" for s in rel_subs]
        for sub_u in sub_links[:2]:
            try:
                with opener.open(urllib.request.Request(sub_u, headers=headers), timeout=20) as r2:
                    html_clean += "\n" + _clean_html(r2.read().decode("utf-8", errors="ignore"))
            except Exception:
                pass

        candidates: List[str] = []

        # 1. Cek link video-downloads.googleusercontent.com langsung
        for m in re.findall(r"https://video-downloads\.googleusercontent\.com/[^\s\"'<>\\]+", html_clean):
            if m not in candidates:
                candidates.append(m)

        # 2. Cek meta og:video jika tersedia
        for m in re.findall(r'<meta[^>]+property=["\']og:video[^"\']*["\'][^>]+content=["\']([^"\']+)["\']', html_clean):
            if m not in candidates:
                candidates.append(m)

        # 3. Ambil base URL media dari og:image dan lh3.googleusercontent.com/pw/...
        base_urls: List[str] = []
        for m in re.findall(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html_clean):
            if "googleusercontent.com" in m:
                b = m.split("=")[0]
                if b not in base_urls:
                    base_urls.append(b)

        for m in re.findall(r"https://lh3\.googleusercontent\.com/(?:pw/)?[A-Za-z0-9_\-/]+", html_clean):
            b = m.split("=")[0]
            tail = b.rsplit("/", 1)[-1]
            if len(tail) >= 28 and b not in base_urls:
                base_urls.append(b)

        # Prioritaskan stream HD MP4 cepat (=m22 720p, =m37 1080p) sebelum =dv (raw besar) dan =m18 (360p)
        for suffix in ("=m22", "=m37", "=dv", "=m18"):
            for b in base_urls[:6]:
                cand = f"{b}{suffix}"
                if cand not in candidates:
                    candidates.append(cand)

    # Coba unduh dari kandidat URL sampai dapat stream video yang valid (dengan progres MB real-time)
    for cand_url in candidates:
        try:
            req = urllib.request.Request(cand_url, headers=headers)
            with opener.open(req, timeout=25) as resp:
                ctype = (resp.headers.get("Content-Type") or "").lower()
                if ctype.startswith("image/") or ctype.startswith("text/html"):
                    continue
                total_bytes = int(resp.headers.get("Content-Length") or 0)
                downloaded = 0
                chunk_size = 512 * 1024
                with open(out_file, "wb") as out:
                    while True:
                        buf = resp.read(chunk_size)
                        if not buf:
                            break
                        out.write(buf)
                        downloaded += len(buf)
                        if progress_callback:
                            mb_done = downloaded / (1024 * 1024)
                            if total_bytes > 0:
                                mb_tot = total_bytes / (1024 * 1024)
                                pct = min(19, 12 + int(7 * downloaded / total_bytes))
                                progress_callback(pct, f"Mengunduh video Google Photos: {mb_done:.1f} / {mb_tot:.1f} MB...")
                            else:
                                progress_callback(15, f"Mengunduh video Google Photos: {mb_done:.1f} MB...")
            if _is_valid_video_file(out_file):
                return out_file
        except Exception:
            continue

    # Fallback ke yt-dlp jika ekstraktor di atas belum berhasil
    if YT_DLP_AVAILABLE:
        try:
            return download_youtube_video(url, output_dir, progress_callback)
        except Exception:
            pass

    if os.path.exists(out_file):
        try:
            os.remove(out_file)
        except Exception:
            pass

    raise RuntimeError(
        "Gagal mengunduh video dari link Google Photos. Pastikan: (1) Item yang dibagikan adalah VIDEO (bukan foto), "
        "(2) Video sudah selesai diproses di Google Photos, atau (3) Gunakan Google Drive dengan izin 'Anyone with the link'."
    )


def download_remote_video(url: str, output_dir: str, progress_callback: Optional[Callable[[int, str], None]] = None) -> str:
    """
    Universally downloads video from YouTube, Google Drive, Google Photos, Dropbox, or direct web URLs.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    clean_url = url.strip()

    # 1. Google Photos (photos.app.goo.gl / photos.google.com / googleusercontent.com)
    if any(k in clean_url for k in ("photos.app.goo.gl", "photos.google.com", "googleusercontent.com")):
        return download_google_photos_video(clean_url, output_dir, progress_callback)

    # 2. Google Drive
    if "drive.google.com" in clean_url or "docs.google.com" in clean_url:
        if progress_callback:
            progress_callback(10, "Menghubungkan ke Google Drive & mengunduh video...")
        try:
            import gdown
            out_file = str(Path(output_dir) / f"gdrive_{uuid.uuid4().hex[:6]}.mp4")
            downloaded = gdown.download(url=clean_url, output=out_file, quiet=False, fuzzy=True)
            if downloaded and _is_valid_video_file(downloaded):
                return downloaded
            if YT_DLP_AVAILABLE:
                return download_youtube_video(clean_url, output_dir, progress_callback)
            raise RuntimeError("File gagal diunduh atau link Google Drive bukan file video yang valid.")
        except Exception as e:
            raise RuntimeError(f"Gagal mengunduh dari Google Drive: {str(e)}. Pastikan link diatur ke 'Anyone with the link' (Siapa saja yang memiliki link).")

    # 3. YouTube & Platform Sosial Media (yt-dlp)
    if any(k in clean_url for k in ("youtube.com", "youtu.be", "tiktok.com", "instagram.com", "facebook.com", "fb.watch", "twitter.com", "x.com", "vimeo.com")):
        return download_youtube_video(clean_url, output_dir, progress_callback)

    # 4. Dropbox
    if "dropbox.com" in clean_url:
        clean_url = clean_url.replace("?dl=0", "?dl=1")
        if "?dl=" not in clean_url:
            clean_url += "?dl=1"

    # 5. Direct / Generic HTTP/HTTPS URL
    if clean_url.startswith("http://") or clean_url.startswith("https://"):
        if progress_callback:
            progress_callback(15, "Mengunduh video dari tautan web...")
        import urllib.request
        out_file = str(Path(output_dir) / f"web_{uuid.uuid4().hex[:6]}.mp4")
        req = urllib.request.Request(clean_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                ctype = (resp.headers.get("Content-Type") or "").lower()
                if not ctype.startswith("text/html"):
                    with open(out_file, 'wb') as out:
                        shutil.copyfileobj(resp, out)
                    if _is_valid_video_file(out_file):
                        return out_file
        except Exception:
            pass
        if os.path.exists(out_file):
            try:
                os.remove(out_file)
            except Exception:
                pass
        if YT_DLP_AVAILABLE:
            try:
                return download_youtube_video(clean_url, output_dir, progress_callback)
            except Exception as e:
                raise RuntimeError(f"Tautan web tidak berisi stream video langsung yang dapat diunduh: {e}")
        raise RuntimeError("Tautan web tersebut adalah halaman HTML, bukan file video langsung (.mp4).")

    raise ValueError(f"Tautan tidak dikenali: {clean_url}")


def download_youtube_video(url: str, output_dir: str, progress_callback: Optional[Callable[[int, str], None]] = None) -> str:
    if not YT_DLP_AVAILABLE:
        raise RuntimeError("yt-dlp is not installed.")

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_template = str(Path(output_dir) / "yt_%(id)s.%(ext)s")

    ydl_opts = {
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': out_template,
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True
    }

    if progress_callback:
        progress_callback(15, "Menghubungkan ke YouTube & mengunduh video...")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if not filename.endswith(".mp4"):
            mp4_name = str(Path(filename).with_suffix(".mp4"))
            if os.path.exists(mp4_name):
                filename = mp4_name
        return filename


def get_video_duration(video_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    res = run_command(cmd)
    try:
        return float(res.stdout.strip())
    except ValueError:
        return 0.0


def extract_audio(video_path: str, audio_out_path: str, max_duration: Optional[float] = None) -> str:
    Path(audio_out_path).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y"]
    if max_duration and max_duration > 0:
        cmd.extend(["-t", str(max_duration)])
    cmd.extend([
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_out_path
    ])
    run_command(cmd)
    return audio_out_path


def transcribe_audio_with_progress(
    audio_path: str,
    total_audio_dur: float,
    model_size: str = "base",
    niche: str = "universal",
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Dict[str, Any]:
    if not FASTER_WHISPER_AVAILABLE:
        raise RuntimeError("faster-whisper is not installed.")

    model = WhisperModel(
        model_size,
        device="cpu",
        compute_type="int8",
        cpu_threads=10,
        num_workers=2
    )

    init_prompt = DEFAULT_PROMPTS.get(niche, DEFAULT_PROMPTS["universal"])
    beam = 3 if model_size in ["base", "small", "medium"] else 2

    segments_generator, info = model.transcribe(
        audio_path,
        language="id",
        beam_size=beam,
        initial_prompt=init_prompt,
        condition_on_previous_text=False,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=400)
    )

    segments = []
    full_text_list = []
    effective_dur = max(total_audio_dur, info.duration if hasattr(info, "duration") else 1.0)

    for seg in segments_generator:
        words = []
        if hasattr(seg, "words") and seg.words:
            for w in seg.words:
                corrected_word = apply_phonetic_corrections(w.word.strip())
                words.append({
                    "word": corrected_word,
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "probability": round(w.probability, 3)
                })

        corrected_seg_text = apply_phonetic_corrections(seg.text.strip())
        segments.append({
            "id": seg.id,
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": corrected_seg_text,
            "words": words
        })
        full_text_list.append(corrected_seg_text)

        if progress_callback and effective_dur > 0:
            current_sec = seg.end
            pct = 20 + int((current_sec / effective_dur) * 40)
            pct = min(pct, 59)
            curr_min = int(current_sec // 60)
            tot_min = int(effective_dur // 60)
            progress_callback(
                pct,
                f"Mentranskripsi: Menit {curr_min} dari {tot_min} ({int((current_sec/effective_dur)*100)}%)..."
            )

    return {
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "duration": round(info.duration, 2),
        "full_text": " ".join(full_text_list),
        "segments": segments
    }


def find_viral_clips(
    transcript_data: Dict[str, Any],
    niche: str = "universal",
    min_duration: float = 25.0,
    max_duration: float = 60.0,
    top_k: int = 3
) -> List[Dict[str, Any]]:
    segments = transcript_data.get("segments", [])
    if not segments:
        return []

    # 1. Coba kurasi menggunakan AI (Gemini / SumoPod / 9Router) jika diaktifkan & memiliki API Key
    try:
        import ai_brain
        ai_selected = ai_brain.curate_viral_clips_with_ai(
            transcript_data=transcript_data,
            niche=niche,
            min_duration=min_duration,
            max_duration=max_duration,
            top_k=top_k,
        )
        if ai_selected:
            return ai_selected
    except Exception as ai_err:
        print(f"[Info] Fallback ke kurasi lokal: {ai_err}")

    # 2. Fallback Algoritma Lokal (Heuristik) jika AI tidak aktif / offline
    HOOK_KEYWORDS = [
        "tahukah", "kenapa", "mengapa", "bagaimana", "rahasia", "kunci",
        "jangan", "seringkali", "banyak orang", "banyak yang salah", "waspada",
        "hati-hati", "pernahkah", "satu hal", "faktanya", "kesalahan", "tips",
        "uang", "bisnis", "sukses", "gagal", "mindset", "aturan", "hukumnya",
        "paling penting", "kamu harus tahu", "ternyata", "masalahnya", "solusinya"
    ]

    candidates = []

    for i in range(len(segments)):
        seg_start = segments[i]["start"]
        current_text = []
        current_words = []

        for j in range(i, len(segments)):
            seg_end = segments[j]["end"]
            dur = seg_end - seg_start
            current_text.append(segments[j]["text"])
            current_words.extend(segments[j].get("words", []))

            if dur >= min_duration:
                if dur <= max_duration:
                    combined_text = " ".join(current_text)
                    first_sentence = segments[i]["text"].lower()

                    hook_score = 72.0
                    for kw in HOOK_KEYWORDS:
                        if kw in first_sentence:
                            hook_score += 6.0

                    if "?" in segments[i]["text"] or "apakah" in first_sentence:
                        hook_score += 8.0

                    lower_body = combined_text.lower()
                    kw_count = sum(1 for kw in HOOK_KEYWORDS if kw in lower_body)
                    hook_score += min(kw_count * 2.5, 12.0)

                    if 35.0 <= dur <= 50.0:
                        hook_score += 5.0

                    if combined_text.endswith((".", "!", "?")):
                        hook_score += 4.0

                    hook_score = min(round(hook_score, 1), 98.5)
                    title = generate_catchy_title(segments[i]["text"], combined_text, niche)

                    candidates.append({
                        "start_time": seg_start,
                        "end_time": seg_end,
                        "duration": round(dur, 2),
                        "hook_score": hook_score,
                        "hook_title": title,
                        "text": combined_text,
                        "words": current_words
                    })
                else:
                    break

    candidates.sort(key=lambda x: x["hook_score"], reverse=True)

    niche_cfg = NICHE_CONFIGS.get(niche, NICHE_CONFIGS["universal"])
    selected: List[Dict[str, Any]] = []

    for cand in candidates:
        overlap = False
        for sel in selected:
            if not (cand["end_time"] <= sel["start_time"] or cand["start_time"] >= sel["end_time"]):
                overlap_dur = min(cand["end_time"], sel["end_time"]) - max(cand["start_time"], sel["start_time"])
                if overlap_dur > 8.0:
                    overlap = True
                    break
        if not overlap:
            cand["clip_id"] = f"clip_{len(selected) + 1}"
            cand["hashtags"] = niche_cfg["hashtags"]
            selected.append(cand)
            if top_k > 0 and top_k < 99 and len(selected) >= top_k:
                break

    return selected


def generate_catchy_title(opening_sentence: str, full_clip_text: str, niche: str = "universal") -> str:
    clean = re.sub(r"[^A-Za-z0-9À-ÿ\s\-]", "", apply_phonetic_corrections(opening_sentence)).strip()
    words = [w for w in clean.split() if len(w) > 1 or w.lower() in ("di", "ke")]
    picked = words[:6] if len(words) > 6 else words
    # Buang kata sambung gantung di ujung judul agar tidak terputus canggung (misal "DUA ORANG KALAU")
    dangling = {"kalau", "jika", "bila", "yang", "dan", "atau", "di", "ke", "dari", "untuk", "pada", "dengan", "karena", "adalah", "itu", "ini", "ketika", "saat", "bahwa"}
    while len(picked) > 3 and picked[-1].lower() in dangling:
        picked.pop()
    base = " ".join(picked).upper() if picked else "POIN PENTING"

    lower_full = full_clip_text.lower()
    
    if niche == "bisnis":
        if "uang" in lower_full or "modal" in lower_full or "omset" in lower_full:
            prefix = "STRATEGI CUAN: "
        elif "gagal" in lower_full or "rugi" in lower_full:
            prefix = "HINDARI INI! "
        else:
            prefix = "KUNCI BISNIS: "
    elif niche == "podcast":
        if "?" in opening_sentence:
            prefix = "PERTANYAAN MENARIK: "
        else:
            prefix = "POINT PENTING: "
    elif niche == "motivasi":
        prefix = "INGAT INI! "
    elif niche == "edukasi":
        if "?" in opening_sentence:
            prefix = "TAHUKAH ANDA? "
        else:
            prefix = "FAKTA PENTING: "
    elif niche == "gaming":
        prefix = "EPIC MOMENT! "
    elif niche == "kajian":
        if "shalat" in lower_full or "sholat" in lower_full:
            prefix = "HATI-HATI! "
        elif "pahala" in lower_full:
            prefix = "MASYA ALLAH! "
        else:
            prefix = "RENUNGAN: "
    else:
        # Universal
        if "?" in opening_sentence or "kenapa" in lower_full:
            prefix = "TAHUKAH KAMU? "
        elif "rahasia" in lower_full or "kunci" in lower_full:
            prefix = "RAHASIA BESAR: "
        else:
            prefix = "VIRAL: "

    return f"{prefix}{base}"


DEFAULT_PROMPTS = {
    "kajian": (
        "Transkripsi ceramah kajian Islam bahasa Indonesia yang jelas dan rapi: "
        "Allah Subhanahu wa Ta'ala, Rasulullah shallallahu 'alaihi wa sallam, Al-Qur'an, hadits, "
        "para sahabat, kaum muslimin, keluarga, mendidik anak perempuan, sabar, syukur, pahala, surga, "
        "ustadz, syariat, ibadah, akhlak, taubat, sedekah, doa."
    ),
    "bisnis": (
        "Transkripsi podcast bisnis, keuangan, investasi saham, omset, modal, cashflow, ROI, "
        "strategi marketing, entrepreneur, valuasi, margin, profit, eksekusi, founder, startup."
    ),
    "podcast": (
        "Transkripsi podcast dan wawancara bahasa Indonesia yang rapi dengan tanda baca, koma, "
        "titik, tanda tanya, dan kosakata percakapan yang jelas."
    ),
    "motivasi": (
        "Transkripsi motivasi dan pengembangan diri, mindset, kebiasaan, disiplin, fokus, "
        "produktivitas, impian, kegagalan, kesuksesan, inspirasi."
    ),
    "edukasi": (
        "Transkripsi materi edukasi, kuliah, sains, wawasan pengetahuan, sejarah, teknologi, fakta ilmiah."
    ),
    "gaming": (
        "Transkripsi gameplay dan gaming highlight, clutch, win, epic moment, streaming, pro player."
    ),
    "universal": (
        "Transkripsi video bahasa Indonesia dengan ejaan yang akurat, huruf kapital, dan tanda baca tepat."
    )
}

PHONETIC_CORRECTIONS = [
    (r"\bkomus limit\b", "kaum muslimin"),
    (r"\btemusikin\b", "kaum muslimin"),
    (r"\bperanggung hud\b", "Perang Uhud"),
    (r"\bperang hud\b", "Perang Uhud"),
    (r"\bjahas rapitu\b", "jasad para syuhada"),
    (r"\bjahas\b", "jasad"),
    (r"\bhidika asi\b", "indikasi"),
    (r"\brosululloh\b", "Rasulullah"),
    (r"\balloh\b", "Allah"),
    (r"\bsholat\b", "shalat"),
    (r"\bkealahan\b", "kekalahan"),
    (r"\bpenyalangan\b", "penyerangan"),
    # Arabic / Qur'an verses common in Islamic lectures
    (r"\bfokun keliukal kalbi\b", "fazzhan ghalizhal qalb"),
    (r"\bfokun keliukal\b", "fazzhan ghalizha"),
    (r"\bkalbi hatinya kasab\b", "ghalizhal qalb hatinya kasar"),
    (r"\blentoknya min\b", "lanfadhdhu min hawlik"),
    (r"\bkuberhasilan\b", "keberhasilan"),
    (r"\blemah lembut kepada\b", "lemah-lembut kepada mereka"),
    (r"\bwadahi wa salam\b", "'alaihi wa sallam"),
    (r"\bhadishadis\b", "hadits-hadits"),
    (r"\bsebutar\b", "seputar"),
    (r"\bmasyibahas\b", "masih bahas"),
    (r"\balalah\b", "adalah"),
    (r"\blogikar\b", "logika"),
    (r"\bnajalan\b", "nggak jalan"),
    (r"\btimkel\b", "titel"),
    (r"\btelbunyatnya\b", "sebenarnya"),
    (r"\bperumpuan\b", "perempuan"),
    (r"\bmarau\b", "marah"),
    (r"\bdaripang\b", "gampang"),
    (r"\bsebeginak\b", "sebegitu"),
    (r"\bmajoritasnya\b", "mayoritasnya"),
    (r"\bmajoritas\b", "mayoritas"),
    (r"\busama bin zet\b", "Usamah bin Zaid"),
    (r"\busama bin zed\b", "Usamah bin Zaid"),
    (r"\busama\b", "Usamah"),
    (r"\bzet\b", "Zaid"),
    (r"\bzed\b", "Zaid"),
    (r"\btermu daya\b", "termuda yang"),
    (r"\btermudai\b", "termuda"),
    (r"\btermu\b", "termuda"),
    (r"\bditunduk\b", "ditunjuk"),
    (r"\bulakukan\b", "lakukan"),
]


def apply_phonetic_corrections(text: str) -> str:
    res = text
    for pattern, replacement in PHONETIC_CORRECTIONS:
        res = re.sub(pattern, replacement, res, flags=re.IGNORECASE)
    return res


def create_ass_subtitles(
    words: List[Dict[str, Any]],
    clip_start_time: float,
    ass_path: str,
    font_name: str = "Arial",
    font_size: int = 50
) -> str:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hormozi,{font_name},{font_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,2,60,60,680,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def format_ass_time(sec: float) -> str:
        sec = max(0.0, sec)
        hrs = int(sec // 3600)
        mins = int((sec % 3600) // 60)
        secs = sec % 60
        return f"{hrs:d}:{mins:02d}:{secs:05.2f}"

    # Fast 2-3 words per line for snappy Hormozi pacing
    CHUNK_SIZE = 3
    events = []

    i = 0
    while i < len(words):
        chunk = words[i:i + CHUNK_SIZE]
        if not chunk:
            break

        for idx, active_word in enumerate(chunk):
            w_start = max(0.0, active_word["start"] - clip_start_time)
            w_end = max(w_start + 0.28, active_word["end"] - clip_start_time)

            line_parts = []
            for j, w in enumerate(chunk):
                raw_corrected = apply_phonetic_corrections(w["word"]).upper()
                clean_lower = re.sub(r"[^\w]", "", raw_corrected.lower())
                is_power = clean_lower in EMOJI_MAP
                display_w = raw_corrected

                if j == idx:
                    # Pop-bounce transform: active word pops up 122% (130% for power words) and settles back
                    hi_col = "&H004ADE80&" if is_power else "&H0000F5FF&"
                    pop_sc = 130 if is_power else 120
                    line_parts.append(
                        rf"{{\t(0,80,\fscx{pop_sc}\fscy{pop_sc})\t(80,160,\fscx100\fscy100)\c{hi_col}\b1}}"
                        + display_w
                        + r"{\r}"
                    )
                elif is_power:
                    line_parts.append(r"{\c&H0080F5FF&\b1}" + display_w)
                else:
                    line_parts.append(r"{\c&H00FFFFFF&\b1}" + display_w)

            dialogue_text = " ".join(line_parts)
            events.append(
                f"Dialogue: 0,{format_ass_time(w_start)},{format_ass_time(w_end)},Hormozi,,0,0,0,,{dialogue_text}"
            )

        i += CHUNK_SIZE

    Path(ass_path).write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    return ass_path


def render_clip_to_9_16(
    source_video: str,
    clip_info: Dict[str, Any],
    output_mp4: str,
    niche: str = "universal",
    custom_watermark: Optional[str] = None,
    add_sfx: bool = True,
    intensity: str = "normal",
    subtitle_size: str = "small",
    watermark_image: Optional[str] = None,
    watermark_pos: str = "top_right",
    progress_callback: Optional[Callable[[str, str], None]] = None
) -> str:
    try:
        import pro_editor
        edl = pro_editor.render_clip_pro(
            source_video=source_video,
            clip_info=clip_info,
            output_mp4=output_mp4,
            niche=niche,
            custom_watermark=custom_watermark,
            intensity=intensity,
            subtitle_size=subtitle_size,
            watermark_image=watermark_image,
            watermark_pos=watermark_pos,
            progress_callback=progress_callback
        )
        clip_info["edl"] = edl
        if "duration" in edl:
            clip_info["duration"] = round(float(edl["duration"]), 2)
        return output_mp4
    except Exception as pro_err:
        print(f"[Warning] pro_editor fallback to legacy render: {pro_err}")

    start_sec = clip_info["start_time"]
    end_sec = clip_info["end_time"]
    duration = max(1.0, end_sec - start_sec)
    hook_title = clip_info.get("hook_title", "HIGHLIGHT VIRAL")
    words = clip_info.get("words", [])

    base_dir = Path(__file__).resolve().parent
    temp_dir = base_dir / "uploads/temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    ass_filename = f"{clip_info['clip_id']}.ass"
    ass_path = temp_dir / ass_filename
    sub_sizes = {"compact": 42, "small": 50, "medium": 64, "large": 78}
    target_font_size = sub_sizes.get(str(subtitle_size).lower(), 50) if isinstance(subtitle_size, str) else int(subtitle_size)
    create_ass_subtitles(words, start_sec, str(ass_path), font_size=target_font_size)

    relative_ass = f"uploads/temp/{ass_filename}"
    clean_title = apply_phonetic_corrections(hook_title).replace("'", "").replace(":", " -")

    niche_cfg = NICHE_CONFIGS.get(niche, NICHE_CONFIGS["universal"])
    top_header_text = custom_watermark if custom_watermark and custom_watermark.strip() else niche_cfg["header_tag"]
    # Clean non-alphanumeric chars for drawtext safety on Windows
    clean_header = re.sub(r"[^\w\s\-\&]", "", top_header_text).strip()

    sfx_whoosh = base_dir / "static/sfx/whoosh_fast.wav"
    sfx_pop = base_dir / "static/sfx/pop_clean.wav"
    sfx_chime = base_dir / "static/sfx/chime_gold.wav"

    # 1. Video Filter:
    # - Blurred pillarbox background
    # - Dynamic camera punch-in every 4s (wide 1.0x vs punch 1.30x)
    # - Subtle flash transition at 4s camera cut (0.12s white flash)
    # - Top animated neon green progress bar
    # - Sliding Hook Badge overlay at t=0-4s
    # - Floating B-Roll Card at t=5.0s to 10.0s (Key Takeaway)
    # - Dynamic pop-bounce Hormozi subtitles at chest level (MarginV=650)
    card_title = "HIKMAH & DALIL PENTING" if niche == "kajian" else "POINT UTAMA & STRATEGI"
    filter_v = (
        "[0:v]split=2[bg_in][fg_in];"
        "[bg_in]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.18[bg];"
        "[fg_in]crop=w='if(between(mod(t,8),0,4), in_w, in_w/1.30)':h='if(between(mod(t,8),0,4), in_h, in_h/1.30)':x='(in_w-out_w)/2':y='(in_h-out_h)/3.2',scale=1080:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[base_vid];"
        "[base_vid]drawbox=x=0:y=0:w=1080:h=1920:color=white@0.32:t=fill:enable='between(t,3.95,4.08)'[flash_vid];"
        f"[flash_vid]drawbox=x=0:y=0:w='1080*(t/{duration:.2f})':h=14:color=0x10B981@1:t=fill[prog_vid];"
        f"[prog_vid]drawbox=x='if(lt(t,0.4), -500+1400*t, 80)':y=150:w=920:h=90:color=0x0F172A@0.92:t=fill:enable='between(t,0,4)',"
        f"drawbox=x='if(lt(t,0.4), -500+1400*t, 80)':y=150:w=920:h=90:color=0xF59E0B@1:t=3:enable='between(t,0,4)',"
        f"drawtext=text='{clean_header}':font='Segoe UI':fontsize=28:fontcolor=0xFBBF24:x='if(lt(t,0.4), -470+1400*t, 110)':y=165:enable='between(t,0,4)',"
        f"drawtext=text='{clean_title}':font='Segoe UI':fontsize=36:fontcolor=0xFFFFFF:x='if(lt(t,0.4), -470+1400*t, 110)':y=195:enable='between(t,0,4)'[header_vid];"
        f"[header_vid]drawbox=x='if(lt(t,5.5), -400+800*(t-5.0), 140)':y=290:w=800:h=80:color=0x047857@0.92:t=fill:enable='between(t,5.0,10.0)',"
        f"drawbox=x='if(lt(t,5.5), -400+800*(t-5.0), 140)':y=290:w=800:h=80:color=0x34D399@1:t=3:enable='between(t,5.0,10.0)',"
        f"drawtext=text='{card_title}':font='Segoe UI':fontsize=30:fontcolor=0xFFFFFF:x='if(lt(t,5.5), -370+800*(t-5.0), 180)':y=315:enable='between(t,5.0,10.0)',"
        f"subtitles=filename='{relative_ass}'[outv]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_sec),
        "-to", str(end_sec),
        "-i", source_video
    ]

    has_sfx = add_sfx and sfx_whoosh.exists()

    if has_sfx:
        cmd.extend([
            "-i", str(sfx_whoosh)
        ])

        # Clean 2-track audio mix:
        # Original voice 100% intact (0dB) + 1 subtle whoosh at camera cut (4.0s)
        # normalize=0 prevents any audio drop or crackling static
        audio_filter = (
            "[0:a]volume=1.0[voice];"
            "[1:a]adelay=3950|3950,volume=0.20[sfx_w];"
            "[voice][sfx_w]amix=inputs=2:duration=first:normalize=0[outa]"
        )

        filter_complex = f"{filter_v};{audio_filter}"
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "[outa]"
        ])
    else:
        cmd.extend([
            "-filter_complex", filter_v,
            "-map", "[outv]",
            "-map", "0:a"
        ])

    cmd.extend([
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_mp4
    ])

    subprocess.run(cmd, cwd=str(base_dir), check=True)
    return output_mp4
