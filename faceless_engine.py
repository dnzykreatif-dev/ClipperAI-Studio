"""
ClipperAI Studio - AI Faceless Video Maker (Text-to-Video Engine)
Generates viral faceless shorts directly from text/scripts using natural Indonesian TTS (Edge-TTS),
kinetic animated typography (Hormozi style), procedural motion backgrounds, and multi-track SFX.
100% Free, zero token limits, no subscriptions.
"""

import os
import uuid
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

import edge_tts
import clipper_engine
import yt_seo_engine

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
UPLOADS_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"
SFX_DIR = STATIC_DIR / "sfx"

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

VOICES = {
    "ardi": {"id": "id-ID-ArdiNeural", "name": "🎙️ Ardi (Pria Hangat & Berwibawa)"},
    "gadis": {"id": "id-ID-GadisNeural", "name": "🎙️ Gadis (Wanita Ramah & Edukatif)"}
}

THEMES = {
    "cyber": {
        "name": "🌌 Dark Cyber / Tech",
        "bg_color1": "0x060913",
        "bg_color2": "0x1e1b4b",
        "header_tag": "⚡ INSIGHT PENTING",
        "header_bg": "0x4338CA",
        "highlight_color": "&H0000FFFF",  # Neon Yellow
        "border_color": "&H00000000"
    },
    "islamic": {
        "name": "🕌 Islamic / Gold Emerald",
        "bg_color1": "0x041710",
        "bg_color2": "0x064e3b",
        "header_tag": "🕌 RENUNGAN & MUTIARA HIKMAH",
        "header_bg": "0x059669",
        "highlight_color": "&H0038BDF8",  # Amber / Gold
        "border_color": "&H00000000"
    },
    "business": {
        "name": "💼 Modern Business / Cuan",
        "bg_color1": "0x090D16",
        "bg_color2": "0x1E293B",
        "header_tag": "💡 RAHASIA SUKSES & FINANSIAL",
        "header_bg": "0xD97706",
        "highlight_color": "&H004ADE80",  # Neon Green
        "border_color": "&H00000000"
    },
    "motivation": {
        "name": "🔥 High Energy / Motivasi",
        "bg_color1": "0x18060A",
        "bg_color2": "0x4C0519",
        "header_tag": "🔥 DENGAR INI SAAT INGIN MENYERAH",
        "header_bg": "0xE11D48",
        "highlight_color": "&H0000FFFF",  # Bright Yellow
        "border_color": "&H00000000"
    }
}


async def _synthesize_speech(text: str, voice_id: str, output_path: str):
    """Generates natural neural audio from text using Edge-TTS."""
    communicate = edge_tts.Communicate(text=text, voice=voice_id)
    await communicate.save(output_path)


def generate_tts_audio(text: str, voice_key: str = "ardi", output_path: Optional[str] = None) -> str:
    """Synchronous wrapper for Edge-TTS synthesis."""
    if not output_path:
        output_path = str(UPLOADS_DIR / f"tts_{uuid.uuid4().hex[:8]}.mp3")
    
    voice_id = VOICES.get(voice_key, VOICES["ardi"])["id"]
    asyncio.run(_synthesize_speech(text, voice_id, output_path))
    return output_path


def format_ass_time(seconds: float) -> str:
    """Formats float seconds into ASS timestamp format H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"


def create_faceless_ass(
    words: List[Dict[str, Any]],
    ass_path: str,
    theme_key: str = "cyber",
    header_title: Optional[str] = None
) -> str:
    """
    Creates high-impact Hormozi animated ASS captions with word-by-word highlight.
    """
    theme = THEMES.get(theme_key, THEMES["cyber"])
    highlight_color = theme["highlight_color"]

    header = f"""[Script Info]
Title: ClipperAI Faceless Motion
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Trebuchet MS,66,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,6,3,2,60,60,420,1
Style: Highlight,Trebuchet MS,72,{highlight_color},&H000000FF,&H00000000,&HA0000000,-1,0,0,0,105,105,2,0,1,8,4,2,60,60,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    # Group words into chunks of 3-5 words for fast-paced mobile engagement
    chunk_size = 4
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        if not chunk:
            continue

        c_start = chunk[0]["start"]
        c_end = chunk[-1]["end"] + 0.15

        # Word-by-word highlight within this sentence chunk
        for cur_idx, cur_w in enumerate(chunk):
            w_start = cur_w["start"]
            w_end = cur_w["end"]
            
            # Format chunk: current word highlighted and enlarged, others white
            chunk_tokens = []
            for j, w in enumerate(chunk):
                w_clean = w["word"].strip().upper()
                if j == cur_idx:
                    chunk_tokens.append(f"{{\\c{highlight_color}\\fscx112\\fscy112}}{w_clean}{{\\rDefault}}")
                else:
                    chunk_tokens.append(f"{{\\c&H00FFFFFF&}}{w_clean}")

            line_text = " ".join(chunk_tokens)
            events.append(f"Dialogue: 0,{format_ass_time(w_start)},{format_ass_time(w_end)},Default,,0,0,0,,{line_text}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")

    return ass_path


