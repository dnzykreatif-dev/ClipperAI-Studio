"""
ClipperAI Studio - Pro Editor (Fase 1-4 Terintegrasi + Aset Argon)

Mengubah video mentah (16:9 maupun 9:16) menjadi Shorts/Reels dengan editing profesional:
  1. Face Tracking (YuNet OpenCV DNN) -> auto-reframe mengikuti wajah pembicara
  2. Auto Jump-Cut (membuang jeda hening > 0.45s) + pemecahan multi-shot (7-12 shot / klip)
  3. 4 Mode Kamera & Visual B-Roll (Close 1.38x, Medium 1.15x, B-Roll Cinema Split Card, Wide)
  4. Transisi Visual Nyata di setiap pergantian shot (Flash-Bloom + Light-Leak Argon + Whoosh SFX)
  5. Keyword Pop Callout & B-Roll Takeaway Card berkepercayaan tinggi (filter probabilitas Whisper)
  6. Color Grading 3D LUT Argon (VL0001..VL0096) + Overlay Light-Leak/Film (VL0201..VL0281)
  7. Audio Broadcast Mastering: Highpass + FFT Denoise + Compressor + Multi-SFX + Loudnorm -14 LUFS
  8. EDL JSON (Edit Decision List) + Verifikasi QA Otomatis & Contact Sheet (.qa.jpg)
"""

from __future__ import annotations

import json
import random
import re
import shutil
import subprocess
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

import clipper_engine as ce

try:
    import cv2
    CV2_OK = True
except Exception:  # pragma: no cover
    CV2_OK = False

BASE_DIR = Path(__file__).resolve().parent
ASSETS = BASE_DIR / "assets"
ARGON = ASSETS / "argon"
YUNET = ASSETS / "models" / "face_detection_yunet_2023mar.onnx"

FPS = 30
OUT_W, OUT_H = 1080, 1920

STOPWORDS = set(
    "yang dan di ke dari ini itu untuk dengan pada adalah akan atau juga tidak ada ya sudah "
    "saya kita kamu anda mereka kami dia kalau jadi karena sebagai oleh dalam bisa lebih sangat "
    "banyak sekali seperti ketika sehingga namun tetapi tapi bahwa agar supaya yaitu yakni "
    "apa gimana kenapa mengapa bagaimana terus lalu nah itulah dimana pun saja masih harus "
    "sebuah seorang suatu para setiap semua seluruh bagian adapun seputar tentang".split()
)
POWER_WORDS = set(
    "rahasia kunci gagal sukses uang bisnis jangan waspada bahaya penting ternyata fakta "
    "kesalahan hikmah pahala dosa taubat ikhlas sabar syukur surga neraka amanah ilmu "
    "mindset disiplin konsisten modal untung rugi gratis wajib haram halal doa shalat "
    "pendidikan keluarga anak orangtua akhlak iman takwa sedekah rezeki berkah".split()
)

# Preset gaya per niche: LUT / overlay / SFX Argon + warna aksen ASS (BGR) + warna frame (RGB hex)
PRESETS: Dict[str, Dict[str, Any]] = {
    "kajian":    dict(lut="VL0001", lut_s=0.55, overlay="VL0201", ov_s=0.22, accent="&H0038B8F5&", hex="0xF59E0B", badge="HIKMAH & POIN INTI"),
    "bisnis":    dict(lut="VL0076", lut_s=0.55, overlay="VL0281", ov_s=0.28, accent="&H004ADE80&", hex="0x10B981", badge="STRATEGI & INSIGHT"),
    "podcast":   dict(lut="VL0096", lut_s=0.50, overlay="VL0231", ov_s=0.18, accent="&H0000F5FF&", hex="0x38BDF8", badge="SOROTAN UTAMA"),
    "motivasi":  dict(lut="VL0091", lut_s=0.60, overlay="VL0201", ov_s=0.24, accent="&H0000F5FF&", hex="0xF43F5E", badge="MINDSET PENTING"),
    "edukasi":   dict(lut="VL0096", lut_s=0.50, overlay="VL0231", ov_s=0.18, accent="&H0000F5FF&", hex="0x6366F1", badge="CATATAN MATERI"),
    "gaming":    dict(lut="VL0031", lut_s=0.60, overlay="VL0281", ov_s=0.30, accent="&H00F5FF00&", hex="0xA855F7", badge="HIGHLIGHT MOMENT"),
    "universal": dict(lut="VL0096", lut_s=0.50, overlay="VL0231", ov_s=0.18, accent="&H0000F5FF&", hex="0xF59E0B", badge="POIN PENTING"),
}

