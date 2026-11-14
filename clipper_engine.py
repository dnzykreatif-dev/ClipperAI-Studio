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


DEFAULT_PROMPTS = {
    "kajian": (
        "Transkripsi ceramah agama Islam, ayat Al-Qur'an dan hadits: "
        "فَبِمَا رَحْمَةٍ مِنَ اللَّهِ لِنْتَ لَهُمْ وَلَوْ كُنْتَ فَظًّا غَلِيظَ الْقَلْبِ لَانْفَضُّوا مِنْ حَوْلِكَ "
        "(Fabima rahmatin minallahi linta lahum walau kunta fazzhan ghalizhal qalb lanfadhdhu min hawlik), "
        "lemah lembut, hatinya kasar, Nabi shallallahu 'alaihi wasallam, para sahabat, "
        "Perang Uhud, kaum muslimin, para syuhada, Rasulullah, indikasi, dalil, syariat."
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
    font_size: int = 66
) -> str:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hormozi,{font_name},{font_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,4,2,60,60,650,1

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

                display_w = EMOJI_MAP.get(clean_lower, raw_corrected)

                if j == idx:
                    # Pop-bounce transform: active word pops up 120% and settles back
                    line_parts.append(
                        r"{\t(0,80,\fscx120\fscy120)\t(80,160,\fscx100\fscy100)\c&H0000F5FF&\b1}"
                        + display_w
                        + r"{\r}"
                    )
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
    add_sfx: bool = True
) -> str:
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
    create_ass_subtitles(words, start_sec, str(ass_path))

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