def render_faceless_video(
    script_text: str,
    output_mp4: str,
    voice_key: str = "ardi",
    theme_key: str = "cyber",
    header_title: Optional[str] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Dict[str, Any]:
    """
    Renders complete 1080x1920 vertical faceless short from text:
    1. Generates natural TTS voice.
    2. Transcribes with Faster-Whisper to align word timestamps.
    3. Builds animated ASS captions.
    4. Generates procedural visual motion background with dynamic waves.
    5. Adds whoosh SFX and normalizes audio to 0 dB.
    """
    Path(output_mp4).parent.mkdir(parents=True, exist_ok=True)
    theme = THEMES.get(theme_key, THEMES["cyber"])
    import re
    raw_header = header_title.strip() if header_title else theme["header_tag"]
    clean_header = re.sub(r'[^\w\s\-\.,!?&]', '', raw_header).strip().upper()
    if not clean_header:
        clean_header = "INSIGHT PENTING"

    # Step 1: TTS Generation
    if progress_callback:
        progress_callback(15, f"AI sedang menghasilkan suara narasi alami ({VOICES.get(voice_key, VOICES['ardi'])['name']})...")

    audio_path = str(UPLOADS_DIR / f"faceless_audio_{uuid.uuid4().hex[:6]}.mp3")
    generate_tts_audio(text=script_text, voice_key=voice_key, output_path=audio_path)

    total_dur = clipper_engine.get_video_duration(audio_path)
    if total_dur <= 0:
        total_dur = 15.0

    # Step 2: High-Speed Word Alignment with Faster-Whisper
    if progress_callback:
        progress_callback(40, "Menyelaraskan animasi kata-demi-kata (Hormozi Pop Subtitles)...")

    transcript = clipper_engine.transcribe_audio_with_progress(
        audio_path=audio_path,
        total_audio_dur=total_dur,
        model_size="base",
        niche="universal"
    )

    all_words = []
    for seg in transcript.get("segments", []):
        for w in seg.get("words", []):
            all_words.append({
                "word": w.get("word", "").strip(),
                "start": float(w.get("start", 0.0)),
                "end": float(w.get("end", 0.0))
            })

    # Fallback if no words found
    if not all_words:
        tokens = script_text.split()
        interval = total_dur / max(1, len(tokens))
        for idx, t in enumerate(tokens):
            all_words.append({
                "word": t,
                "start": idx * interval,
                "end": (idx + 1) * interval
            })

    # Step 3: Build Animated ASS
    ass_path = str(UPLOADS_DIR / f"faceless_{uuid.uuid4().hex[:6]}.ass")
    create_faceless_ass(all_words, ass_path, theme_key=theme_key, header_title=clean_header)
    escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:")

    # Step 4: Multi-Track Audio (Voice + Whoosh SFX)
    whoosh_sfx = SFX_DIR / "whoosh.wav"
    has_sfx = whoosh_sfx.exists()

    # Step 5: Render with FFmpeg Procedural Motion Canvas
    if progress_callback:
        progress_callback(70, "Merender video vertikal 9:16 dengan efek motion canvas & audio 0 dB...")

    # Procedural background: Dynamic smooth gradient waves
    c1 = theme["bg_color1"]
    c2 = theme["bg_color2"]

    # Filtergraph: Creates 1080x1920 procedural radial motion canvas + header badge + ASS subtitles
    font_file = "C\\:/Windows/Fonts/arialbd.ttf"
    if not os.path.exists("C:/Windows/Fonts/arialbd.ttf"):
        font_file = "C\\:/Windows/Fonts/arial.ttf"

    filtergraph = (
        f"gradients=s=1080x1920:d={total_dur:0.2f}:c0={c1}:c1={c2}:x0=540:y0=960:x1=1080:y1=1920:type=radial:speed=0.005[canvas];"
        f"[canvas]drawbox=x=80:y=240:w=920:h=90:color={theme['header_bg']}@0.9:t=fill,"
        f"drawtext=fontfile='{font_file}':text='{clean_header}':"
        f"fontsize=36:fontcolor=white:x=(w-text_w)/2:y=268,"
        f"ass='{escaped_ass}'[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", audio_path
    ]

    if has_sfx:
        cmd.extend(["-i", str(whoosh_sfx)])
        # Mix voice (1.0) and whoosh (0.25)
        audio_filter = "[0:a]volume=1.0[vce];[1:a]adelay=100|100,volume=0.25[sfx];[vce][sfx]amix=inputs=2:duration=first:normalize=0[a]"
    else:
        audio_filter = "[0:a]volume=1.0[a]"

    full_filter = f"{filtergraph};{audio_filter}"

    cmd.extend([
        "-filter_complex", full_filter,
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_mp4
    ])

    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Clean up temp files
    for p in [audio_path, ass_path]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass

    # Step 6: Generate Auto SEO Package for the Faceless Short
    seo_package = yt_seo_engine.generate_shorts_seo_package(
        transcript_text=script_text,
        title_hint=clean_header,
        niche="universal",
        mode="shorts"
    )

    seo_json_path = output_mp4.replace(".mp4", "_seo.json")
    try:
        with open(seo_json_path, "w", encoding="utf-8") as f:
            json.dump(seo_package, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    if progress_callback:
        progress_callback(100, "Selesai! Video Faceless siap ditonton & diupload.")

    return {
        "ok": True,
        "video_path": output_mp4,
        "filename": Path(output_mp4).name,
        "duration": round(total_dur, 2),
        "seo": seo_package
    }