INTENSITY = {
    "halus":   dict(shot=(3.8, 5.5), push=0.05, punch=0.06, flash=0.16),
    "normal":  dict(shot=(2.6, 4.2), push=0.08, punch=0.12, flash=0.24),
    "agresif": dict(shot=(1.9, 3.1), push=0.11, punch=0.18, flash=0.30),
}

GAP_CUT = 0.45
PAD_IN, PAD_OUT = 0.06, 0.12


def _run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=str(BASE_DIR), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace"
    )


def _run_ok(cmd: List[str]) -> None:
    r = _run(cmd)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg gagal: " + r.stderr[-1500:])


def _snap(t: float) -> float:
    return round(t * FPS) / FPS


def probe_video(path: str) -> Tuple[int, int, float]:
    r = _run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-show_entries", "format=duration", "-of", "json", path
    ])
    j = json.loads(r.stdout)
    st = j["streams"][0]
    return int(st["width"]), int(st["height"]), float(j["format"]["duration"])


# ----------------------------------------------------------------------------
# 1. Face Tracking
# ----------------------------------------------------------------------------
def track_faces(src: str, t0: float, t1: float, step: float = 0.5) -> List[Tuple[float, float, float, float]]:
    if not (CV2_OK and YUNET.exists()):
        return []
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        return []
    fw = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    fh = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    scale = 640.0 / fw if fw > 640 else 1.0
    dw, dh = int(fw * scale), int(fh * scale)
    try:
        det = cv2.FaceDetectorYN.create(str(YUNET), "", (dw, dh), 0.65, 0.3, 5000)
    except Exception:
        cap.release()
        return []
    out = []
    t = t0
    while t <= t1:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000.0)
        ok, frame = cap.read()
        if ok:
            small = cv2.resize(frame, (dw, dh)) if scale != 1.0 else frame
            det.setInputSize((dw, dh))
            _, faces = det.detect(small)
            if faces is not None and len(faces):
                f = max(faces, key=lambda r: r[2] * r[3])
                x, y, w, h = f[0], f[1], f[2], f[3]
                out.append((t, float((x + w / 2) / dw), float((y + h / 2) / dh), float(h / dh)))
        t += step
    cap.release()
    return out


def face_for_range(track, a: float, b: float, fallback) -> Tuple[float, float, float]:
    pts = [p for p in track if a - 0.3 <= p[0] <= b + 0.3]
    if not pts:
        return fallback
    return (
        float(np.median([p[1] for p in pts])),
        float(np.median([p[2] for p in pts])),
        float(np.median([p[3] for p in pts])),
    )


