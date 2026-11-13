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
    "belajar": "📚 BELAJAR"
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
    model_size: str = "tiny",
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

    segments_generator, info = model.transcribe(
        audio_path,
        language="id",
        beam_size=1,
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
                words.append({
                    "word": w.word.strip(),
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "probability": round(w.probability, 3)
                })

        segments.append({
            "id": seg.id,
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text.strip(),
            "words": words
        })
        full_text_list.append(seg.text.strip())

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

    # Broad hook triggers across all niches
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
            if len(selected) >= top_k:
                break

    return selected


def generate_catchy_title(opening_sentence: str, full_clip_text: str, niche: str = "universal") -> str:
    clean = re.sub(r"[^\w\s]", "", opening_sentence).strip()
    words = clean.split()
    base = " ".join(words[:6]).upper() if len(words) > 6 else clean.upper()

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


def create_ass_subtitles(
    words: List[Dict[str, Any]],
    clip_start_time: float,
    ass_path: str,
    font_name: str = "Arial",
    font_size: int = 56
) -> str:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,4,2,60,60,340,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def format_ass_time(sec: float) -> str:
        sec = max(0.0, sec)
        hrs = int(sec // 3600)
        mins = int((sec % 3600) // 60)
        secs = sec % 60
        return f"{hrs:d}:{mins:02d}:{secs:05.2f}"

    CHUNK_SIZE = 4
    events = []

    i = 0
    while i < len(words):
        chunk = words[i:i + CHUNK_SIZE]
        if not chunk:
            break

        for idx, active_word in enumerate(chunk):
            w_start = max(0.0, active_word["start"] - clip_start_time)
            w_end = max(w_start + 0.25, active_word["end"] - clip_start_time)

            line_parts = []
            for j, w in enumerate(chunk):
                raw_w = w["word"].upper()
                clean_lower = re.sub(r"[^\w]", "", w["word"].lower())

                display_w = EMOJI_MAP.get(clean_lower, raw_w)

                if j == idx:
                    # Highlight active word in neon yellow/green with slight pop scale
                    line_parts.append(r"{\c&H0000F5FF&\b1\fscx108\fscy108}" + display_w + r"{\r}")
                else:
                    line_parts.append(r"{\c&H00FFFFFF&\b1}" + display_w)

            dialogue_text = " ".join(line_parts)
            events.append(
                f"Dialogue: 0,{format_ass_time(w_start)},{format_ass_time(w_end)},Default,,0,0,0,,{dialogue_text}"
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
    add_sfx: bool = True
) -> str:
    start_sec = clip_info["start_time"]
    end_sec = clip_info["end_time"]
    hook_title = clip_info.get("hook_title", "HIGHLIGHT VIRAL")
    words = clip_info.get("words", [])

    base_dir = Path(__file__).resolve().parent
    temp_dir = base_dir / "uploads/temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    ass_filename = f"{clip_info['clip_id']}.ass"
    ass_path = temp_dir / ass_filename
    create_ass_subtitles(words, start_sec, str(ass_path))

    relative_ass = f"uploads/temp/{ass_filename}"
    clean_title = hook_title.replace("'", "").replace(":", " -")
    sfx_whoosh = "static/sfx/whoosh_fast.wav"

    niche_cfg = NICHE_CONFIGS.get(niche, NICHE_CONFIGS["universal"])
    top_header_text = custom_watermark if custom_watermark and custom_watermark.strip() else niche_cfg["header_tag"]
    box_color = niche_cfg["header_color"]
    border_color = niche_cfg["border_color"]

    filter_complex = (
        f"[0:v]split=2[bg_in][fg_in];"
        f"[bg_in]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.12[bg];"
        f"[fg_in]scale=1080:-2[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2[vid];"
        f"[vid]drawbox=x=60:y=120:w=960:h=180:color={box_color}@0.92:t=fill,"
        f"drawbox=x=60:y=120:w=960:h=180:color={border_color}@1:t=4,"
        f"drawtext=text='{top_header_text}':font='Segoe UI':fontsize=28:fontcolor=0xFBBF24:x=100:y=145,"
        f"drawtext=text='{clean_title}':font='Segoe UI':fontsize=40:fontcolor=0xFFFFFF:x=100:y=195,"
        f"subtitles=filename='{relative_ass}'[outv]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_sec),
        "-to", str(end_sec),
        "-i", source_video
    ]

    has_sfx = add_sfx and (base_dir / sfx_whoosh).exists()
    if has_sfx:
        cmd.extend([
            "-i", str(base_dir / sfx_whoosh),
            "-filter_complex", filter_complex + ";[0:a][1:a]amix=inputs=2:duration=first:weights=1 0.4[outa]",
            "-map", "[outv]",
            "-map", "[outa]"
        ])
    else:
        cmd.extend([
            "-filter_complex", filter_complex,
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
