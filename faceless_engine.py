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
from typing import Dict, Any, List, Optional, Callable, Tuple

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
    "ardi": {"id": "id-ID-ArdiNeural", "name": "🎙️ Ardi (Pria Hangat & Berwibawa - ID)"},
    "gadis": {"id": "id-ID-GadisNeural", "name": "🎙️ Gadis (Wanita Ramah & Edukatif - ID)"},
    "osman": {"id": "ms-MY-OsmanNeural", "name": "🇲🇾 Osman (Pria Santai Melayu / Korang - MS)"},
    "yasmin": {"id": "ms-MY-YasminNeural", "name": "🇲🇾 Yasmin (Wanita Lembut Melayu / Korang - MS)"},
}

THEMES = {
    "vox": {
        "name": "📜 Vox 2.5D Torn-Paper & Parallax (Dokumenter / Explainer)",
        "bg_color1": "0xE8E1D3",
        "bg_color2": "0xD8CEBA",
        "header_tag": "📜 VOX EXPLAINER • 2.5D COLLAGE",
        "header_bg": "0xB91C1C",  # Vox Crimson Red
        "highlight_color": "&H001818B9",  # Deep Red Accent in ASS (BGR)
        "border_color": "&H00000000",
        "is_vox": True,
    },
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
    """Generates natural neural audio from text using Edge-TTS with generous timeout."""
    communicate = edge_tts.Communicate(text=text, voice=voice_id)
    await asyncio.wait_for(communicate.save(output_path), timeout=60.0)


def generate_tts_audio(text: str, voice_key: str = "ardi", output_path: Optional[str] = None) -> str:
    """Synchronous wrapper for Edge-TTS synthesis with retry and validation."""
    if not output_path:
        output_path = str(UPLOADS_DIR / f"tts_{uuid.uuid4().hex[:8]}.mp3")

    voice_id = VOICES.get(voice_key, VOICES["ardi"])["id"]
    last_err = None
    for attempt in range(3):
        try:
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception:
                    pass
            asyncio.run(_synthesize_speech(text, voice_id, output_path))
            if os.path.exists(output_path) and os.path.getsize(output_path) > 2000:
                return output_path
        except Exception as e:
            last_err = e
            time.sleep(1.5)

    # Offline SAPI fallback jika koneksi internet terputus
    wav_tmp = output_path + ".wav"
    ps_cmd = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.SetOutputToWaveFile('{wav_tmp}'); "
        f"$s.Speak({json.dumps(text)}); $s.Dispose()"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if os.path.exists(wav_tmp) and os.path.getsize(wav_tmp) > 2000:
        subprocess.run(["ffmpeg", "-y", "-i", wav_tmp, "-c:a", "libmp3lame", "-q:a", "2", output_path],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            os.remove(wav_tmp)
        except Exception:
            pass
        if os.path.exists(output_path) and os.path.getsize(output_path) > 2000:
            return output_path

    raise RuntimeError(f"Gagal menghasilkan audio suara narator TTS ({last_err or 'Koneksi suara terputus'}). Mohon periksa koneksi internet.")


def direct_ai_storyboard(script_text: str, theme_key: str = "vox") -> Dict[str, Any]:
    """
    Menggunakan Otak AI (Gemini 2.5 Flash / Router) untuk bertindak sebagai Video Director:
    1. Memoles naskah suara agar mengalir natural dan padat.
    2. Memecah naskah menjadi 3-5 scene visual yang sangat dinamis dengan berbagai gaya:
       - 'stat_shock': Angka/statistik raksasa
       - 'comparison': Dua kartu sobek kontras (Sebelum vs Sesudah)
       - 'checklist': Kertas memo centang fitur bergantian
       - 'cta_slam': Ajakan bertindak tombol aksi
       - 'torn_headline': Judul punchy dengan stabilo
    """
    import ai_brain
    import re

    sys_prompt = (
        "Kamu adalah AI Executive Video Director kelas dunia untuk video vertikal 9:16 (Shorts/TikTok/Reels) "
        "bergaya Vox Explainer, Ali Abdaal, dan dokumenter modern. "
        "Tugasmu: Menganalisis naskah pengguna dan menyusun STORYBOARD VISUAL DINAMIS agar video SANGAT MENARIK, "
        "TIDAK MONOTON, dan memanjakan mata penonton. "
        "\n\nPILIHAN GAYA VISUAL (style) UNTUK SETIAP ADEGAN:\n"
        "1. 'stat_shock': Untuk angka/persentase mencengangkan (misal: '87%', '1 KLIK', '100+ SANTRI', 'Rp 0'). "
        "Wajib sertakan field 'stat_number' dan 'stat_label'.\n"
        "2. 'comparison': Untuk membandingkan cara lama vs cara baru (SEBELUM vs SESUDAH / MASALAH vs SOLUSI). "
        "Wajib sertakan field 'compare_left' dan 'compare_right'.\n"
        "3. 'checklist': Untuk daftar poin atau fitur unggulan yang dicentang. Wajib sertakan 'items' (array 2-3 string pendek).\n"
        "4. 'torn_headline': Untuk judul masalah, hook, atau pernyataan dramatis dengan kartu kertas sobek dan stabilo.\n"
        "5. 'cta_slam': Untuk adegan terakhir (Call to Action), ajakan komentar atau coba demo. Wajib sertakan 'cta_text'.\n"
        "\nATURAN KETAT:\n"
        "- Pastikan gaya visual BERBEDA-BEDA untuk tiap adegan berurutan (JANGAN ada 2 adegan berurutan dengan style sama).\n"
        "- Jika ada ajakan aksi di akhir naskah, adegan terakhir WAJIB ber-style 'cta_slam'.\n"
        "- Bahasa: Bahasa Indonesia natural, santai, dan edukatif.\n"
        "- Output: Wajib format JSON murni sesuai skema berikut:\n"
        "{\n"
        "  \"narration_script\": \"naskah lengkap yang akan dibacakan oleh narator suara (TTS)\",\n"
        "  \"scenes\": [\n"
        "    {\n"
        "      \"scene_num\": 1,\n"
        "      \"style\": \"torn_headline\" | \"stat_shock\" | \"comparison\" | \"checklist\" | \"cta_slam\",\n"
        "      \"tag\": \"LABEL SINGKAT PENDUKUNG (2-3 KATA)\",\n"
        "      \"headline\": \"Judul Inti Adegan (Maksimal 6 kata)\",\n"
        "      \"stat_number\": \"87%\",\n"
        "      \"stat_label\": \"Keterangan Angka\",\n"
        "      \"compare_left\": \"Cara Lama: Data Tercecer\",\n"
        "      \"compare_right\": \"Cara Baru: 1 Klik Rapi di HP\",\n"
        "      \"items\": [\"Absensi Realtime\", \"Pantau Hafalan\", \"Raport Digital\"],\n"
        "      \"cta_text\": \"KOMEN 'MAU DEMO' DI BAWAH\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )

    try:
        if ai_brain.is_ai_ready():
            res_str = ai_brain.generate_text(
                system_prompt=sys_prompt,
                user_prompt=f"Naskah Pengguna:\n{script_text}",
                json_mode=True,
                timeout=35
            )
            cleaned = res_str.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```[a-zA-Z]*\n", "", cleaned)
                cleaned = re.sub(r"\n```$", "", cleaned)
            data = json.loads(cleaned)
            if data.get("scenes") and len(data["scenes"]) >= 2:
                if not data.get("narration_script"):
                    data["narration_script"] = script_text
                return data
    except Exception as e:
        print(f"[AI Director Warning] AI Storyboard fallback triggered: {e}")

    # Heuristic Fallback Storyboard jika AI sedang offline
    tokens = script_text.split()
    scenes = []
    scenes.append({
        "scene_num": 1,
        "style": "torn_headline",
        "tag": "MASALAH UTAMA",
        "headline": " ".join(tokens[:5]).upper() if tokens else "INSIGHT PENTING"
    })
    scenes.append({
        "scene_num": 2,
        "style": "comparison" if len(tokens) > 20 else "checklist",
        "tag": "SOLUSI TERPADU",
        "headline": "TRANSFORMASI TOTAL",
        "compare_left": "Sebelum: Manual & Pusing",
        "compare_right": "Sesudah: 1 Klik HP Beres",
        "items": ["Absensi Otomatis", "Data Terpusat", "Akses Mudah"]
    })
    scenes.append({
        "scene_num": 3,
        "style": "cta_slam",
        "tag": "LANGKAH SEKARANG",
        "headline": "SIAP TINGKATKAN KUALITAS?",
        "cta_text": "HUBUNGI KAMI SEKARANG"
    })
    return {
        "narration_script": script_text,
        "scenes": scenes
    }



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
) -> Tuple[str, List[float], List[Dict[str, Any]]]:
    """
    Creates high-impact Hormozi animated ASS captions + Multi-Scene Visual Cards & Keyword Pops.
    Returns (ass_path, scene_cut_times, sfx_events).
    """
    import re
    import pro_editor
    theme = THEMES.get(theme_key, THEMES["cyber"])
    highlight_color = theme["highlight_color"]

    header = f"""[Script Info]
Title: ClipperAI Faceless Motion v2
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Trebuchet MS,68,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,7,3,2,60,60,380,1
Style: Highlight,Trebuchet MS,74,{highlight_color},&H000000FF,&H00000000,&HA0000000,-1,0,0,0,105,105,2,0,1,8,4,2,60,60,380,1
Style: SceneTag,Segoe UI,32,{highlight_color},&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,3,0,1,3,0,5,60,60,0,1
Style: SceneHero,Segoe UI,64,&H00FFFFFF,&H0000FFFF,&H000F172A,&HC80F172A,-1,0,0,0,100,100,1.5,0,3,22,0,5,80,80,0,1
Style: SceneSub,Segoe UI,40,&H00E2E8F0,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,4,2,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    chunk_size = 4
    scenes = []
    cur_scene = []
    for w in words:
        cur_scene.append(w)
        dur = w["end"] - cur_scene[0]["start"]
        punct = w["word"].strip()[-1:] in ".,?!;:"
        if dur >= 3.2 or (punct and dur >= 2.0):
            scenes.append(cur_scene)
            cur_scene = []
    if cur_scene:
        scenes.append(cur_scene)

    cut_times: List[float] = []
    sfx_events: List[Dict[str, Any]] = [dict(id="VL0516", t=0.02, gain=0.30)]
    whoosh_ids = ["VL0501", "VL0502", "VL0503", "VL0504", "VL0505"]

    for s_idx, sc in enumerate(scenes):
        s_start = sc[0]["start"]
        s_end = sc[-1]["end"] + 0.08
        if s_idx > 0:
            cut_times.append(round(s_start, 3))
            sfx_events.append(dict(id=whoosh_ids[s_idx % len(whoosh_ids)], t=max(0.0, s_start - 0.05), gain=0.34))

        kw = pro_editor.pick_keyword(sc)
        hero_word = re.sub(r"[^\w\-]", "", kw["word"] if kw else sc[0]["word"]).upper()
        phrase = pro_editor.summarize_shot_phrase(sc)
        sfx_events.append(dict(id="VL0526", t=s_start + 0.12, gain=0.26))

        events.append(
            f"Dialogue: 2,{format_ass_time(s_start)},{format_ass_time(s_end)},SceneTag,,0,0,0,,"
            rf"{{\an5\pos(540,620)\fad(120,140)}}✦ SCENE 0{s_idx + 1} • POIN UTAMA"
        )
        events.append(
            f"Dialogue: 2,{format_ass_time(s_start)},{format_ass_time(s_end)},SceneHero,,0,0,0,,"
            rf"{{\an5\pos(540,730)\fad(100,140)\fscx80\fscy80\t(0,140,\fscx108\fscy108)\t(140,260,\fscx100\fscy100)\1c{highlight_color}}}⚡ {hero_word}"
        )
        events.append(
            f"Dialogue: 2,{format_ass_time(s_start)},{format_ass_time(s_end)},SceneSub,,0,0,0,,"
            rf"{{\an5\pos(540,850)\fad(160,140)}}{phrase}"
        )

    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        if not chunk:
            continue
        for cur_idx, cur_w in enumerate(chunk):
            w_start = cur_w["start"]
            w_end = max(w_start + 0.18, cur_w["end"])
            chunk_tokens = []
            for j, w in enumerate(chunk):
                w_clean = w["word"].strip().upper()
                if j == cur_idx:
                    chunk_tokens.append(
                        f"{{\\t(0,80,\\fscx120\\fscy120)\\t(80,160,\\fscx100\\fscy100)\\c{highlight_color}}}{w_clean}{{\\rDefault}}"
                    )
                else:
                    chunk_tokens.append(f"{{\\c&H00FFFFFF&}}{w_clean}")
            line_text = " ".join(chunk_tokens)
            events.append(f"Dialogue: 0,{format_ass_time(w_start)},{format_ass_time(w_end)},Default,,0,0,0,,{line_text}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")

    return ass_path, cut_times, sfx_events


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

    # Step 1: AI Video Director (Storyboard & Narration Polish)
    if progress_callback:
        progress_callback(10, "Otak AI (Gemini) sedang menganalisis naskah & menyusun storyboard animasi dinamis...")

    storyboard = direct_ai_storyboard(script_text, theme_key=theme_key)
    narration_text = storyboard.get("narration_script") or script_text
    sb_scenes = storyboard.get("scenes") or []

    # Step 2: TTS Generation
    if progress_callback:
        progress_callback(25, f"AI sedang menghasilkan suara narasi alami ({VOICES.get(voice_key, VOICES['ardi'])['name']})...")

    audio_path = str(UPLOADS_DIR / f"faceless_audio_{uuid.uuid4().hex[:6]}.mp3")
    generate_tts_audio(text=narration_text, voice_key=voice_key, output_path=audio_path)

    total_dur = clipper_engine.get_video_duration(audio_path)
    if total_dur <= 0:
        total_dur = 15.0

    # Step 3: High-Speed Word Alignment with Faster-Whisper
    if progress_callback:
        progress_callback(45, "Menyelaraskan animasi kata-demi-kata (Hormozi Pop Subtitles)...")

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
        tokens = narration_text.split()
        interval = total_dur / max(1, len(tokens))
        for idx, t in enumerate(tokens):
            all_words.append({
                "word": t,
                "start": idx * interval,
                "end": (idx + 1) * interval
            })

    # Step 4: Build Animated ASS (fallback) + Motion Graphics Timeline & Argon SFX cues
    import pro_editor
    import motion_gfx as mg
    ass_path = str(UPLOADS_DIR / f"faceless_{uuid.uuid4().hex[:6]}.ass")
    _, cut_times, sfx_events = create_faceless_ass(all_words, ass_path, theme_key=theme_key, header_title=clean_header)

    accent_map = {
        "vox": "0xB91C1C",
        "cyber": "0x38BDF8",
        "islamic": "0xF59E0B",
        "business": "0x10B981",
        "motivation": "0xF43F5E",
    }
    accent_rgb = mg.hex_rgb(accent_map.get(theme_key, theme["header_bg"]))
    emoji_map = getattr(clipper_engine, "EMOJI_MAP", {}) or {}

    # Bangun scene kata dari all_words untuk sinkronisasi waktu & fallback
    scenes = []
    cur_sc = []
    for w in all_words:
        cur_sc.append(w)
        dur_sc = w["end"] - cur_sc[0]["start"]
        punct = w["word"].strip()[-1:] in ".,?!;:"
        if dur_sc >= 3.2 or (punct and dur_sc >= 2.0):
            scenes.append(cur_sc)
            cur_sc = []
    if cur_sc:
        scenes.append(cur_sc)
    if not scenes and all_words:
        scenes = [all_words]

    elements: List[Any] = []
    is_vox_style = theme.get("is_vox", False)
    whoosh_ids = ["VL0501", "VL0502", "VL0503", "VL0504", "VL0505"]

    # 1. Background Kanvas
    if is_vox_style:
        # Kertas kusut krem (Wrinkled parchment floor) untuk Vox 2.5D
        elements.append(mg.VoxParchmentBackground(total_dur, accent_rgb))
    # Untuk tema modern (islamic, cyber, dll), ffmpeg memproses radial gradient + argon light-leak di bawah

    # 2. Top Header Pill (Safe Zone Atas: y=110)
    elements.append(mg.TopHeaderPill(raw_header, total_dur, accent_rgb, y=110))

    # 3. Dynamic AI Storyboard Scenes (Hero Stage: y=680..720)
    # Satu adegan menampilkan SATU Hero Visual Card terpusat (stat_shock, comparison, checklist, cta_slam, atau headline)
    # Card is_paper=True jika tema Vox, is_paper=False (Remotion Glassmorphic) jika tema modern!
    n_scenes = max(1, len(sb_scenes))

    for s_idx, sc in enumerate(sb_scenes):
        t0 = round(s_idx * (total_dur / n_scenes), 2)
        t1 = round((s_idx + 1) * (total_dur / n_scenes) + (0.12 if s_idx < n_scenes - 1 else 0.0), 2)
        style = sc.get("style", "torn_headline")
        tag = sc.get("tag") or f"SCENE 0{s_idx + 1} • {raw_header}"
        head = sc.get("headline") or ""

        # Whoosh transisi antar adegan
        if s_idx > 0:
            sfx_events.append(dict(id=whoosh_ids[s_idx % len(whoosh_ids)], t=max(0.0, t0 - 0.06), gain=0.32))

        if style == "stat_shock":
            stat_n = sc.get("stat_number") or "100%"
            elements.append(mg.VoxBigStatCard(
                tag=tag,
                stat_num=stat_n,
                headline=head or sc.get("stat_label", "Fakta Mengejutkan"),
                t0=t0, t1=t1,
                accent=accent_rgb,
                y_top=700,
                seed=s_idx * 23 + 11,
                is_paper=is_vox_style
            ))
            sfx_events.append(dict(id="VL0511", t=t0 + 0.05, gain=0.34))

        elif style == "comparison":
            left_t = sc.get("compare_left") or "SEBELUM: CARA LAMA MANUAL"
            right_t = sc.get("compare_right") or "SESUDAH: SOLUSI OTOMATIS"
            elements.append(mg.VoxComparisonCard(
                tag=tag,
                left_text=left_t,
                right_text=right_t,
                t0=t0, t1=t1,
                accent=accent_rgb,
                y_top=680,
                seed=s_idx * 31 + 47,
                is_paper=is_vox_style
            ))
            sfx_events.append(dict(id="VL0541" if is_vox_style else "VL0503", t=t0 + 0.02, gain=0.36))
            sfx_events.append(dict(id="VL0542" if is_vox_style else "VL0504", t=t0 + 0.20, gain=0.36))

        elif style == "checklist":
            items = sc.get("items") or ["Poin 1", "Poin 2", "Poin 3"]
            elements.append(mg.VoxChecklistCard(
                tag=tag,
                headline=head or "FITUR UTAMA",
                items=items,
                t0=t0, t1=t1,
                accent=accent_rgb,
                y_top=700,
                seed=s_idx * 19 + 63,
                is_paper=is_vox_style
            ))
            sfx_events.append(dict(id="VL0541" if is_vox_style else "VL0502", t=t0 + 0.02, gain=0.34))
            for item_i in range(len(items)):
                sfx_events.append(dict(id="VL0531", t=t0 + 0.22 + item_i * 0.28, gain=0.28))

        elif style == "cta_slam":
            cta_txt = sc.get("cta_text") or "COBA SEKARANG!"
            elements.append(mg.VoxCtaCard(
                tag=tag or "LANGKAH SEKARANG",
                headline=head or "SIAP MEMULAI?",
                cta_text=cta_txt,
                t0=t0, t1=t1,
                accent=accent_rgb,
                y_top=720,
                seed=s_idx * 37 + 91,
                is_paper=is_vox_style
            ))
            sfx_events.append(dict(id="VL0516", t=t0 + 0.05, gain=0.35))

        else:  # torn_headline / default
            rot_val = (-2.0 if s_idx % 2 == 0 else 1.8) if is_vox_style else 0.0
            elements.append(mg.VoxTornCardHero(
                tag=tag,
                headline=head,
                t0=t0, t1=t1,
                accent=accent_rgb,
                y_top=680,
                rot=rot_val,
                seed=s_idx * 17 + 43,
                is_paper=is_vox_style
            ))
            sfx_events.append(dict(id="VL0541" if is_vox_style else "VL0501", t=max(0.0, t0 - 0.04), gain=0.36))

    # 4. Kinetic Subtitle Karaoke di Safe Zone Bawah (y_center=1520)
    # Terpisah lebih dari 550px dari Hero Stage di atasnya — NOL OVERLAP!
    elements.append(mg.CaptionTrack(
        all_words, accent_rgb, power_words=pro_editor.POWER_WORDS,
        emoji_map=emoji_map, y_center=1520
    ))

    # 5. Glowing Bottom Progress Bar
    elements.append(mg.ProgressBar(total_dur, accent_rgb))
    timeline = mg.Timeline(total_dur, elements)

    # Step 4: Multi-Track Argon SFX Bed
    sfx_wav = UPLOADS_DIR / f"faceless_sfx_{uuid.uuid4().hex[:6]}.wav"
    pro_editor.build_sfx_bed(sfx_events, total_dur, sfx_wav)

    # Step 5: Render with FFmpeg Procedural Motion Canvas + Argon Light-Leak + Motion Graphics RGBA Overlay
    if progress_callback:
        progress_callback(70, "Merender video 9:16 dengan Motion Graphics Remotion-Style, Argon Light-Leak & Audio -14 LUFS...")

    c1 = theme["bg_color1"]
    c2 = theme["bg_color2"]
    ov_name = "VL0201" if theme_key in ("islamic", "motivation") else "VL0281"
    ov_path = BASE_DIR / "assets" / "argon" / "overlays" / f"{ov_name}.mp4"
    has_ov = ov_path.exists() and not is_vox_style

    if is_vox_style:
        # Pada gaya Vox, lantai kanvas krem kusut sudah dirender presisi di dalam layer RGBA Motion Graphics
        v_chain = [
            f"color=c=0xEDE7DA:s=1080x1920:r=30:d={total_dur:0.2f}[grad]"
        ]
    else:
        v_chain = [
            f"gradients=s=1080x1920:r=30:d={total_dur:0.2f}:c0={c1}:c1={c2}:x0=540:y0=960:x1=1080:y1=1920:type=radial:speed=0.008[grad]"
        ]
    last_v = "grad"
    cmd = ["ffmpeg", "-y", "-i", audio_path, "-i", str(sfx_wav)]
    idx = 2
    if has_ov:
        cmd.extend(["-stream_loop", "-1", "-i", str(ov_path)])
        v_chain.append(f"[{idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p[ov]")
        v_chain.append(f"[{last_v}][ov]blend=all_mode=screen:all_opacity=0.25:shortest=1[bgfx]")
        last_v = "bgfx"
        idx += 1

    cmd.extend(["-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{mg.W}x{mg.H}", "-framerate", "30", "-i", "pipe:0"])
    v_chain.append(f"[{last_v}]vignette=PI/6[vg]")
    v_chain.append(f"[{idx}:v]format=rgba[mg]")
    v_chain.append("[vg][mg]overlay=0:0:format=auto:eof_action=pass,format=yuv420p[v]")

    audio_filter = (
        "[0:a]aresample=48000,volume=1.0[vce];"
        "[1:a]volume=1.0[sfx];"
        "[vce][sfx]amix=inputs=2:duration=first:normalize=0,"
        "loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    )

    cmd.extend([
        "-filter_complex", ";".join(v_chain) + ";" + audio_filter,
        "-map", "[v]",
        "-map", "[a]",
        "-t", f"{total_dur:0.2f}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_mp4
    ])

    log_file = UPLOADS_DIR / f"faceless_ffmpeg_{uuid.uuid4().hex[:6]}.log"
    pro_editor._encode_with_overlay(cmd, timeline, log_file)
    if log_file.exists():
        try:
            log_file.unlink()
        except Exception:
            pass

    # Clean up temp files
    for p in [audio_path, ass_path, str(sfx_wav)]:
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