# ----------------------------------------------------------------------------
# 2. Shot Planning (Jump-Cut + Multi-Shot + B-Roll Spotlight)
# ----------------------------------------------------------------------------
def plan_shots(
    words: List[Dict[str, Any]], clip_start: float, clip_end: float,
    intensity: str, rng: random.Random
) -> List[Dict[str, Any]]:
    cfg = INTENSITY[intensity]
    ws = [w for w in words if w["end"] > clip_start and w["start"] < clip_end and w.get("word", "").strip()]
    ws.sort(key=lambda w: w["start"])
    if not ws:
        return [dict(a=_snap(clip_start), b=_snap(clip_end), words=[])]

    shots: List[Dict[str, Any]] = []
    cur: List[Dict[str, Any]] = []
    target = rng.uniform(*cfg["shot"])

    def close(cws):
        a = max(clip_start, cws[0]["start"] - PAD_IN)
        b = min(clip_end, cws[-1]["end"] + PAD_OUT)
        a, b = _snap(a), _snap(b)
        if b - a < 0.6:
            b = a + 0.6
        shots.append(dict(a=a, b=b, words=list(cws)))

    for i, w in enumerate(ws):
        cur.append(w)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        if nxt is None:
            break
        gap = nxt["start"] - w["end"]
        dur = w["end"] - cur[0]["start"]
        punct = w["word"].strip()[-1:] in ".,?!;:"
        if gap > GAP_CUT:
            close(cur); cur = []; target = rng.uniform(*cfg["shot"])
        elif dur >= target and (punct or gap >= 0.12 or dur >= cfg["shot"][1] + 0.9):
            close(cur); cur = []; target = rng.uniform(*cfg["shot"])

    if cur:
        if shots and (cur[-1]["end"] - cur[0]["start"]) < 1.1 and cur[0]["start"] - shots[-1]["words"][-1]["end"] <= GAP_CUT:
            shots[-1]["words"].extend(cur)
            shots[-1]["b"] = _snap(min(clip_end, cur[-1]["end"] + PAD_OUT))
        else:
            close(cur)
    return shots


# Siklus kamera yang memberi variasi nyata bahkan dari 1 kamera vertikal maupun horizontal:
# close (1.38x) -> medium (1.14x) -> broll_card (Cinema Split Card) -> close -> wide (1.0x) -> medium -> broll_card
FRAMING_CYCLE = ["close", "medium", "broll_card", "close", "wide", "medium", "broll_card", "close"]


def assign_framing(shots: List[Dict[str, Any]], vertical_source: bool, rng: random.Random) -> None:
    for i, s in enumerate(shots):
        dur = s["b"] - s["a"]
        if i == 0:
            f = "close"
        else:
            f = FRAMING_CYCLE[i % len(FRAMING_CYCLE)]
            # broll_card paling bagus untuk shot >= 2.0 detik
            if f == "broll_card" and dur < 1.8:
                f = "medium"
        if i > 0 and f == shots[i - 1].get("framing"):
            f = "medium" if f != "medium" else "close"
        s["framing"] = f


