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
  9. Motion Graphics modern (motion_gfx.py): caption karaoke spring + pill, hook title card,
     stiker keyword, panel takeaway, video-card rounded, kamera ease + handheld drift.
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
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

import clipper_engine as ce
import motion_gfx as mg

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
    "sebuah seorang suatu para setiap semua seluruh bagian adapun seputar tentang "
    "kurang anaknya kemudian sekarang begini begitu misalnya contohnya pertama kedua ketiga "
    "akhirnya biasanya memang bahkan apalagi padahal sebelum sesudah setelah sampai hingga "
    "antara diantara waktu tahun orang beliau kalian engkau dirinya namanya disebut dikatakan "
    "katanya artinya maksudnya ibarat nanti tadi baru lagi pernah belum sedang hendak mau "
    "ingin punya milik melakukan dilakukan".split()
)
POWER_WORDS = set(
    "rahasia kunci gagal sukses uang bisnis jangan waspada bahaya penting ternyata fakta "
    "kesalahan hikmah pahala dosa taubat ikhlas sabar syukur surga neraka amanah ilmu "
    "mindset disiplin konsisten modal untung rugi gratis wajib haram halal doa shalat "
    "pendidikan keluarga anak orangtua akhlak iman takwa sedekah rezeki berkah "
    "nabi rasul rasulullah allah panglima perang pasukan pemimpin sahabat ulama sejarah "
    "termuda pemuda berani kuat hebat bukti nyata solusi masalah".split()
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
    "halus":   dict(shot=(4.2, 6.2), push=0.05, punch=0.06, flash=0.0),
    "normal":  dict(shot=(2.8, 4.4), push=0.07, punch=0.09, flash=0.0),
    "agresif": dict(shot=(2.2, 3.5), push=0.09, punch=0.12, flash=0.0),
}

GAP_CUT = 0.55
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


def _encode_with_overlay(cmd: List[str], timeline: "mg.Timeline", log_path: Path) -> None:
    """Jalankan ffmpeg sambil mem-pipe frame RGBA motion graphics ke stdin (render paralel, urutan terjaga)."""
    n = timeline.n_frames()
    with open(log_path, "w", encoding="utf-8", errors="replace") as lf:
        p = subprocess.Popen(cmd, cwd=str(BASE_DIR), stdin=subprocess.PIPE,
                             stdout=subprocess.DEVNULL, stderr=lf)
        try:
            with ThreadPoolExecutor(max_workers=4) as ex:
                for b in range(0, n, 24):
                    for buf in ex.map(timeline.frame, range(b, min(n, b + 24))):
                        p.stdin.write(buf)
        except (BrokenPipeError, OSError):
            pass
        finally:
            try:
                p.stdin.close()
            except Exception:
                pass
        rc = p.wait()
    if rc != 0:
        raise RuntimeError("ffmpeg gagal: " + Path(log_path).read_text(encoding="utf-8", errors="replace")[-1500:])


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
    sx = float(np.median([p[1] for p in pts]))
    sy = float(np.median([p[2] for p in pts]))
    sh = float(np.median([p[3] for p in pts]))
    # Stabilkan koordinat X/Y terhadap median seluruh klip agar deteksi palsu tidak memotong wajah
    fbx, fby, fbh = fallback
    sx = max(fbx - 0.06, min(fbx + 0.06, sx))
    sy = max(fby - 0.05, min(fby + 0.05, sy))
    return (
        0.85 * fbx + 0.15 * sx,
        0.85 * fby + 0.15 * sy,
        0.80 * fbh + 0.20 * sh,
    )


# ----------------------------------------------------------------------------
# 2. Shot Planning (Jump-Cut + Multi-Shot + Clean Camera Alternation)
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
        if b - a < 1.2:
            b = min(_snap(clip_end), a + 1.2)
        shots.append(dict(a=a, b=b, words=list(cws)))

    for i, w in enumerate(ws):
        cur.append(w)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        if nxt is None:
            break
        gap = nxt["start"] - w["end"]
        dur = w["end"] - cur[0]["start"]
        punct = w["word"].strip()[-1:] in ".,?!;:"
        if gap > GAP_CUT and dur >= 2.4:
            close(cur); cur = []; target = rng.uniform(*cfg["shot"])
        elif dur >= target and (punct or gap >= 0.18 or dur >= cfg["shot"][1] + 1.2):
            close(cur); cur = []; target = rng.uniform(*cfg["shot"])

    if cur:
        if shots and (cur[-1]["end"] - cur[0]["start"]) < 2.5 and cur[0]["start"] - shots[-1]["words"][-1]["end"] <= GAP_CUT + 0.25:
            shots[-1]["words"].extend(cur)
            shots[-1]["b"] = _snap(min(clip_end, cur[-1]["end"] + PAD_OUT))
        else:
            close(cur)

    # Gabungkan shot yang terlalu pendek (< 2.1s) agar transisi tetap ritmis dan dinamis
    merged: List[Dict[str, Any]] = []
    for s in shots:
        if merged and (s["b"] - s["a"] < 2.1 or merged[-1]["b"] - merged[-1]["a"] < 2.1):
            pause = s["a"] - merged[-1]["b"]
            if pause < 0.65:
                merged[-1]["b"] = s["b"]
                merged[-1]["words"].extend(s["words"])
                continue
        merged.append(s)
    return merged if merged else shots


# Siklus kamera profesional layar penuh (Medium <-> Close <-> Cinema Focus dengan Kartu Insight Glassmorphic)
FRAMING_CYCLE = ["medium", "close", "cinema_focus", "close", "medium", "cinema_focus"]


def assign_framing(shots: List[Dict[str, Any]], vertical_source: bool, rng: random.Random) -> None:
    for i, s in enumerate(shots):
        f = FRAMING_CYCLE[i % len(FRAMING_CYCLE)]
        if i == 0:
            f = "medium"
        elif i > 0 and f == shots[i - 1].get("framing"):
            f = "close" if f == "medium" else "medium"
        s["framing"] = f


# ----------------------------------------------------------------------------
# 3. Render Shot (Clean Full-Screen Camera: medium 1.04x, cinema_focus 1.15x, close 1.24x)
# ----------------------------------------------------------------------------
CARD_X, CARD_Y, CARD_W, CARD_H = 100, 400, 880, 1080


def build_shot_filter(shot: Dict[str, Any], src_w: int, src_h: int, face, dur: float, cfg, accent_hex: str,
                      card_pad: int = 60) -> str:
    framing = shot["framing"]
    push, punch = cfg["push"], cfg["punch"]
    # Kurva zoom dinamis per-frame dengan ease-out punch di awal shot + smooth push-in
    zexpr = f"(1+{push}*t/{max(dur, 0.5):.3f}+{punch}*pow(max(0\\,1-t/0.26)\\,3))"
    cx, cy, fh = face
    vertical_src = (src_w / src_h) < 0.7

    # WIDE pada sumber landscape 16:9 (blurred pillarbox + zoom)
    if framing == "wide" and not vertical_src:
        scale_w = f"scale=w='trunc(1080*{zexpr}/2)*2':h=-2:eval=frame"
        return (
            "[0:v]split[a][b];"
            "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "boxblur=25:5,eq=brightness=-0.20:saturation=0.9[bg];"
            f"[b]{scale_w},crop=1080:ih[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=30,format=yuv420p,setsar=1[v]"
        )

    # CLOSE (1.28x punch-in tegas), CINEMA_FOCUS (1.19x + fokus kontras), MEDIUM (1.12x full-frame bersih & potong tepi atas)
    if src_w / src_h >= 9 / 16:
        ch0 = src_h
    else:
        ch0 = src_w * 16 / 9

    if framing == "close":
        z = 1.28
    elif framing == "cinema_focus":
        z = 1.19
    elif framing == "medium":
        z = 1.12
    else:
        z = 1.08

    if fh < 0.12 and framing == "close":
        z *= 1.06
    z = min(z, 1.38)
    ch = ch0 / z
    m = max(1, int(ch / 32))
    ch = min(src_h, 32 * m)
    cw = min(src_w, 18 * m)
    x = int(min(max(cx * src_w - cw / 2, 0), max(0, src_w - cw)))
    y_bias = 0.37 if framing == "close" else (0.39 if framing == "cinema_focus" else 0.40)
    y_min = int(min(0.068 * src_h, max(0, src_h - ch)))
    y = int(min(max(cy * src_h - y_bias * ch, y_min), max(0, src_h - ch)))

    scale = f"scale=w='trunc(1080*{zexpr}/2)*2':h=-2:eval=frame"
    extra_fx = ",eq=contrast=1.06:saturation=1.08" if framing == "cinema_focus" else ""
    return (
        f"[0:v]crop={cw}:{ch}:{x}:{y},{scale},crop=1080:1920:(iw-ow)/2:(ih-oh)/2{extra_fx},"
        "fps=30,format=yuv420p,setsar=1[v]"
    )