# ----------------------------------------------------------------------------
# 3. Render Shot (4 Mode Kamera: close, medium, wide, broll_card)
# ----------------------------------------------------------------------------
def build_shot_filter(shot: Dict[str, Any], src_w: int, src_h: int, face, dur: float, cfg, accent_hex: str) -> str:
    framing = shot["framing"]
    push, punch = cfg["push"], cfg["punch"]
    # Kurva zoom dinamis per-frame: punch cepat di 0.28s pertama + push-in halus sepanjang shot
    zexpr = f"(1+{push}*t/{dur:.3f}+{punch}*pow(max(0\\,1-t/0.28)\\,2))"
    cx, cy, fh = face
    vertical_src = (src_w / src_h) < 0.7

    # Mode 1: B-ROLL CINEMA SPLIT CARD (Visual Pattern Interrupt)
    if framing == "broll_card":
        # Ambil crop 9:11 sekitar wajah untuk ditempatkan di dalam Cinema Viewport Card (880x1080 di y=400)
        if src_w / src_h >= 880 / 1080:
            ch = int(src_h * 0.82)
            cw = int(ch * 880 / 1080)
        else:
            cw = int(src_w * 0.88)
            ch = int(cw * 1080 / 880)
        cw = max(16, (cw // 2) * 2)
        ch = max(16, (ch // 2) * 2)
        x = int(min(max(cx * src_w - cw / 2, 0), max(0, src_w - cw)))
        y = int(min(max(cy * src_h - 0.42 * ch, 0), max(0, src_h - ch)))
        scale_card = f"scale=w='trunc(880*{zexpr}/2)*2':h=-2:eval=frame:flags=bicubic,crop=880:1080"
        return (
            "[0:v]split=2[bg0][fg0];"
            "[bg0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "boxblur=30:6,eq=brightness=-0.26:saturation=0.80:contrast=1.08,"
            "drawbox=x=70:y=165:w=940:h=190:color=0x0F172A@0.92:t=fill,"
            f"drawbox=x=70:y=165:w=940:h=190:color={accent_hex}@0.95:t=4,"
            f"drawbox=x=70:y=165:w=18:h=190:color={accent_hex}@1:t=fill,"
            f"drawbox=x=92:y=392:w=896:h=1096:color={accent_hex}@0.95:t=6[bg];"
            f"[fg0]crop={cw}:{ch}:{x}:{y},{scale_card}[fg];"
            "[bg][fg]overlay=100:400,fps=30,format=yuv420p,setsar=1[v]"
        )

    # Mode 2: WIDE pada sumber landscape 16:9 (blurred pillarbox + zoom)
    if framing == "wide" and not vertical_src:
        scale_w = f"scale=w='trunc(1080*{zexpr}/2)*2':h=-2:eval=frame:flags=bicubic"
        return (
            "[0:v]split[a][b];"
            "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "boxblur=25:5,eq=brightness=-0.18:saturation=0.9[bg];"
            f"[b]{scale_w},crop=1080:ih[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=30,format=yuv420p,setsar=1[v]"
        )

    # Mode 3 & 4: CLOSE (1.40x), MEDIUM (1.16x), atau WIDE vertikal (1.00x)
    if src_w / src_h >= 9 / 16:
        ch0 = src_h
    else:
        ch0 = src_w * 16 / 9

    if framing == "close":
        z = 1.42
    elif framing == "medium":
        z = 1.16
    else:  # wide pada sumber vertikal
        z = 1.00

    if fh < 0.12 and framing != "wide":
        z *= 1.10
    z = min(z, 1.68)
    ch = ch0 / z
    m = max(1, int(ch / 32))
    ch = min(src_h, 32 * m)
    cw = min(src_w, 18 * m)
    x = int(min(max(cx * src_w - cw / 2, 0), max(0, src_w - cw)))
    # Sedikit variasi posisi vertikal antara close dan medium agar cut terasa nyata
    y_bias = 0.38 if framing == "close" else 0.43
    y = int(min(max(cy * src_h - y_bias * ch, 0), max(0, src_h - ch)))

    scale = f"scale=w='trunc(1080*{zexpr}/2)*2':h=-2:eval=frame:flags=bicubic"
    return (
        f"[0:v]crop={cw}:{ch}:{x}:{y},{scale},crop=1080:1920,"
        "fps=30,format=yuv420p,setsar=1[v]"
    )


def render_shot(
    src: str, shot: Dict[str, Any], idx: int, src_w: int, src_h: int,
    face, cfg, accent_hex: str, tmp: Path
) -> str:
    dur = shot["b"] - shot["a"]
    out = str(tmp / f"shot_{idx:03d}.mp4")
    fg = build_shot_filter(shot, src_w, src_h, face, dur, cfg, accent_hex)
    cmd = [
        "ffmpeg", "-y", "-ss", f"{shot['a']:.3f}", "-i", src, "-t", f"{dur:.3f}",
        "-filter_complex", fg, "-map", "[v]", "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p",
        "-r", str(FPS), out
    ]
    _run_ok(cmd)
    return out


# ----------------------------------------------------------------------------
# 4. Keyword Pop, B-Roll Card Takeaway & Opening Hook Banner (ASS Layer)
# ----------------------------------------------------------------------------
def pick_keyword(shot_words: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    best, best_score = None, 0.0
    for w in shot_words:
        prob = float(w.get("probability", 1.0))
        raw = ce.apply_phonetic_corrections(w.get("word", "")).strip()
        t = re.sub(r"[^\w]", "", raw.lower())
        if len(t) < 4 or t in STOPWORDS:
            continue
        # Hindari kata hasil halusinasi ASR ber-probabilitas rendah kecuali ada di POWER_WORDS
        if prob < 0.78 and t not in POWER_WORDS:
            continue
        score = min(len(t), 10) + (12 if t in POWER_WORDS else 0) + (prob * 4.0)
        if score > best_score:
            best, best_score = dict(w, word=raw), score
    return best


def summarize_shot_phrase(shot_words: List[Dict[str, Any]]) -> str:
    """Ambil frasa inti 4-6 kata dari shot untuk ditampilkan pada B-Roll Card."""
    tokens = []
    for w in shot_words:
        cleaned = re.sub(r"[^\w\-]", "", ce.apply_phonetic_corrections(w.get("word", ""))).strip()
        if cleaned:
            tokens.append(cleaned.upper())
    if not tokens:
        return "POIN PENTING PEMBAHASAN"
    # Cari posisi power word jika ada
    for idx, tok in enumerate(tokens):
        if tok.lower() in POWER_WORDS:
            start = max(0, idx - 1)
            return " ".join(tokens[start:start + 5])
    return " ".join(tokens[:5])


def _ass_time(sec: float) -> str:
    sec = max(0.0, sec)
    return f"{int(sec // 3600)}:{int((sec % 3600) // 60):02d}:{sec % 60:05.2f}"


def build_ass(
    remapped_words: List[Dict[str, Any]],
    keyword_events: List[Dict[str, Any]],
    broll_cards: List[Dict[str, Any]],
    hook_banner: Dict[str, Any],
    accent: str,
    ass_path: Path,
) -> None:
    ce.create_ass_subtitles(remapped_words, 0.0, str(ass_path))
    txt = ass_path.read_text(encoding="utf-8")

    extra_styles = (
        "Style: KwBadge,Segoe UI,54,&H00FFFFFF,&H0000FFFF,&H000F172A,&HC80F172A,-1,0,0,0,100,100,1.5,0,3,18,0,5,40,40,0,1\n"
        "Style: BrollTag,Segoe UI,30,&H0038BDF8,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,3,0,7,0,0,0,1\n"
        "Style: BrollBody,Segoe UI,42,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0.5,0,1,3,0,7,0,0,0,1\n"
    )
    txt = txt.replace("\n[Events]", extra_styles + "\n[Events]", 1)
    lines: List[str] = []

    # 1. Opening Hook Banner (t=0.05..3.2s)
    if hook_banner:
        ht0, ht1 = 0.05, min(3.2, hook_banner["dur"])
        h_tag = hook_banner["header"]
        h_title = hook_banner["title"][:38]
        lines.append(
            f"Dialogue: 2,{_ass_time(ht0)},{_ass_time(ht1)},BrollTag,,0,0,0,,"
            rf"{{\an7\pos(108,162)\fad(120,180)\1c{accent}}}★ {h_tag}"
        )
        lines.append(
            f"Dialogue: 2,{_ass_time(ht0)},{_ass_time(ht1)},BrollBody,,0,0,0,,"
            rf"{{\an7\pos(108,202)\fad(120,180)\1c&H00FFFFFF&}}{h_title}"
        )

    # 2. B-Roll Cinema Split Cards (teks di dalam kotak atas x=70..1010, y=165..355)
    for bc in broll_cards:
        bt0, bt1 = bc["t0"], bc["t1"]
        lines.append(
            f"Dialogue: 3,{_ass_time(bt0)},{_ass_time(bt1)},BrollTag,,0,0,0,,"
            rf"{{\an7\pos(112,188)\fad(100,140)\1c{accent}}}✦ {bc['badge']}"
        )
        lines.append(
            f"Dialogue: 3,{_ass_time(bt0)},{_ass_time(bt1)},BrollBody,,0,0,0,,"
            rf"{{\an7\pos(112,238)\fad(140,140)\1c&H00FFFFFF&}}{bc['phrase']}"
        )

    # 3. Keyword Pop Callout Badge (di atas dada y=320, tidak menabrak subtitle utama di y=1270)
    for ev in keyword_events:
        word = re.sub(r"[^\w\s\-]", "", ev["text"]).upper()
        t0, t1 = ev["t"], ev["t"] + ev["d"]
        anim = (
            r"{\an5\pos(540,320)\fad(60,140)\fscx75\fscy75"
            r"\t(0,110,\fscx112\fscy112)\t(110,220,\fscx100\fscy100)"
            rf"\1c{accent}" + "}"
        )
        lines.append(f"Dialogue: 2,{_ass_time(t0)},{_ass_time(t1)},KwBadge,,0,0,0,,{anim}⚡ {word}")

    ass_path.write_text(txt.rstrip("\n") + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------
# 5. Audio: Speech Trim + Multi-SFX Bed
# ----------------------------------------------------------------------------
def build_speech(src: str, shots: List[Dict[str, Any]], out_wav: Path) -> None:
    parts, labels = [], []
    for i, s in enumerate(shots):
        d = s["b"] - s["a"]
        parts.append(
            f"[0:a]atrim={s['a']:.3f}:{s['b']:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:d=0.015,afade=t=out:st={max(0.0, d - 0.015):.3f}:d=0.015[a{i}]"
        )
        labels.append(f"[a{i}]")
    fc = ";".join(parts) + f";{''.join(labels)}concat=n={len(shots)}:v=0:a=1,aresample=48000[a]"
    _run_ok([
        "ffmpeg", "-y", "-i", src, "-filter_complex", fc, "-map", "[a]",
        "-ac", "2", "-c:a", "pcm_s16le", str(out_wav)
    ])


def _read_wav(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as w:
        n, ch, sw = w.getnframes(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16 if sw == 2 else np.uint8).astype(np.float32)
    a = a / 32768.0 if sw == 2 else (a - 128.0) / 128.0
    a = a.reshape(-1, ch)
    return a if ch == 2 else np.repeat(a, 2, axis=1)


def build_sfx_bed(events: List[Dict[str, Any]], total: float, out_wav: Path) -> None:
    sr = 48000
    bed = np.zeros((int((total + 1.0) * sr), 2), dtype=np.float32)
    cache: Dict[str, np.ndarray] = {}
    for ev in events:
        f = ARGON / "sfx" / f"{ev['id']}.wav"
        if not f.exists():
            continue
        if ev["id"] not in cache:
            cache[ev["id"]] = _read_wav(f)
        a = cache[ev["id"]] * ev["gain"]
        s = max(0, int(ev["t"] * sr))
        e = min(len(bed), s + len(a))
        if e > s:
            bed[s:e] += a[: e - s]
    bed = np.clip(bed, -1.0, 1.0)
    pcm = (bed * 32767).astype(np.int16)
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(pcm.tobytes())


# ----------------------------------------------------------------------------
# 6. Main Entry: render_clip_pro
# ----------------------------------------------------------------------------
def render_clip_pro(
    source_video: str,
    clip_info: Dict[str, Any],
    output_mp4: str,
    niche: str = "universal",
    custom_watermark: Optional[str] = None,
    intensity: str = "normal",
) -> Dict[str, Any]:
    intensity = intensity if intensity in INTENSITY else "normal"
    preset = PRESETS.get(niche, PRESETS["universal"])
    cfg = INTENSITY[intensity]
    clip_id = clip_info.get("clip_id", "clip")
    rng = random.Random(f"{clip_id}-{clip_info['start_time']:.2f}")

    tmp = BASE_DIR / "uploads" / "temp" / f"pro_{clip_id}_{rng.randint(1000, 9999)}"
    tmp.mkdir(parents=True, exist_ok=True)

    c0, c1 = float(clip_info["start_time"]), float(clip_info["end_time"])
    src_w, src_h, _ = probe_video(source_video)
    vertical = (src_w / src_h) < 0.7

    # 1. Plan shots & assign 4-mode camera framing
    words = clip_info.get("words", [])
    shots = plan_shots(words, c0, c1, intensity, rng)
    assign_framing(shots, vertical, rng)

    # 2. Face tracking
    track = track_faces(source_video, c0, c1)
    fb = face_for_range(track, c0, c1, (0.5, 0.42, 0.22))
    for s in shots:
        s["face"] = face_for_range(track, s["a"], s["b"], fb)

    # 3. Render individual shots in parallel
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = [
            ex.submit(render_shot, source_video, s, i, src_w, src_h, s["face"], cfg, preset["hex"], tmp)
            for i, s in enumerate(shots)
        ]
        files = [f.result() for f in futs]

    listf = tmp / "list.txt"
    listf.write_text("\n".join(f"file '{Path(f).as_posix()}'" for f in files), encoding="utf-8")
    vcat = tmp / "video_cat.mp4"
    _run_ok(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf), "-c", "copy", str(vcat)])

    # 4. Timeline remap + transitions + B-Roll cards + Keyword callouts + SFX cues
    t = 0.0
    remapped, kw_events, broll_cards, sfx_events, cut_times = [], [], [], [], []
    whoosh_ids = ["VL0501", "VL0502", "VL0503", "VL0504", "VL0505"]

    for i, s in enumerate(shots):
        s["t0"] = t
        d = s["b"] - s["a"]
        for w in s["words"]:
            ws_ = t + max(0.0, w["start"] - s["a"])
            we_ = t + max(0.0, w["end"] - s["a"])
            remapped.append({
                "word": w["word"], "start": ws_, "end": max(we_, ws_ + 0.1),
                "probability": w.get("probability", 1.0)
            })

        if i > 0:
            cut_times.append(round(t, 3))
            sfx_id = "VL0516" if s["framing"] == "broll_card" else whoosh_ids[i % len(whoosh_ids)]
            sfx_events.append(dict(id=sfx_id, t=max(0.0, t - 0.05), gain=0.32))
        else:
            sfx_events.append(dict(id="VL0516", t=0.02, gain=0.28))

        if s["framing"] == "broll_card":
            phrase = summarize_shot_phrase(s["words"])
            broll_cards.append(dict(t0=t + 0.05, t1=t + d - 0.05, badge=preset["badge"], phrase=phrase))
            s["broll_phrase"] = phrase
        elif t > 3.3:  # Jangan tabrak Hook Banner di 0..3.2s
            kw = pick_keyword(s["words"])
            if kw is not None:
                kt = t + max(0.20, kw["start"] - s["a"])
                if kt < t + d - 0.35:
                    kw_events.append(dict(text=kw["word"], t=kt, d=min(1.05, t + d - kt - 0.05)))
                    sfx_events.append(dict(id="VL0526", t=kt, gain=0.28))
                    s["keyword"] = kw["word"]
        t += d
    total = _snap(t)

    clean_title = re.sub(
        r"[^\w\s\-&!?]", "",
        ce.apply_phonetic_corrections(clip_info.get("hook_title", "")).replace(":", " -")
    ).strip()
    niche_cfg = ce.NICHE_CONFIGS.get(niche, ce.NICHE_CONFIGS["universal"])
    header = custom_watermark.strip() if custom_watermark and custom_watermark.strip() else niche_cfg["header_tag"]
    clean_header = re.sub(r"[^\w\s\-&]", "", header).strip()

    # Gunakan Hook Banner di 0..3.2s jika shot pertama bukan broll_card
    hook_end = min(3.2, shots[0]["b"] - shots[0]["a"] - 0.1) if shots else 2.8
    hook_banner = dict(header=clean_header, title=clean_title, dur=max(1.8, hook_end))

    ass_path = tmp / "subs.ass"
    build_ass(remapped, kw_events, broll_cards, hook_banner, preset["accent"], ass_path)

    speech = tmp / "speech.wav"
    sfxbed = tmp / "sfx.wav"
    build_speech(source_video, shots, speech)
    build_sfx_bed(sfx_events, total, sfxbed)

    # 5. Final Composite: Argon 3D LUT + Vignette + Light-Leak Overlay + Cut Flash Transitions + Hook Box + ASS
    rel = lambda p: Path(p).resolve().relative_to(BASE_DIR).as_posix()
    lut = ARGON / "luts" / f"{preset['lut']}.cube"
    ovf = ARGON / "overlays" / f"{preset['overlay']}.mp4"

    chain = [
        "[0:v]split[o][l]",
        f"[l]lut3d=file='{rel(lut)}'[lg]",
        f"[o][lg]blend=all_mode=normal:all_opacity={preset['lut_s']}[gr]",
        "[gr]vignette=PI/7[vg]",
    ]
    last = "vg"
    if ovf.exists():
        chain.append("[3:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p[ov]")
        chain.append(f"[{last}][ov]blend=all_mode=screen:all_opacity={preset['ov_s']}:shortest=1[fx]")
        last = "fx"

    # Ekspresi transisi flash halus di setiap titik cut antar-shot
    flash_terms = [f"between(t\\,{ct - 0.05:.2f}\\,{ct + 0.09:.2f})" for ct in cut_times[:16]]
    flash_enable = "+".join(flash_terms) if flash_terms else "0"
    hb_dur = hook_banner["dur"]

    chain.append(
        f"[{last}]drawbox=x=0:y=0:w=1080:h=1920:color=white@{cfg['flash']}:t=fill:enable='{flash_enable}',"
        f"drawbox=x=0:y=0:w='1080*(t/{total:.2f})':h=12:color=0x10B981@1:t=fill,"
        f"drawbox=x=80:y=148:w=920:h=110:color=0x0F172A@0.92:t=fill:enable='between(t\\,0.05\\,{hb_dur:.2f})',"
        f"drawbox=x=80:y=148:w=920:h=110:color={preset['hex']}@0.95:t=3:enable='between(t\\,0.05\\,{hb_dur:.2f})',"
        f"subtitles=filename='{rel(ass_path)}'[outv]"
    )

    achain = (
        "[1:a]highpass=f=70,afftdn=nr=8:nf=-32,"
        "acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2[sp];"
        "[sp][2:a]amix=inputs=2:duration=first:normalize=0,"
        "loudnorm=I=-14:TP=-1.5:LRA=11[outa]"
    )
    cmd = ["ffmpeg", "-y", "-i", str(vcat), "-i", str(speech), "-i", str(sfxbed)]
    if ovf.exists():
        cmd += ["-stream_loop", "-1", "-i", str(ovf)]
    cmd += [
        "-filter_complex", ";".join(chain) + ";" + achain,
        "-map", "[outv]", "-map", "[outa]",
        "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        output_mp4,
    ]
    _run_ok(cmd)

    # 6. Simpan EDL + Jalankan QA Otomatis
    edl = dict(
        format="9:16", style=niche, intensity=intensity, duration=total,
        source=Path(source_video).name,
        preset=dict(lut=preset["lut"], overlay=preset["overlay"]),
        shots=[
            dict(
                src=[s["a"], s["b"]], t0=round(s["t0"], 3), framing=s["framing"],
                face=[round(v, 3) for v in s["face"]],
                keyword=s.get("keyword"), broll_phrase=s.get("broll_phrase"),
            )
            for s in shots
        ],
        transitions=cut_times,
        broll_cards=broll_cards,
        sfx=sfx_events,
        keywords=kw_events,
    )
    Path(output_mp4).with_suffix(".edl.json").write_text(
        json.dumps(edl, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    try:
        import qa
        edl["qa"] = qa.check_video(output_mp4, expected_shots=len(shots))
    except Exception as e:
        edl["qa"] = {"error": str(e)}

    shutil.rmtree(tmp, ignore_errors=True)
    return edl