def render_shot(
    src: str, shot: Dict[str, Any], idx: int, src_w: int, src_h: int,
    face, cfg, accent_hex: str, tmp: Path, card_assets: Optional[Tuple[Path, Path, int]] = None
) -> str:
    dur = shot["b"] - shot["a"]
    out = str(tmp / f"shot_{idx:03d}.mp4")
    shot["idx"] = idx
    use_card = shot["framing"] == "broll_card" and card_assets is not None
    if shot["framing"] == "broll_card" and not use_card:
        shot["framing"] = "medium"
    fg = build_shot_filter(shot, src_w, src_h, face, dur, cfg, accent_hex,
                           card_pad=card_assets[2] if card_assets else 60)
    cmd = ["ffmpeg", "-y", "-ss", f"{shot['a']:.3f}", "-i", src]
    if use_card:
        cmd += ["-loop", "1", "-i", str(card_assets[0]), "-loop", "1", "-i", str(card_assets[1])]
    cmd += [
        "-t", f"{dur:.3f}",
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
    subtitle_size: str = "small",
    watermark_image: Optional[str] = None,
    watermark_pos: str = "top_right",
    progress_callback: Optional[Callable[[str, str], None]] = None,
) -> Dict[str, Any]:
    intensity = intensity if intensity in INTENSITY else "normal"
    preset = PRESETS.get(niche, PRESETS["universal"])
    cfg = INTENSITY[intensity]
    clip_id = clip_info.get("clip_id", "clip")
    rng = random.Random(f"{clip_id}-{clip_info['start_time']:.2f}")

    sub_sizes = {"compact": 46, "small": 56, "medium": 68, "large": 82}
    target_font_size = sub_sizes.get(str(subtitle_size).lower(), 56) if isinstance(subtitle_size, str) else int(subtitle_size)

    tmp = BASE_DIR / "uploads" / "temp" / f"pro_{clip_id}_{rng.randint(1000, 9999)}"
    tmp.mkdir(parents=True, exist_ok=True)

    c0, c1 = float(clip_info["start_time"]), float(clip_info["end_time"])
    src_w, src_h, _ = probe_video(source_video)
    vertical = (src_w / src_h) < 0.7

    # 1. Plan shots & assign 4-mode camera framing (Jeda kosong terbuang)
    if progress_callback:
        progress_callback("silence_cut", "Jeda kosong terbuang (Auto Jump-Cut)...")
    words = clip_info.get("words", [])
    shots = plan_shots(words, c0, c1, intensity, rng)
    assign_framing(shots, vertical, rng)

    # 2. Face tracking (Crop 9:16 ikutin wajah)
    if progress_callback:
        progress_callback("face_crop", "Crop 9:16 mengikuti wajah (YuNet AI Face-Tracking)...")
    track = track_faces(source_video, c0, c1)
    fb = face_for_range(track, c0, c1, (0.5, 0.42, 0.22))
    for s in shots:
        s["face"] = face_for_range(track, s["a"], s["b"], fb)

    # 3. Render individual shots in parallel (video-card B-Roll memakai mask rounded + bayangan)
    accent_rgb = mg.hex_rgb(preset["hex"])
    try:
        card_assets = mg.make_card_assets(tmp, accent_rgb, CARD_W, CARD_H)
    except Exception:
        card_assets = None
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = [
            ex.submit(render_shot, source_video, s, i, src_w, src_h, s["face"], cfg, preset["hex"], tmp, card_assets)
            for i, s in enumerate(shots)
        ]
        files = [f.result() for f in futs]

    listf = tmp / "list.txt"
    listf.write_text("\n".join(f"file '{Path(f).as_posix()}'" for f in files), encoding="utf-8")
    vcat = tmp / "video_cat.mp4"
    _run_ok(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf), "-c", "copy", str(vcat)])

    # 4. Timeline remap + Multi-Layer Effects + Studio Harmonic SFX (0% white-noise)
    t = 0.0
    remapped, kw_events, broll_cards, sfx_events, cut_times = [], [], [], [], []
    emoji_map = getattr(ce, "EMOJI_MAP", {}) or {}
    ai_pwords = set(w.lower().strip() for w in (clip_info.get("power_words") or []) if w)
    merged_power_words = POWER_WORDS | ai_pwords

    clean_title = re.sub(
        r"[^\w\s\-&!?]", "",
        ce.apply_phonetic_corrections(clip_info.get("hook_title", "")).replace(":", " -")
    ).strip()
    niche_cfg = ce.NICHE_CONFIGS.get(niche, ce.NICHE_CONFIGS["universal"])
    header = custom_watermark.strip() if custom_watermark and custom_watermark.strip() else niche_cfg["header_tag"]

    hook_end = min(3.1, shots[0]["b"] - shots[0]["a"] - 0.1) if shots else 2.8
    hook_dur = max(1.9, hook_end)

    # SFX Hook Pembuka (Deep Sub-Bass Boom + Warm Glass Chime)
    if clean_title:
        sfx_events.append(dict(id="VL0516", t=0.05, gain=0.42, role="hook_boom"))
        sfx_events.append(dict(id="VL0566", t=0.20, gain=0.24, role="hook_chime"))

    velvet_ids = ["VL0501", "VL0502", "VL0503", "VL0504"]
    pop_ids = ["VL0526", "VL0531"]

    for i, s in enumerate(shots):
        s["t0"] = t
        d = s["b"] - s["a"]
        for w in s["words"]:
            ws_ = t + max(0.0, w["start"] - s["a"])
            we_ = t + max(0.0, w["end"] - s["a"])
            remapped.append({
                "word": ce.apply_phonetic_corrections(w["word"]), "start": ws_, "end": max(we_, ws_ + 0.1),
                "probability": w.get("probability", 1.0)
            })

        if i > 0:
            cut_t = round(t, 3)
            cut_times.append(cut_t)
            # Velvet Sub-Bass Transition SFX di setiap pergantian kamera
            vid = velvet_ids[(i - 1) % len(velvet_ids)]
            sfx_events.append(dict(id=vid, t=max(0.0, cut_t - 0.08), gain=0.32, role="camera_transition"))

        # Pilih efek visual & audio untuk setiap shot setelah hook pembuka
        if i >= 1 and d >= 2.1:
            if s.get("framing") == "cinema_focus":
                phrase = summarize_shot_phrase(s["words"])
                bt0 = round(t + 0.12, 3)
                bt1 = round(t + min(d - 0.15, 3.4), 3)
                if bt1 - bt0 >= 1.4:
                    s["broll_phrase"] = phrase
                    broll_cards.append(dict(t0=bt0, t1=bt1, badge=preset["badge"], phrase=phrase))
                    sfx_events.append(dict(id="VL0511", t=max(0.0, bt0 - 0.32), gain=0.22, role="insight_riser"))
                    sfx_events.append(dict(id="VL0566", t=bt0 + 0.05, gain=0.30, role="insight_chime"))
            else:
                kw = pick_keyword(s["words"])
                if kw:
                    kt = t + max(0.15, kw["start"] - s["a"] - 0.04)
                    if kt > hook_dur + 0.25:
                        kdur = min(1.85, max(1.15, (t + d) - kt - 0.12))
                        if kdur >= 0.9:
                            kw_clean = re.sub(r"[^\w\-]", "", kw["word"]).upper()
                            s["keyword"] = kw_clean
                            em_raw = emoji_map.get(kw_clean.lower(), "🔥")
                            em = mg.first_emoji(em_raw) or "🔥"
                            kw_events.append(dict(text=kw_clean, t=round(kt, 3), d=round(kdur, 3), emoji=em))
                            pid = pop_ids[len(kw_events) % len(pop_ids)]
                            sfx_events.append(dict(id=pid, t=max(0.0, round(kt, 3)), gain=0.28, role="keyword_pop"))

        t += d
    total = _snap(t)

    # Kumpulkan zona waktu saat kartu lower-middle aktif agar emoji caption otomatis menyesuaikan posisi
    card_zones: List[Tuple[float, float]] = []
    if clean_title:
        card_zones.append((0.0, hook_dur + 0.25))
    for bc in broll_cards:
        card_zones.append((bc["t0"] - 0.1, bc["t1"] + 0.15))
    for kev in kw_events:
        card_zones.append((kev["t"] - 0.1, kev["t"] + kev["d"] + 0.15))

    # 4b. Motion graphics timeline (Subtitle per kata + Multi-Layer Agency Look)
    if progress_callback:
        progress_callback("subtitles", "Subtitle per kata (Pop-Bounce Hormozi)...")
    elements: List[Any] = [
        mg.TopGradient(total, height=240, max_alpha=185),
        mg.BottomGradient(total, height=820, max_alpha=225),
        mg.CinemaParticles(total, accent_rgb, count=12),
        mg.TopHeaderPill(header, total, accent_rgb, y=96),
        mg.CaptionTrack(remapped, accent_rgb, power_words=merged_power_words,
                        emoji_map=emoji_map, font_size=target_font_size, y_center=1520, alt_zones=[], card_zones=card_zones),
    ]

    # Logo brand watermark (default: dn-zy / Dede Nuriman Az-Zailiy KREATIF)
    effective_logo = watermark_image
    if not effective_logo or not str(effective_logo).strip():
        default_brand = BASE_DIR / "static" / "branding" / "dnzy_watermark.png"
        if default_brand.exists():
            effective_logo = str(default_brand)

    if effective_logo and str(effective_logo).lower() != "none" and watermark_pos != "none":
        elements.append(mg.LogoWatermark(
            image_path=str(effective_logo),
            total=total,
            pos=watermark_pos,
            width=185,
            opacity=0.92
        ))
    if clean_title:
        elements.append(mg.HookTitle(clean_title, header, accent_rgb, t0=0.0, t1=hook_dur, y=1090))
    for bc in broll_cards:
        elements.append(mg.BrollPanel(bc["badge"], bc["phrase"], bc["t0"], bc["t1"], accent_rgb, y_top=1120))
    for kev in kw_events:
        elements.append(mg.KeywordSticker(kev["text"], kev["t"], kev["d"], accent_rgb, emoji=kev.get("emoji", "🔥"), y=1245))
    if cut_times:
        elements.append(mg.CutSweep(cut_times, accent=accent_rgb, strength=0.34))
    elements.append(mg.ProgressBar(total, accent_rgb))
    timeline = mg.Timeline(total, elements)

    speech = tmp / "speech.wav"
    build_speech(source_video, shots, speech)
    sfx_wav = tmp / "sfx.wav"
    build_sfx_bed(sfx_events, total, sfx_wav)

    # 5. Final Composite: Argon 3D LUT + Vignette + Light-Leak Overlay + Motion Graphics RGBA + Voice & Studio SFX Mix
    if progress_callback:
        progress_callback("loudnorm", "Suara rata · -14 LUFS (Mastering Broadcast)...")
    rel = lambda p: Path(p).resolve().relative_to(BASE_DIR).as_posix()
    lut = ARGON / "luts" / f"{preset['lut']}.cube"
    ovf = ARGON / "overlays" / f"{preset['overlay']}.mp4"

    chain = [
        "[0:v]split[o][l]",
        f"[l]lut3d=file='{rel(lut)}'[lg]",
        f"[o][lg]blend=all_mode=normal:all_opacity={preset['lut_s']}[gr]",
        "[gr]vignette=PI/6[vg]",
    ]
    last = "vg"
    cmd = ["ffmpeg", "-y", "-i", str(vcat), "-i", str(speech), "-i", str(sfx_wav)]
    idx = 3
    if ovf.exists():
        cmd += ["-stream_loop", "-1", "-i", str(ovf)]
        chain.append(f"[{idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p[ov]")
        chain.append(f"[{last}][ov]blend=all_mode=screen:all_opacity={preset['ov_s'] * 0.55:.3f}:shortest=1[fx]")
        last = "fx"
        idx += 1
    cmd += ["-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{mg.W}x{mg.H}", "-framerate", str(FPS), "-i", "pipe:0"]
    chain.append(f"[{idx}:v]format=rgba[mg]")
    chain.append(f"[{last}][mg]overlay=0:0:format=auto:eof_action=pass,format=yuv420p[outv]")

    achain = (
        "[1:a]highpass=f=70,afftdn=nr=8:nf=-32,"
        "acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,"
        "loudnorm=I=-14:TP=-1.5:LRA=11[voc];"
        "[2:a]volume=0.88[sfx];"
        "[voc][sfx]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[outa]"
    )
    cmd += [
        "-filter_complex", ";".join(chain) + ";" + achain,
        "-map", "[outv]", "-map", "[outa]",
        "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        output_mp4,
    ]
    _encode_with_overlay(cmd, timeline, tmp / "ffmpeg_final.log")

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

    try:
        import thumbnail_engine
        thumb_path = str(Path(output_mp4).with_name(f"{Path(output_mp4).stem}_thumb.jpg"))
        clean_jpg = str(Path(output_mp4).with_name(f"{Path(output_mp4).stem}_clean.jpg"))
        # Ambil frame terbaik dari vcat (video 9:16 bersih sebelum ditempel subtitle)
        clean_im = thumbnail_engine.pick_best_frame(str(vcat))
        clean_im.save(clean_jpg, "JPEG", quality=92)
        thumb_hl = clip_info.get("thumbnail_text") or clean_title or "WAJIB SIMAK!"
        thumbnail_engine.generate_thumbnail(
            video_path=str(vcat),
            output_jpg=thumb_path,
            headline=thumb_hl,
            sub_badge=header,
            niche=niche,
            clean_frame_jpg=clean_jpg,
        )
        edl["thumbnail"] = Path(thumb_path).name
    except Exception as te:
        print(f"[Thumbnail Warning] {te}")

    shutil.rmtree(tmp, ignore_errors=True)
    return edl
